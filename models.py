from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class StudentProgress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    topic = Column(String)
    score = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# 🆕 NEW TABLE
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # 🆕 Added Name Field
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)