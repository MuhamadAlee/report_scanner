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

from routes.user import user
from routes.auth import auth
from routes.report import report
from routes.subscription import subscription

load_dotenv()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)
app.include_router(user)
app.include_router(report)
app.include_router(subscription)


# if __name__ == "__main__":
#     host = os.getenv('HOST')
#     port = int(os.getenv('PORT'))
#     uvicorn.run(app=app, host=host, port=port)
