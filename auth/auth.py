import bcrypt
import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = data.copy()
    expire_time = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

def get_current_user(token: str) -> str:
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]
