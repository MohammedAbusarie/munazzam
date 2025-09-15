# rebuild_db.py

import sys
# Add the app directory to the Python path to allow for imports
sys.path.append('app')

from app.core.database import Base, engine
# Import all models to ensure they are registered with Base.metadata
from app.core import models

def rebuild_database():
    """
    Drops all tables and recreates them based on the current models.
    WARNING: THIS DELETES ALL EXISTING DATA.
    """
    print("WARNING: This will delete all data in the database.")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() == 'yes':
        print("Dropping all tables...")
        # This drops tables that are defined in your models.py
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        print("Database has been rebuilt.")
    else:
        print("Database rebuild cancelled.")

if __name__ == "__main__":
    rebuild_database()