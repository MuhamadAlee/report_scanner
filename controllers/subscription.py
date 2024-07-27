import os
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserBase
from fastapi import HTTPException
from datetime import datetime
from models.subscription import Subscription
from config.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

def get_current_user_monthly_subscription(db:Session, user_id:int):
    try:
        data_records = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        if not data_records:
            raise HTTPException(status_code=404, detail="No data found for the specified user")
        return data_records
    except:
        raise HTTPException(status_code=404, detail="No data found for the specified user")
    
def get_all_user_monthly_subscription(db:Session):
    try:
        data_records = db.query(Subscription).all()
        if not data_records:
            raise HTTPException(status_code=404, detail="No data found for the specified user")
        return data_records
    except:
        raise HTTPException(status_code=404, detail="No data found for the specified user")

def update_specific_subscription(db:Session, id:int, subscription:Subscription):
    try:
        db_subscription = db.query(Subscription).filter(Subscription.id == id).first()
        if not db_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        db_subscription.user_id = subscription.user_id
        db_subscription.is_paid = subscription.is_paid
        db_subscription.month = subscription.month
        db_subscription.no_of_requests = subscription.no_of_requests
        

        db.commit()
        db.refresh(db_subscription)
        return db_subscription
    except:
        raise HTTPException(status_code=404, detail="Unable to update subscription")

def update_or_create_subscription(user_id: int):


    try:
        db = SessionLocal()
        # Get the first day of the current month
        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)
        
        # Query the subscription for the current month and user
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.month >= first_day_of_month,
            Subscription.month < first_day_of_month.replace(month=first_day_of_month.month % 12 + 1)
        ).first()
        
        if subscription:
            # Update the number of requests
            subscription.no_of_requests += 1
            
            subscription.charges = subscription.no_of_requests * int(os.getenv('PER_REQUEST_CHARGE'))
            subscription.month = now
            db.commit()
            db.refresh(subscription)
        else:
            # Create a new subscription entry
            subscription = Subscription(
                user_id = user_id,
                no_of_requests = 1,
                month = now, 
                charges = int(os.getenv('PER_REQUEST_CHARGE'))
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            db.close()
        
        return subscription
    except:
        raise HTTPException(status_code=404, detail="Unable to update subscription")
    
    
