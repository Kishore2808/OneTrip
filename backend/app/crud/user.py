from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.services.auth import hash_password

def get_user_by_email(db: Session, email: str):
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, email: str, password: str):
    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        return None

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
