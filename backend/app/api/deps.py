# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth import decode_token
from app.db import SessionLocal
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email, get_user_by_id  # you may need get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    # implement get_user_by_id in crud.user if not present
    user = db.query.__class__  # placeholder — replace with your get_user_by_id usage
    # better: use a small helper crud function:
    from app.crud.user import get_user_by_id
    user = get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
