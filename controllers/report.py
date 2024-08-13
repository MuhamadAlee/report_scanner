import json
from utils.util import hash_password
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.user import User
from schemas.user import UserBase
from fastapi import HTTPException
from datetime import datetime
from models.report import Report
from controllers.subscription import *
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def store_report(db: Session, data:dict):
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # adding entry for usage
        update_or_create_subscription(user_id=data['user_id'])
        
        # Create a new data record
        new_record = Report(
            response=data['response'],
            terms=data['terms'],
            images_path=data['images_path'],
            user_id=data['user_id'],
            report_code = data['report_code'],
            patient_name = data['patient_name'],
            timestamp=datetime.utcnow()
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record
    except:
        raise HTTPException(status_code=422, detail="Unable to add report")


def get_all_user_reports(db:Session, user_id:int):
    try:
        data_records = db.query(Report).filter(Report.user_id == user_id).all()
        if not data_records:
            raise HTTPException(status_code=404, detail="No data found for the specified user")
        return data_records
    except:
        raise HTTPException(status_code=404, detail="No Report find")

def get_report_data(db:Session, report_id:int):
    try:
        data_record = db.query(Report).filter(Report.id == report_id).first()
        if not data_record:
            raise HTTPException(status_code=404, detail="No Report find")
        return data_record
    except:
        raise HTTPException(status_code=404, detail="No Report find")
    
def get_report_data_for_patient(db:Session, pname:str):
    try:
        data_record = db.query(Report).filter(func.lower(Report.patient_name).ilike(f'%{pname.lower()}%')).all()
        if not data_record:
            raise HTTPException(status_code=404, detail="No Report find")
        return data_record
    except:
        raise HTTPException(status_code=404, detail="No Report find")   

def delete_report(db:Session, report_id:int):
    try:
        data_record = db.query(Report).filter(Report.id == report_id).first()
        if not data_record:
            raise HTTPException(status_code=404, detail="Data record not found")
        
        db.delete(data_record)
        db.commit()
        
        return {"message": "Data record deleted successfully"}
    except:
        raise HTTPException(status_code=422, detail="Unable to delete report")
    
def get_demo_report():
    try:
        data = None
        with open(f'{BASE_DIR}/demo_report/demo_report.json', 'r') as file:
            data = json.load(file)
        return data
    except:
        raise HTTPException(status_code=404, detail='demo report not found')