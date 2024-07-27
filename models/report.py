from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.database import Base


class Report(Base):
    __tablename__ = "report"
    
    id = Column(Integer, primary_key=True, index=True)
    response = Column(String)
    terms = Column(JSON)
    images_path = Column(JSON)
    user_id = Column(Integer, ForeignKey('user.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")