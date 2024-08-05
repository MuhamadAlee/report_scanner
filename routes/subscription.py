import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.auth import get_current_user
from schemas.subscription import SubscriptionBase
from typing import List
from controllers.subscription import *

from config.database import engine, Base, get_db, SessionLocal

Base.metadata.create_all(bind=engine)
subscription = APIRouter(tags=['subscriptions'])


@subscription.get("/get_current_user_subscription", dependencies=[Depends(get_current_user)])
async def get_current_user_subscription(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_current_user_monthly_subscription(db=db, user_id=current_user.id)

@subscription.get("/get_all_user_subscription", dependencies=[Depends(get_current_user)])
async def get_all_user_subscription(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    return get_all_user_monthly_subscription(db=db)

@subscription.put("/update_subscription", dependencies=[Depends(get_current_user)])
async def update_subscription(subscription_id: int, subscription:SubscriptionBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    return update_specific_subscription(db=db, id=subscription_id, subscription = subscription)

@subscription.put("/send_report_notification", dependencies=[Depends(get_current_user)])
async def send_rport(report_code: int, email: str, url: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized for this endpoint')
    return send_report_url_to_user(db=db,  email=email, report_code= report_code, url=url)