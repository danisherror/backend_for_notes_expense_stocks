from fastapi import APIRouter, HTTPException, Depends, status
from database.database import user_collection
from auth.auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
)
from models.model import User, UserOut
from pymongo.errors import DuplicateKeyError

class UserAuthRouter:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        self.router.add_api_route("/signup", self.signup, methods=["POST"], response_model=dict)
        self.router.add_api_route("/signin", self.signin, methods=["POST"], response_model=dict)
        self.router.add_api_route("/profile", self.get_profile, methods=["GET"], response_model=UserOut)

    async def signup(self, user: User):
        hashed_password = hash_password(user.password)
        user_data = {"email": user.email, "password": hashed_password}

        if user_collection.find_one({"email": user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
            )

        try:
            user_collection.insert_one(user_data)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
            )

        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}

    async def signin(self, form_data: User):
        user = user_collection.find_one({"email": form_data.email})
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        token = create_access_token({"sub": user["email"]})
        return {"access_token": token, "token_type": "bearer"}

    async def get_profile(self, token: str = Depends(get_current_user)):
        user = user_collection.find_one({"email": token})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        
        return UserOut(email=user["email"], id=str(user["_id"]))

# Instantiate and register the UserAuthRouter
user_auth_router_instance = UserAuthRouter()
router = user_auth_router_instance.router
