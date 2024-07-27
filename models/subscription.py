from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.database import Base


class Subscription(Base):
    __tablename__ = "subscription"
    
    id = Column(Integer, primary_key=True, index=True)
    no_of_requests = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    month = Column(DateTime, default=datetime.utcnow)
    is_paid = Column(Boolean, default=False)
    charges = Column(Integer)
    
    user = relationship("User")