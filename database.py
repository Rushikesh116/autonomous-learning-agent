from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CHANGE 1: Use SQLite instead of Postgres ---
# DATABASE_URL = "postgresql://postgres:password@localhost/learning_agent"
DATABASE_URL = "sqlite:///./learning_agent.db"

# --- CHANGE 2: SQLite requires this special argument ---
connect_args = {"check_same_thread": False}

# Create engine with the new args
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()