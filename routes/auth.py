from utils.util import hash_password
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth import Token
from config.database import get_db
from models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from controllers.auth import create_access_token, revoke_token, get_current_user, get_current_token
from pydantic import BaseModel
class OAuth2LoginRequest(BaseModel):
    grant_type: str = "password"  # Default to "password"
    username: str
    password: str

auth = APIRouter(tags=['authentication'])


@auth.post("/login/", response_model=Token)
def login(userdetails: OAuth2LoginRequest = Depends(), db: Session = Depends(get_db)):
    # Extract username and password from the request body
    user = db.query(User).filter(User.email == userdetails.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User does not exist')
    
    if user.hashed_password != hash_password(userdetails.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong Password')
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Disabled User')
    
    return create_access_token(data=user)


@auth.post("/logout", dependencies=[Depends(get_current_user), Depends(get_current_token)])
async def report_scanner(token: str = Depends(get_current_token)):
    return revoke_token(token)

