from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # admin, surveyor, citizen

class Owner(Base):
    __tablename__ = "owners"

    owner_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(String(255), nullable=True)

class Parcel(Base):
    __tablename__ = "parcels"

    parcel_id = Column(Integer, primary_key=True, index=True)
    ulpin_2d = Column(String(14), unique=True, nullable=False)
    area_sqm = Column(Float, nullable=False)

class Building(Base):
    __tablename__ = "buildings"

    building_id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("parcels.parcel_id"), nullable=False)
    total_floors = Column(Integer, default=1, nullable=False)

class Property(Base):
    __tablename__ = "properties"

    property_id = Column(Integer, primary_key=True, index=True)
    ulpin_3d = Column(String(30), unique=True, nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.building_id"), nullable=False)
    parcel_id = Column(Integer, ForeignKey("parcels.parcel_id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("owners.owner_id"), nullable=True)
    floor_number = Column(Integer, default=0, nullable=False)
    unit_index = Column(Integer, default=1, nullable=False)
    elevation_min_m = Column(Float, nullable=False)
    elevation_max_m = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=False)
    verification_status = Column(String(20), default="unverified", nullable=False)

class ConflictLog(Base):
    __tablename__ = "conflict_logs"

    conflict_id = Column(Integer, primary_key=True, index=True)
    property_id_a = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    property_id_b = Column(Integer, ForeignKey("properties.property_id"), nullable=True)
    conflict_type = Column(String(50), nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved = Column(Boolean, default=False, nullable=False)
