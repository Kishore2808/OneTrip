# app/services/places/service.py
import os
from typing import List, Dict, Optional
from app.services.places.google import google_text_search, google_place_details
from app.services.places.foursquare import fsq_search
from app.services.places.normalizer import normalize_google_place, normalize_fsq_place
from app.db import SessionLocal
from app.models.trip import Place as PlaceModel  # your Place model
from sqlalchemy import select
from math import radians, cos, sin, asin, sqrt

CACHE_ENABLED = os.getenv("PLACES_CACHE_ENABLED", "true").lower() in ("1", "true", "yes")

def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in kilometers
    lon1, lat1, lon2, lat2 = map(float, (lon1, lat1, lon2, lat2))
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def find_cached_place_by_external(db, external_id: str, source: str):
    return db.query(PlaceModel).filter(PlaceModel.external_id == external_id, PlaceModel.source == source).first()

def find_cached_nearby_by_name(db, name: str, lat: float, lon: float, radius_km: float = 0.3):
    # naive approach: find places with same name and within radius_km
    rows = db.query(PlaceModel).filter(PlaceModel.name == name).all()
    for r in rows:
        if r.latitude is None or r.longitude is None:
            continue
        dist = haversine_km(lat, lon, r.latitude, r.longitude)
        if dist <= radius_km:
            return r
    return None

def cache_place(db, normalized: Dict):
    p = find_cached_place_by_external(db, normalized.get("external_id"), normalized.get("source"))
    if p:
        return p
    # create new
    new = PlaceModel(
        name=normalized.get("name"),
        category=normalized.get("category"),
        rating=normalized.get("rating"),
        price_level=normalized.get("price_level"),
        address=normalized.get("address"),
        latitude=normalized.get("lat"),
        longitude=normalized.get("lon"),
        external_id=normalized.get("external_id"),
        source=normalized.get("source")
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def try_google_then_fsq(query: str, ll: Optional[str] = None, radius: int = 5000, limit: int = 20) -> List[Dict]:
    results = []
    # 1) Google primary
    try:
        raw = google_text_search(query=query, location=ll, radius=radius, limit=limit)
        for r in raw:
            normalized = normalize_google_place(r)
            results.append(normalized)
        # If enough hits, return
        if len(results) >= max(3, min(limit, 5)):
            return results
    except Exception as e:
        # log later - for now continue to fallback
        pass

    # 2) Fallback to Foursquare
    try:
        raw2 = fsq_search(query=query, ll=ll, radius=radius, limit=limit)
        for r in raw2:
            normalized = normalize_fsq_place(r)
            results.append(normalized)
    except Exception:
        pass

    return results

def search_and_maybe_cache(query: str, ll: Optional[str], radius: int = 5000, limit: int = 20, use_cache: bool = True):
    raw_results = try_google_then_fsq(query=query, ll=ll, radius=radius, limit=limit)
    out = []
    if CACHE_ENABLED and use_cache:
        db = SessionLocal()
        try:
            for nr in raw_results:
                # try external id lookup
                cached = None
                ext = nr.get("external_id")
                src = nr.get("source")
                if ext and src:
                    cached = find_cached_place_by_external(db, ext, src)
                if not cached and nr.get("lat") and nr.get("lon"):
                    cached = find_cached_nearby_by_name(db, nr.get("name"), nr.get("lat"), nr.get("lon"))
                if cached:
                    out.append({
                        "id": cached.id,
                        "name": cached.name,
                        "address": cached.address,
                        "lat": cached.latitude,
                        "lon": cached.longitude,
                        "category": cached.category,
                        "rating": cached.rating,
                        "price_level": cached.price_level,
                        "source": cached.source,
                        "external_id": cached.external_id
                    })
                else:
                    saved = cache_place(db, nr)
                    out.append({
                        "id": saved.id,
                        "name": saved.name,
                        "address": saved.address,
                        "lat": saved.latitude,
                        "lon": saved.longitude,
                        "category": saved.category,
                        "rating": saved.rating,
                        "price_level": saved.price_level,
                        "source": saved.source,
                        "external_id": saved.external_id
                    })
        finally:
            db.close()
    else:
        # if not caching, return normalized raw results
        for nr in raw_results:
            out.append(nr)
    return out
