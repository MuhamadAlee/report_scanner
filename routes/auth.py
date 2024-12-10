from utils.util import hash_password
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth import Token
from config.database import get_db
from models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from controllers.auth import create_access_token, revoke_token, get_current_user, get_current_token


from pydantic import BaseModel
from typing import Union



auth = APIRouter(tags=['authentication'])


# Model for handling JSON input
class LoginRequest(BaseModel):
    username: str
    password: str

# Endpoint that supports both form data and JSON
@auth.post("/login/", response_model=Token)
def login(
    userdetails: Union[OAuth2PasswordRequestForm, LoginRequest] = Depends(),
    db: Session = Depends(get_db)
):
    # Check if the input was JSON (LoginRequest) or form data (OAuth2PasswordRequestForm)
    if isinstance(userdetails, LoginRequest):
        username = userdetails.username
        password = userdetails.password
    else:  # It's form data
        username = userdetails.username
        password = userdetails.password

    user = db.query(User).filter(User.email == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User does not exist')
    
    if user.hashed_password != hash_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong Password')
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Disabled User')
    
    return create_access_token(data=user)


@auth.post("/logout", dependencies=[Depends(get_current_user), Depends(get_current_token)])
async def report_scanner(token: str = Depends(get_current_token)):
    return revoke_token(token)

