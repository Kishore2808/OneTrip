from passlib.context import CryptContext
from jose import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_jwt(data: dict):
    return jwt.encode(
        data,
        os.getenv("JWT_SECRET"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )
