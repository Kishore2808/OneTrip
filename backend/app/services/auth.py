#####FIRST VERSION OF THE FILE (auth.py) BELOW#####


# from passlib.context import CryptContext
# from jose import jwt
# import os

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(password: str, hashed: str):
#     return pwd_context.verify(password, hashed)

# def create_jwt(data: dict):
#     return jwt.encode(
#         data,
#         os.getenv("JWT_SECRET"),
#         algorithm=os.getenv("JWT_ALGORITHM")
#     )


########SECOND VERSION OF THE FILE (auth.py) BELOW#####

import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str):
#     return pwd_context.verify(plain_password, hashed_password)

# Use Argon2 (modern + strong + no 72-byte limit)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Create a JWT token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    """Decode a JWT token and return the payload"""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
