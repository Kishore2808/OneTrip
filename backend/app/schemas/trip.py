# backend/app/schemas/trip.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class PlaceCreate(BaseModel):
    name: str
    category: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    external_id: Optional[str]
    source: Optional[str]

class ActivityCreate(BaseModel):
    name: str
    type: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    estimated_cost: Optional[float]
    place: Optional[PlaceCreate]

class TripDayCreate(BaseModel):
    day_number: int
    date: date
    activities: List[ActivityCreate] = []

class TripSegmentCreate(BaseModel):
    city: str
    country: Optional[str]
    start_date: date
    end_date: date
    days: List[TripDayCreate] = []

# class TripCreate(BaseModel):
#     user_id: int
#     title: Optional[str]
#     description: Optional[str]
#     start_date: date
#     end_date: date
#     budget: Optional[float]
#     segments: List[TripSegmentCreate] = []

class TripCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: date
    end_date: date
    budget: Optional[float] = None
    segments: List[TripSegmentCreate] = []


class PreferenceCreate(BaseModel):
    pace: Optional[str] = "normal"
    foodie: Optional[bool] = False
    shopping: Optional[bool] = False
    nightlife: Optional[bool] = False
    budget_level: Optional[str] = None
