# munazzam/seed_database.py

import pandas as pd
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.models import (
    Base, Car, Department, CarClass, Manufacturer, Model, FunctionalLocation,
    LocationDescription, NotificationRecipient, ContractType, Management, Activity,
    OwnershipStatus, RoomType
)

# --- CONFIGURATION ---
CSV_FILE_PATH = "سيارات المدينة.xlsx - Sheet1.csv"

def get_or_create(session, model, **kwargs):
    """
    Checks if an object exists in the database. If not, it creates it.
    Returns the object instance.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def generate_random_dates():
    """Generates a set of logical, diverse dates for a vehicle."""
    reg_start = date.today() - timedelta(days=random.randint(30, 3 * 365))
    reg_end = reg_start + timedelta(days=random.randint(1, 2) * 365 - 1)
    
    insp_start = reg_start + timedelta(days=random.randint(0, 30))
    insp_end = insp_start + timedelta(days=365 - 1)
    
    return {
        "registration_start_date": reg_start,
        "registration_end_date": reg_end,
        "inspection_start_date": insp_start,
        "inspection_end_date": insp_end,
    }

def seed_data():
    """
    Main function to read the CSV and populate the database.
    """
    db: Session = SessionLocal()
    
    print(f"Reading data from '{CSV_FILE_PATH}'...")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # Clean up column names by removing extra spaces
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"ERROR: The file '{CSV_FILE_PATH}' was not found.")
        print("Please make sure it's in the same directory as this script.")
        return

    print("Starting database seeding process...")
    
    # Pre-fetch existing data to reduce queries inside the loop
    existing_cars = {c.fleet_no for c in db.query(Car.fleet_no).all()}

    for index, row in df.iterrows():
        try:
            fleet_no = str(row['Fleet No']).strip()
            if fleet_no in existing_cars:
                print(f"Skipping existing car with Fleet No: {fleet_no}")
                continue

            # --- 1. Get or Create all Lookup Table Entries ---
            # This ensures all foreign key relationships can be satisfied.
            department = get_or_create(db, Department, name=str(row['Department']).strip())
            car_class = get_or_create(db, CarClass, name=str(row['Class']).strip())
            manufacturer = get_or_create(db, Manufacturer, name=str(row['Manufacturer']).strip())
            model = get_or_create(db, Model, name=str(row['Model No']).strip())
            func_location = get_or_create(db, FunctionalLocation, name=str(row['Functional Location']).strip())
            loc_description = get_or_create(db, LocationDescription, name=str(row['Location Description']).strip())
            recipient = get_or_create(db, NotificationRecipient, name=str(row['مستلم الاشعار']).strip())
            contract = get_or_create(db, ContractType, name=str(row['العقد']).strip())
            management = get_or_create(db, Management, name=str(row['الإدارة']).strip())
            activity = get_or_create(db, Activity, name=str(row['النشاط']).strip())

            # --- 2. Map Enum Values ---
            ownership = OwnershipStatus.LEASED if 'Leased' in str(row['Owned/Leased']) else OwnershipStatus.OWNED
            
            room_str = str(row['Room']).strip()
            if "NON-REGU" in room_str:
                room_type = RoomType.NON_REGULAR
            elif "EMP-24HRS" in room_str:
                room_type = RoomType.EMP_24HRS
            else: # Default to REGULAR
                room_type = RoomType.REGULAR
            
            # --- 3. Generate Diverse Dates ---
            random_dates = generate_random_dates()

            # --- 4. Create the Car Object ---
            new_car = Car(
                fleet_no=fleet_no,
                plate_no_en=str(row['Plate No(EN)']).strip(),
                plate_no_ar=str(row['Plate No(AR)']).strip(),
                address_details_1=str(row['Address Details 1']).strip(),
                ownership=ownership,
                room_type=room_type,
                department_id=department.id,
                car_class_id=car_class.id,
                manufacturer_id=manufacturer.id,
                model_id=model.id,
                functional_location_id=func_location.id,
                location_description_id=loc_description.id,
                notification_recipient_id=recipient.id,
                contract_type_id=contract.id,
                management_id=management.id,
                activity_id=activity.id,
                **random_dates
            )
            db.add(new_car)
            
            # Commit periodically to manage memory
            if index % 50 == 0:
                db.commit()
                print(f"Processed {index + 1} of {len(df)} rows...")

        except Exception as e:
            print(f"Error processing row {index + 1}: {row.to_dict()}")
            print(f"--> Exception: {e}")
            db.rollback()
            # Decide if you want to stop on first error or continue
            # return # Uncomment to stop on first error

    # Final commit for any remaining records
    db.commit()
    db.close()
    print("\nDatabase seeding completed successfully! ✅")

if __name__ == "__main__":
    # This will drop and re-create all tables.
    # USE WITH CAUTION IN A PRODUCTION ENVIRONMENT.
    print("WARNING: This script will delete all existing data in your tables.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() == 'y':
        print("Re-creating database schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        seed_data()
    else:
        print("Seeding cancelled.")