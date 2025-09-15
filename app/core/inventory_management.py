# munazzam/app/core/inventory_management.py

from .database import SessionLocal
from .models import (
    Car, Department, CarClass, Manufacturer, Model, FunctionalLocation,
    LocationDescription, NotificationRecipient, ContractType, Management, Activity
)
from sqlalchemy.orm import joinedload
from . import supabase_service # Import the new service

def get_all_cars_with_details():
    """
    Fetches all cars. The image URL is now a direct attribute of the car.
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
    """
    Adds a new car and uploads its image to Supabase Storage.
    """
    session = SessionLocal()
    try:
        image_path = car_data.pop('image_path', None)
        if image_path:
            upload_result = supabase_service.upload_image(image_path)
            if not upload_result["success"]:
                raise Exception(f"Image upload failed: {upload_result['error']}")
            car_data['image_url'] = upload_result['url']
        
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
    """
    Updates a car. If a new image is provided, it replaces the old one
    in Supabase Storage.
    """
    session = SessionLocal()
    try:
        car_to_update = session.query(Car).filter(Car.id == car_id).one()
        
        new_image_path = car_data.pop('image_path', None)
        if new_image_path:
            # If an old image exists, delete it from storage
            if car_to_update.image_url:
                old_path = supabase_service.get_path_from_url(car_to_update.image_url)
                if old_path:
                    supabase_service.delete_image(old_path)

            # Upload the new image
            upload_result = supabase_service.upload_image(new_image_path)
            if not upload_result["success"]:
                raise Exception(f"New image upload failed: {upload_result['error']}")
            
            # Update the URL on the car object directly
            car_to_update.image_url = upload_result['url']

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
    """
    Deletes a car from the database and its associated image from
    Supabase Storage.
    """
    session = SessionLocal()
    try:
        car_to_delete = session.query(Car).filter(Car.id == car_id).one()
        
        # If an image URL exists, delete the file from storage
        if car_to_delete.image_url:
            path = supabase_service.get_path_from_url(car_to_delete.image_url)
            if path:
                supabase_service.delete_image(path)
            
        session.delete(car_to_delete)
        session.commit()
        return {"success": True, "message": "Car deleted successfully."}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error: {e}"}
    finally:
        session.close()