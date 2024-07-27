from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class Report(BaseModel):
    response: str
    terms: Dict[str, str]
    images_path: Dict[str, str]
    user_id: int

class ReportResponse(BaseModel):
    id: int
    response: str
    terms: Dict[str, str]
    images_path: Dict[str, str]
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True