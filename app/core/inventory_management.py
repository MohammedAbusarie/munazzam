# munazzam/app/core/inventory_management.py

from sqlalchemy.orm import joinedload, Session
from .database import SessionLocal
from .models import (
    Car, Department, CarClass, Manufacturer, Model, FunctionalLocation,
    LocationDescription, NotificationRecipient, ContractType, Management,
    Activity, CloudinaryImage
)
from . import cloudinary_service # Import the new service

def get_all_cars_with_details():
    """
    Fetches all cars and eagerly loads all related data, including the image.
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
            joinedload(Car.activity),
            joinedload(Car.image) # Eagerly load the image relationship
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
    Adds a new car, uploads its image to Cloudinary, and saves the records
    in a single database transaction.
    """
    session = SessionLocal()
    try:
        image_path = car_data.pop('image_path', None)
        if not image_path:
            return {"success": False, "message": "Image path is required."}

        upload_result = cloudinary_service.upload_image(image_path)
        if not upload_result["success"]:
            raise Exception(f"Image upload failed: {upload_result['error']}")

        # Create the database record for the uploaded image
        cloudinary_data = upload_result["data"]
        new_image = CloudinaryImage(
            public_id=cloudinary_data['public_id'],
            url=cloudinary_data['secure_url']
        )
        session.add(new_image)

        # Create and link the new car
        new_car = Car(**car_data)
        new_car.image = new_image  # Associate the image with the car
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
    Updates a car's details. If a new image is provided, it replaces the
    old one on Cloudinary and in the database.
    """
    session = SessionLocal()
    try:
        car_to_update = session.query(Car).options(joinedload(Car.image)).filter(Car.id == car_id).one()

        new_image_path = car_data.pop('image_path', None)
        if new_image_path:
            # Delete the old image from Cloudinary if it exists
            if car_to_update.image:
                cloudinary_service.delete_image(car_to_update.image.public_id)
                session.delete(car_to_update.image) # Delete old image record

            # Upload the new image
            upload_result = cloudinary_service.upload_image(new_image_path)
            if not upload_result["success"]:
                raise Exception(f"New image upload failed: {upload_result['error']}")

            # Create and link the new image record
            cloudinary_data = upload_result["data"]
            new_image = CloudinaryImage(
                public_id=cloudinary_data['public_id'],
                url=cloudinary_data['secure_url']
            )
            session.add(new_image)
            car_to_update.image = new_image

        # Update other car attributes
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
    Deletes a car and its associated image from both the database
    and Cloudinary.
    """
    session = SessionLocal()
    try:
        car_to_delete = session.query(Car).options(joinedload(Car.image)).filter(Car.id == car_id).one()
        
        # If an image is associated, delete it from Cloudinary and the DB
        if car_to_delete.image:
            image_public_id = car_to_delete.image.public_id
            session.delete(car_to_delete.image)
            cloudinary_service.delete_image(image_public_id)

        session.delete(car_to_delete)
        session.commit()
        return {"success": True, "message": "Car deleted successfully."}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error: {e}"}
    finally:
        session.close()