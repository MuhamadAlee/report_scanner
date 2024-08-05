import os
import shutil
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from utils.report_generator import ReportGenerator
from utils.reports_content_extractor import Extractor
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.user import user
from routes.auth import auth
from routes.report import report
from routes.subscription import subscription

load_dotenv()
app = FastAPI()


# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth)
app.include_router(user)
app.include_router(report)
app.include_router(subscription)
app.mount("/images", StaticFiles(directory=(os.path.join(str(Path(__file__).resolve().parent), "images"))), name="images")

if __name__ == "__main__":
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    uvicorn.run(app=app, host=host, port=port)
