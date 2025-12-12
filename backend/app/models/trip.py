# backend/app/models/trip.py
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Float, Boolean, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    segments = relationship("TripSegment", back_populates="trip", cascade="all, delete-orphan")
    preferences = relationship("Preference", back_populates="trip", uselist=False, cascade="all, delete-orphan")

class TripSegment(Base):
    __tablename__ = "trip_segments"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    city = Column(String(256), nullable=False)
    country = Column(String(128), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    suggested_transport = Column(String(64), nullable=True)  # e.g., flight/train/bus
    notes = Column(Text, nullable=True)

    trip = relationship("Trip", back_populates="segments")
    days = relationship("TripDay", back_populates="segment", cascade="all, delete-orphan")
    transport_options = relationship("TransportOption", back_populates="segment", cascade="all, delete-orphan")

class TripDay(Base):
    __tablename__ = "trip_days"
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("trip_segments.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1..n within that segment
    date = Column(Date, nullable=False)

    segment = relationship("TripSegment", back_populates="days")
    activities = relationship("Activity", back_populates="day", cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=True)
    name = Column(String(256), nullable=False)
    type = Column(String(64), nullable=True)  # food/sight/shopping/nature
    start_time = Column(String(16), nullable=True)
    end_time = Column(String(16), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    day = relationship("TripDay", back_populates="activities")
    place = relationship("Place", back_populates="activities")

class TransportOption(Base):
    __tablename__ = "transport_options"
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("trip_segments.id", ondelete="CASCADE"), nullable=False)
    mode = Column(String(32), nullable=False)  # flight/train/bus/car
    provider = Column(String(128), nullable=True)  # e.g., Skyscanner, Amtrak
    price = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    departure = Column(String(128), nullable=True)
    arrival = Column(String(128), nullable=True)
    booking_url = Column(String(512), nullable=True)

    segment = relationship("TripSegment", back_populates="transport_options")

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, unique=True)
    pace = Column(String(32), default="normal")  # relaxed/normal/packed
    foodie = Column(Boolean, default=False)
    shopping = Column(Boolean, default=False)
    nightlife = Column(Boolean, default=False)
    accessibility_needs = Column(Text, nullable=True)
    budget_level = Column(String(32), nullable=True)  # low/medium/high

    trip = relationship("Trip", back_populates="preferences")

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    category = Column(String(128), nullable=True)  # restaurant, museum, mall...
    rating = Column(Float, nullable=True)
    price_level = Column(Integer, nullable=True)  # 1..4
    address = Column(String(512), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    external_id = Column(String(256), nullable=True)  # provider id (Google/Yelp)
    source = Column(String(64), nullable=True)  # google/yelp/foursquare

    activities = relationship("Activity", back_populates="place")
