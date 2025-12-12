# app/api/trips.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.trip import TripCreate, PreferenceCreate
from app.crud.trip import create_trip, get_trip, upsert_preferences
from app.models.trip import Place
from app.services.itinerary import build_itinerary_for_trip

router = APIRouter(prefix="/trips", tags=["trips"])


# -----------------------
# Create Trip (Authenticated)
# -----------------------
@router.post("/", status_code=201)
def create_new_trip(
    trip_in: TripCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Force trip owner to the logged-in user
    trip_in.user_id = current_user.id

    trip = create_trip(db, trip_in)
    return {"id": trip.id}


# -----------------------
# Get Trip (Authenticated + Owner-only)
# -----------------------
@router.get("/{trip_id}")
def read_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view this trip"
        )

    return trip


# -----------------------
# Update Preferences
# -----------------------
@router.post("/{trip_id}/preferences")
def update_preferences(
    trip_id: int,
    prefs: PreferenceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to modify this trip"
        )

    pref = upsert_preferences(db, trip_id, prefs)
    return pref


# -----------------------
# Generate Itinerary
# -----------------------
@router.post("/{trip_id}/generate_itinerary")
def generate_itinerary(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. verify trip exists
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # 2. ensure current user owns the trip
    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot generate itinerary for this trip"
        )

    # 3. call smart itinerary service
    itinerary = build_itinerary_for_trip(db, trip)

    return itinerary













# _______First Version of trips.py _______


# # backend/app/api/trips.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db import SessionLocal
# from app.schemas.trip import TripCreate, PreferenceCreate
# from app import crud
# from app.models.trip import Place


# router = APIRouter(prefix="/trips", tags=["trips"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/", status_code=201)
# def create_trip(trip_in: TripCreate, db: Session = Depends(get_db)):
#     trip = crud.trip.create_trip(db, trip_in)
#     return {"id": trip.id}

# @router.get("/{trip_id}")
# def read_trip(trip_id: int, db: Session = Depends(get_db)):
#     trip = crud.trip.get_trip(db, trip_id)
#     if not trip:
#         raise HTTPException(status_code=404, detail="Trip not found")
#     # For brevity return ORM object — FastAPI will convert but you can serialize manually
#     return trip

# @router.post("/{trip_id}/preferences")
# def set_preferences(trip_id: int, prefs: PreferenceCreate, db: Session = Depends(get_db)):
#     from app.crud.trip import upsert_preferences
#     pref = upsert_preferences(db, trip_id, prefs)
#     return pref

# @router.post("/{trip_id}/generate_itinerary")
# def generate_itinerary(trip_id: int, db: Session = Depends(get_db)):
#     """
#     Quick rule-based itinerary generator:
#     - reads trip + preferences + places (if any)
#     - fills days with activities based on pace and preferences
#     This is a simple starter; we'll expand with LLM + optimization later.
#     """
#     trip = crud.trip.get_trip(db, trip_id)
#     if not trip:
#         raise HTTPException(status_code=404, detail="Trip not found")

#     # Simple baseline: for each day, pick up to N mock activities
#     pace_map = {"relaxed": 2, "normal": 4, "packed": 6}
#     pace = trip.preferences.pace if trip.preferences else "normal"
#     per_day = pace_map.get(pace, 4)
#     result = []
#     for seg in trip.segments:
#         for day in seg.days:
#             activities = []
#             # if there are places in DB for that city, pick top per_day (very naive)
#             # places = db.query(app.models.Place).filter(app.models.Place.source != None).limit(per_day).all()
#             places = db.query(Place).filter(Place.source != None).limit(per_day).all()
#             idx = 0
#             while len(activities) < per_day:
#                 if idx < len(places):
#                     p = places[idx]
#                     activities.append({
#                         "name": p.name,
#                         "category": p.category,
#                         "lat": p.latitude,
#                         "lon": p.longitude
#                     })
#                 else:
#                     # fallback mock activity
#                     activities.append({"name": f"Explore {seg.city} - sight {len(activities)+1}"})
#                 idx += 1
#             result.append({"segment": seg.city, "date": str(day.date), "activities": activities})
#     return {"itinerary": result}
