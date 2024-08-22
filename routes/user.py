from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database.database import user_collection
from models.model import User, UserOut
from pymongo.errors import DuplicateKeyError
from auth.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_jwt_token,
    get_current_user
)


oath2Scheme = OAuth2PasswordBearer(tokenUrl="/api/signin")
router = APIRouter()


@router.post("/signup", response_model=dict)
async def create_user(user: User):
    hashed_password = hash_password(user.password)
    user_data = {"email": user.email, "password": hashed_password}
    userr= user_collection.find_one({"email": user.email})
    if userr:
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


@router.post("/signin", response_model=dict)
async def signin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=UserOut)
async def get_profile(token: str = Depends(oath2Scheme)):
    payload = decode_jwt_token(token)
    print(get_current_user(token))
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    print(payload)
    user = user_collection.find_one({"email": payload["sub"]})
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserOut(email=user["email"], id=str(user["_id"]))
