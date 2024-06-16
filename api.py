import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from utils.report_generator import ReportGenerator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
rep_gen = ReportGenerator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    text: str

# Define endpoint
@app.post("/report_scanner")
async def report_scanner(report: ReportRequest):
    response = rep_gen.get_llm_response(report.text)
    response['response'] = response['response'].replace(".  ", ". \n ") 
    return response


if __name__ == "__main__":
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    uvicorn.run(app, host = host,  port=port)
