# munazzam/app/core/database.py

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import sys

# --- Database Configuration ---
# Format: "postgresql://<user>:<password>@<host>:<port>/<dbname>"
DATABASE_URL = "postgresql://postgres:0@localhost:5432/munazzam_db"

#h1tCgNKLMpR4yfsq
DATABASE_URL = "postgresql://postgres:[h1tCgNKLMpR4yfsq]@db.srxjqmxqblntqufhzjsp.supabase.co:5432/postgres"

DATABASE_URL = "postgresql://postgres.srxjqmxqblntqufhzjsp:h1tCgNKLMpR4yfsq@aws-1-eu-central-1.pooler.supabase.com:5432/postgres"

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


def main():
    """
    A simple function to test the database connection.
    """
    print("Attempting to connect to the database...")
    
    try:
        # Create an engine to connect to the database
        engine = create_engine(DATABASE_URL)

        # Use a `with` block to ensure the connection is closed
        with engine.connect() as connection:
            # Execute a simple query to verify the connection
            connection.execute(text("SELECT 1"))
        
        print("✅ Connection successful!")

    except SQLAlchemyError as e:
        print(" Connection failed.")
        print("\nError Details:")
        print(f"  - Type: {type(e).__name__}")
        print(f"  - Message: Check your password, host, or network connection.")
        
if __name__ == "__main__":
    main()