# app/services/itinerary.py

from typing import List, Dict
from sqlalchemy.orm import Session
from math import radians, sin, cos, sqrt, atan2
from app.models.trip import Place
from random import shuffle

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def nearest_point(current, points):
    """Return nearest point from a current location."""
    best = None
    best_dist = float("inf")
    for p in points:
        d = haversine(current["lat"], current["lon"], p["lat"], p["lon"])
        if d < best_dist:
            best = p
            best_dist = d
    return best

def cluster_places_by_distance(places: List[Dict], cluster_km=3.0):
    """
    Groups places into nearby clusters (simple version).
    """
    clusters = []
    for p in places:
        placed = False
        for cluster in clusters:
            for c in cluster:
                if haversine(p["lat"], p["lon"], c["lat"], c["lon"]) <= cluster_km:
                    cluster.append(p)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            clusters.append([p])
    return clusters

# def pick_places_by_preferences(db: Session, p):
#     out = []
#     if p.is_foodie:
#         out.extend(db.query(Place).filter(Place.category.ilike("%restaurant%")).limit(50).all())
#         out.extend(db.query(Place).filter(Place.category.ilike("%cafe%")).limit(50).all())
#     if p.likes_shopping:
#         out.extend(db.query(Place).filter(Place.category.ilike("%shopping%")).limit(50).all())
#         out.extend(db.query(Place).filter(Place.category.ilike("%mall%")).limit(50).all())
#     if p.wants_nightlife:
#         out.extend(db.query(Place).filter(Place.category.ilike("%bar%")).limit(50).all())
#     # Always include sights
#     out.extend(db.query(Place).filter(Place.category.ilike("%tour%")).limit(50).all())
#     out.extend(db.query(Place).filter(Place.category.ilike("%attract%")).limit(50).all())
#     out.extend(db.query(Place).filter(Place.category.ilike("%point_of_interest%")).limit(50).all())

#     # Deduplicate (by external_id or name)
#     unique = {}
#     for x in out:
#         key = x.external_id or x.name
#         unique[key] = x
    
#     return list(unique.values())

def pick_places_by_preferences(db: Session, p):
    # If no preferences -> use a general default
    if p is None:
        class DefaultPref:
            is_foodie = True
            likes_shopping = True
            wants_nightlife = False
            pace = "normal"
        p = DefaultPref()

    out = []

    # Food places
    if getattr(p, "is_foodie", False):
        out.extend(db.query(Place).filter(Place.category.ilike("%restaurant%")).limit(50).all())
        out.extend(db.query(Place).filter(Place.category.ilike("%cafe%")).limit(50).all())

    # Shopping
    if getattr(p, "likes_shopping", False):
        out.extend(db.query(Place).filter(Place.category.ilike("%mall%")).limit(50).all())
        out.extend(db.query(Place).filter(Place.category.ilike("%shopping%")).limit(50).all())

    # Nightlife
    if getattr(p, "wants_nightlife", False):
        out.extend(db.query(Place).filter(Place.category.ilike("%bar%")).limit(50).all())

    # Always include sightseeing
    out.extend(db.query(Place).filter(Place.category.ilike("%tour%")).limit(50).all())
    out.extend(db.query(Place).filter(Place.category.ilike("%attract%")).limit(50).all())
    out.extend(db.query(Place).filter(Place.category.ilike("%point_of_interest%")).limit(50).all())

    # Deduplicate
    unique = {}
    for x in out:
        key = x.external_id or x.name
        unique[key] = x

    return list(unique.values())


def build_itinerary_for_trip(db: Session, trip):
    preferences = trip.preferences
    pace_map = {"relaxed": 2, "normal": 4, "packed": 6}
    per_day = pace_map.get(preferences.pace if preferences else "normal", 4)

    # 1. Get list of places
    raw_places = pick_places_by_preferences(db, preferences)
    places = [{
        "id": p.id,
        "name": p.name,
        "lat": p.latitude,
        "lon": p.longitude,
        "category": p.category,
        "rating": p.rating,
        "source": p.source
    } for p in raw_places if p.latitude and p.longitude]

    if not places:
        return {"itinerary": []}

    # 2. Cluster places by distance
    clusters = cluster_places_by_distance(places, cluster_km=3)

    # Shuffle clusters for variety
    shuffle(clusters)

    itinerary = []

    day_index = 0

    for segment in trip.segments:
        for day in segment.days:
            if day_index >= len(clusters):
                break

            cluster = clusters[day_index]
            shuffle(cluster)

            # pick per_day places
            selected = cluster[:per_day]

            # sort by nearest-neighbor ordering
            if selected:
                route = [selected[0]]
                remaining = selected[1:]

                while remaining:
                    nxt = nearest_point(route[-1], remaining)
                    route.append(nxt)
                    remaining.remove(nxt)
            else:
                route = []

            itinerary.append({
                "segment": segment.city,
                "date": str(day.date),
                "activities": route
            })

            day_index += 1

    return {"itinerary": itinerary}
