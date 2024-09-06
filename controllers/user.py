from utils.util import hash_password
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserBase
from fastapi import HTTPException
from utils.mail import user_creation_notification


def get_user(db: Session, user_id: int):
    try:
        return db.query(User).filter(User.id == user_id).first()
    except:
        raise HTTPException(status_code=404, detail="User not found")

def get_user_by_email(db: Session, email: str):
    try:
        return db.query(User).filter(User.email == email).first()
    except:
        raise HTTPException(status_code=404, detail="User not found")

def get_users(db: Session, skip: int = 0, limit: int = 10):
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except:
        raise HTTPException(status_code=404, detail="Users not found")

def create_user(db: Session, user: UserBase):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.hashed_password),  # In real scenarios, hash the password
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        try:
            user_creation_notification(user.username, user.email, user.hashed_password)
        except Exception as e:
            print(f"unable to send the notification: {e}")
        return db_user
    except:
        raise HTTPException(status_code=422, detail="Unable to create user")

def update_user(db: Session, user_id: int, user: UserBase):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = hash_password(user.hashed_password)
        db_user.is_active = user.is_active
        db_user.is_superuser = user.is_superuser

        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        raise HTTPException(status_code=422, detail="Unable to update user")

def delete_user(db: Session, user_id: int):
    try:

        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except:
        raise HTTPException(status_code=422, detail="Unable to delete user")


