# munazzam/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Database Configuration ---
# Format: "postgresql://<user>:<password>@<host>:<port>/<dbname>"
DATABASE_URL = "postgresql://postgres:0@localhost:5432/munazzam_db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session():
    """
    Dependency function to get a new database session.
    Ensures the session is always closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()