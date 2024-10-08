from fastapi import APIRouter, HTTPException, Depends, status
from database.database import user_collection
from auth.auth import get_current_user
from models.model import User, UserOut
from pymongo.errors import DuplicateKeyError
from auth.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_jwt_token,
    get_current_user
)

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
async def signin(form_data: User):
    user = user_collection.find_one({"email": form_data.email})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=UserOut)
async def get_profile(token: str = Depends(get_current_user)):
    user = user_collection.find_one({"email": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserOut(email=user["email"], id=str(user["_id"]))
