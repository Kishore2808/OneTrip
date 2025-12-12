# backend/app/crud/trip.py
from sqlalchemy.orm import Session
from app.models.trip import Trip, TripSegment, TripDay, Activity, Place, Preference, TransportOption
from datetime import date

def create_trip(db: Session, trip_in):
    trip = Trip(
        user_id=trip_in.user_id,
        title=trip_in.title,
        description=trip_in.description,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        budget=trip_in.budget
    )
    db.add(trip)
    db.flush()  # ensure trip.id available

    # create segments -> days -> activities
    for seg_in in trip_in.segments:
        seg = TripSegment(
            trip_id=trip.id,
            city=seg_in.city,
            country=seg_in.country,
            start_date=seg_in.start_date,
            end_date=seg_in.end_date
        )
        db.add(seg)
        db.flush()
        for day_in in seg_in.days:
            day = TripDay(segment_id=seg.id, day_number=day_in.day_number, date=day_in.date)
            db.add(day)
            db.flush()
            for act_in in day_in.activities:
                place = None
                if act_in.place:
                    place = Place(
                        name=act_in.place.name,
                        category=act_in.place.category,
                        latitude=act_in.place.latitude,
                        longitude=act_in.place.longitude,
                        external_id=act_in.place.external_id,
                        source=act_in.place.source
                    )
                    db.add(place)
                    db.flush()
                activity = Activity(
                    day_id=day.id,
                    place_id=place.id if place else None,
                    name=act_in.name,
                    type=act_in.type,
                    start_time=act_in.start_time,
                    end_time=act_in.end_time,
                    latitude=act_in.latitude,
                    longitude=act_in.longitude,
                    estimated_cost=act_in.estimated_cost
                )
                db.add(activity)
    db.commit()
    db.refresh(trip)
    return trip

def get_trip(db: Session, trip_id: int):
    return db.query(Trip).filter(Trip.id == trip_id).first()

def upsert_preferences(db: Session, trip_id: int, prefs_in):
    pref = db.query(Preference).filter(Preference.trip_id == trip_id).one_or_none()
    if not pref:
        pref = Preference(trip_id=trip_id)
        db.add(pref)
    pref.pace = prefs_in.pace
    pref.foodie = prefs_in.foodie
    pref.shopping = prefs_in.shopping
    pref.nightlife = prefs_in.nightlife
    pref.budget_level = prefs_in.budget_level
    db.commit()
    db.refresh(pref)
    return pref
