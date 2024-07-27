import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from utils.mail import send_email
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from config.database import engine, Base, get_db, SessionLocal
from sqlalchemy import func
from models.subscription import Subscription
from models.user import User
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import pytz

def generation_subscription_mails():
    
    db = SessionLocal()
    subquery = (
    db.query(
        Subscription.user_id,
        func.max(Subscription.month).label('latest_month')
    )
    .group_by(Subscription.user_id)
    .subquery()
)

    # Join the subquery with the Subscription and User tables to get the details
    query = (
        db.query(
            Subscription,
            User.email
        )
        .join(subquery, (Subscription.user_id == subquery.c.user_id) & (Subscription.month == subquery.c.latest_month))
        .join(User, Subscription.user_id == User.id)
        .filter(User.is_superuser == False)
    )

    # Execute the query
    results = query.all()
    for subscription, email in results:
        date = f"{(subscription.month.date().year)}-{(subscription.month.date().month)}"
        send_email(email, date, subscription.no_of_requests, subscription.charges)

    db.close()

if __name__=="__main__":
    
    print("---------- Scheduler started ----------")
    scheduler = BlockingScheduler(timezone=pytz.timezone('Europe/London'))
    # Schedule the job to run every month on the 1st at 12 AM UTC
    scheduler.add_job(generation_subscription_mails, 'cron', day=1, hour=0, minute=0)
    scheduler.start()