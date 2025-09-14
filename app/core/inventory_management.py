# munazzam/app/core/inventory_management.py

from .database import SessionLocal
from .models import (
    Car, Department, CarClass, Manufacturer, Model, FunctionalLocation,
    LocationDescription, NotificationRecipient, ContractType, Management, Activity
)
from sqlalchemy.orm import joinedload

def get_all_cars_with_details():
    """
    Fetches all cars and eagerly loads all related data in a single query
    for efficient display in the main table.
    """
    session = SessionLocal()
    try:
        cars = session.query(Car).options(
            joinedload(Car.department),
            joinedload(Car.car_class),
            joinedload(Car.manufacturer),
            joinedload(Car.model),
            joinedload(Car.functional_location),
            joinedload(Car.location_description),
            joinedload(Car.notification_recipient),
            joinedload(Car.contract_type),
            joinedload(Car.management),
            joinedload(Car.activity)
        ).all()
        return cars
    finally:
        session.close()

def get_lookup_data():
    """Fetches all data needed for the form's dropdowns (QComboBox)."""
    session = SessionLocal()
    try:
        data = {
            "departments": session.query(Department).order_by(Department.name).all(),
            "car_classes": session.query(CarClass).order_by(CarClass.name).all(),
            "manufacturers": session.query(Manufacturer).order_by(Manufacturer.name).all(),
            "models": session.query(Model).order_by(Model.name).all(),
            "functional_locations": session.query(FunctionalLocation).order_by(FunctionalLocation.name).all(),
            "location_descriptions": session.query(LocationDescription).order_by(LocationDescription.name).all(),
            "notification_recipients": session.query(NotificationRecipient).order_by(NotificationRecipient.name).all(),
            "contract_types": session.query(ContractType).order_by(ContractType.name).all(),
            "managements": session.query(Management).order_by(Management.name).all(),
            "activities": session.query(Activity).order_by(Activity.name).all(),
        }
        return data
    finally:
        session.close()

def add_car(car_data):
    """Adds a new car to the database."""
    session = SessionLocal()
    try:
        # For now, we ignore the image path. Later, this is where you would
        # upload the file at car_data['image_path'] to Cloudinary and get a URL.
        car_data.pop('image_path', None)
        
        new_car = Car(**car_data)
        session.add(new_car)
        session.commit()
        return {"success": True, "message": "Car added successfully."}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error: {e}"}
    finally:
        session.close()

def update_car(car_id, car_data):
    """Updates an existing car."""
    session = SessionLocal()
    try:
        car_data.pop('image_path', None)

        car_to_update = session.query(Car).filter(Car.id == car_id).one()
        for key, value in car_data.items():
            setattr(car_to_update, key, value)
        session.commit()
        return {"success": True, "message": "Car updated successfully."}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error: {e}"}
    finally:
        session.close()

def delete_car(car_id):
    """Deletes a car from the database."""
    session = SessionLocal()
    try:
        car_to_delete = session.query(Car).filter(Car.id == car_id).one()
        session.delete(car_to_delete)
        session.commit()
        return {"success": True, "message": "Car deleted successfully."}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error: {e}"}
    finally:
        session.close()