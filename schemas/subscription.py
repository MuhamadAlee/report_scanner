from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    id: int
    no_of_requests: int
    user_id: int
    month: datetime = datetime.utcnow()
    is_paid: bool = False
    charges: int

    class Config:
        orm_mode: True

    