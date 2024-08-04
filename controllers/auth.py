from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import class_mapper
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from utils.util import hash_password
from models.user import User
from config.database import get_db
from collections import deque
from typing import Deque
import os
from dotenv import load_dotenv
load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

revoked_tokens: Deque[str] = deque(maxlen=50)

def model_to_dict(model):
    if model is None:
        return None
    columns = [column.key for column in class_mapper(model.__class__).columns]
    return {column: getattr(model, column) for column in columns}

def create_access_token(data: dict):
    to_encode = model_to_dict(data)
    generated_at = datetime.now(tz=timezone.utc)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    
    to_encode.update({"iat": generated_at, "exp": expires_at})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt, to_encode['id']

def verify_token_access(token: str, credentials_exception):
    try:
        token_data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={ "verify_exp": True})
        id: str = token_data.get("id")

        if (id is None) or (token in revoked_tokens):
            raise credentials_exception
        
    except jwt.ExpiredSignatureError:
        print("JWT has expired")
        raise credentials_exception
    except jwt.InvalidTokenError:
        print("Invalid JWT")
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_token_access(token, credentials_exception)    
    return db.query(User).filter(User.id == token_data['id']).first()

def get_current_token(token: str = Depends(oauth2_scheme)):
    return token

def revoke_token(token):
    if token not in revoked_tokens:
        revoked_tokens.append(token)
    return {"msg": "Successfully logged out"}
