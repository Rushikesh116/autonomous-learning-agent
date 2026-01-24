from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)  # For now, we can use a simple ID like "user_1"
    topic = Column(String, index=True)
    score = Column(Float)
    status = Column(String)  # "Mastered" or "Failed"
    timestamp = Column(DateTime, default=datetime.utcnow)