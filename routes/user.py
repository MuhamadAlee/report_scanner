import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas.user import UserBase, UserResponse
from controllers.user import *
from controllers.auth import get_current_user
from config.database import engine, Base, get_db, SessionLocal
from dotenv import load_dotenv

load_dotenv()

user = APIRouter(tags=['user'])

# Create the database tables
Base.metadata.create_all(bind=engine)

@user.on_event('startup')
async def populate_admin():
    user = {
    "username": os.getenv('ADMIN_USER_NAME'),
    "email":  os.getenv('ADMIN_EMAIL'),
    "is_active": True,
    "is_superuser": True,
    "hashed_password":  os.getenv('ADMIN_PASSWORD'),
    }

    admin_user = UserBase(**user)
    db= SessionLocal()
    db_user = get_user_by_email(db, email=admin_user.email)
    if not db_user:
        print("Super Admin setup")
        create_user(db=db, user=admin_user)

    db.close()
    
@user.post("/create_user/", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def create_new_user(user: UserBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@user.get("/get_all_users/", response_model=List[UserResponse],dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    users = get_users(db, skip=skip, limit=limit)
    return users

@user.get("/get_user_by_id/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user.get("/get_user_by_email/{user_email}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def read_user(user_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    db_user = get_user_by_email(db, email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user.put("/update_user/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def update_existing_user(user_id: int, user: UserBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    return update_user(db=db, user_id=user_id, user=user)

@user.delete("/delete_user/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def delete_existing_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    return delete_user(db=db, user_id=user_id)
