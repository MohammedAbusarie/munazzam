# munazzam/app/core/models.py

import enum
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base, engine

# --- Enum Definitions ---
class OwnershipStatus(enum.Enum):
    OWNED = "Owned"
    LEASED = "Leased"

class RoomType(enum.Enum):
    REGULAR = "regular"
    NON_REGULAR = "non_regular"
    EMP_24HRS = "emp-24hrs"

class EquipmentStatus(enum.Enum):
    OPERATIONAL = "عاملة"  # Operational
    NEW = "جديدة"           # New
    OUT_OF_ORDER = "معطلة" # Out of Order

# ===================================================================
# LOOKUP TABLES (For Dropdown Lists - DDL)
# ===================================================================

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="department")

class CarClass(Base):
    __tablename__ = 'car_classes'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="car_class")

class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="manufacturer")
    equipment = relationship("Equipment", back_populates="manufacturer")

class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="model")
    equipment = relationship("Equipment", back_populates="model")

class FunctionalLocation(Base):
    __tablename__ = 'functional_locations'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="functional_location")

class LocationDescription(Base):
    __tablename__ = 'location_descriptions'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    cars = relationship("Car", back_populates="location_description")

class NotificationRecipient(Base):
    __tablename__ = 'notification_recipients'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    cars = relationship("Car", back_populates="notification_recipient")

class ContractType(Base):
    __tablename__ = 'contract_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="contract_type")

class Management(Base):
    __tablename__ = 'managements'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="management")

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    cars = relationship("Car", back_populates="activity")
    
class EquipmentLocation(Base):
    __tablename__ = 'equipment_locations'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    equipment = relationship("Equipment", back_populates="location")

class Sector(Base):
    __tablename__ = 'sectors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    equipment = relationship("Equipment", back_populates="sector")


# ===================================================================
# DATA TABLES
# ===================================================================

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    fleet_no = Column(String(50), nullable=False, unique=True)
    plate_no_en = Column(String(20), nullable=False)
    plate_no_ar = Column(String(20), nullable=False)
    ownership = Column(Enum(OwnershipStatus), nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    address_details_1 = Column(Text, nullable=False)
    registration_start_date = Column(Date)
    registration_end_date = Column(Date)
    inspection_start_date = Column(Date)
    inspection_end_date = Column(Date)
    
    # --- ADDED image_url field ---
    image_url = Column(String(512), nullable=True) # URL from Supabase Storage

    # --- Foreign Keys to Lookup Tables ---
    department_id = Column(Integer, ForeignKey('departments.id'))
    car_class_id = Column(Integer, ForeignKey('car_classes.id'))
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    functional_location_id = Column(Integer, ForeignKey('functional_locations.id'))
    location_description_id = Column(Integer, ForeignKey('location_descriptions.id'))
    notification_recipient_id = Column(Integer, ForeignKey('notification_recipients.id'))
    contract_type_id = Column(Integer, ForeignKey('contract_types.id'))
    management_id = Column(Integer, ForeignKey('managements.id'))
    activity_id = Column(Integer, ForeignKey('activities.id'))

    # --- Relationships ---
    department = relationship("Department", back_populates="cars")
    car_class = relationship("CarClass", back_populates="cars")
    manufacturer = relationship("Manufacturer", back_populates="cars")
    model = relationship("Model", back_populates="cars")
    functional_location = relationship("FunctionalLocation", back_populates="cars")
    location_description = relationship("LocationDescription", back_populates="cars")
    notification_recipient = relationship("NotificationRecipient", back_populates="cars")
    contract_type = relationship("ContractType", back_populates="cars")
    management = relationship("Management", back_populates="cars")
    activity = relationship("Activity", back_populates="cars")

class CalibrationCertificate(Base):
    __tablename__ = 'calibration_certificates'
    id = Column(Integer, primary_key=True)
    image_url = Column(String(512), nullable=False)
    
    # Foreign key to link to the equipment table
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)

    # Relationship back to the Equipment model
    equipment = relationship("Equipment", back_populates="certificates")


class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    door_number = Column(String(50), nullable=False, unique=True)
    year_of_manufacture = Column(Integer, nullable=True) # e.g., 2023
    plate_number = Column(String(50), nullable=False)
    status = Column(Enum(EquipmentStatus), nullable=False)

    # --- Foreign Keys ---
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    location_id = Column(Integer, ForeignKey('equipment_locations.id'))
    sector_id = Column(Integer, ForeignKey('sectors.id'))

    # --- Relationships ---
    manufacturer = relationship("Manufacturer", back_populates="equipment")
    model = relationship("Model", back_populates="equipment")
    location = relationship("EquipmentLocation", back_populates="equipment")
    sector = relationship("Sector", back_populates="equipment")

    # This creates the one-to-many link to the certificates
    certificates = relationship(
        "CalibrationCertificate", 
        back_populates="equipment",
        cascade="all, delete-orphan"
    )


# ===================================================================
# CREATE DATABASE TABLES
# ===================================================================

def create_all_tables():
    """
    Creates all tables in the database engine.
    This should be run once when setting up the application.
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # You can run this file directly to create the database schema
    print("Creating database tables for Munazzam...")
    create_all_tables()
    print("Tables created successfully.")