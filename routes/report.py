import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from utils.report_generator import ReportGenerator
from utils.reports_content_extractor import Extractor
from controllers.auth import get_current_user
from schemas.report import ReportResponse, Report
from typing import List
from controllers.report import *

from config.database import engine, Base, get_db, SessionLocal

# Directory to save uploaded files
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# utilities
ext = Extractor()
rep_gen = ReportGenerator()

Base.metadata.create_all(bind=engine)
report = APIRouter(tags=['report_scanner'])

@report.post("/file_report_scanner", dependencies=[Depends(get_current_user)])
async def file_report_scanner(file: UploadFile = File(...),db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"message": "Invalid file type. Only PDF files are allowed."})

    file_location = UPLOAD_DIR / file.filename

    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    content = ext.content_extraction(file_location)
    response = rep_gen.get_llm_response(content)
    data = {"response": response['report'],
            "terms": response['medical_terms'],
            "images_path": response['images'],
            "patient_name": response['patient_name'],
            "report_code": response['report_code'],
            "user_id": current_user.id}
    if isinstance(data['response'], dict):
        return store_report(db=db, data=data) 
    return data

# Define endpoint
@report.post("/report_scanner", dependencies=[Depends(get_current_user)])
async def report_scanner(text:str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = rep_gen.get_llm_response(text)

    data = {"response": response['report'],
            "terms": response['medical_terms'],
            "images_path": response['images'],
            "patient_name": response['patient_name'],
            "report_code": response['report_code'],
            "user_id": current_user.id}
    if isinstance(data['response'], dict):
        return store_report(db=db, data=data) 
    return data

@report.get("/get_reports_for_user/{user_id}", dependencies=[Depends(get_current_user)])
async def get_stored_data(user_id: int, db: Session = Depends(get_db)):
    return get_all_user_reports(db=db, user_id=user_id)

@report.get("/get_report_by_id/{report_id}", dependencies=[Depends(get_current_user)])
async def get_data_record(report_id: int, db: Session = Depends(get_db)):
    return get_report_data(db=db, report_id=report_id)

@report.get("/get_patient_report/{report_id}/{report_code}")
async def get_patient_report(report_id: int, report_code:int, db: Session = Depends(get_db)):
    report = get_report_data(db=db, report_id=report_id)
    try:
        if report.report_code == report_code:
            return report
        return {"message": "un-authorized patient"}
    except:
        return {"message": "un-authorized patient"}

@report.get("/get_report_by_patient_name/{patient_name}", dependencies=[Depends(get_current_user)])
async def get_patient_report(patient_name: str, db: Session = Depends(get_db)):
    return get_report_data_for_patient(db=db, pname=patient_name)

@report.delete("/delte_report/{report_id}", response_model=dict, dependencies=[Depends(get_current_user)])
async def delete_data_record(report_id: int, db: Session = Depends(get_db)):
    return delete_report(db=db, report_id=report_id)

@report.get("/demo_report/")
async def fetch_demo_report():
    return get_demo_report()