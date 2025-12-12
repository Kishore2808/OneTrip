# app/services/places/normalizer.py
from typing import Dict, Any

def normalize_google_place(raw: Dict) -> Dict[str, Any]:
    geometry = raw.get("geometry", {})
    loc = geometry.get("location", {}) if geometry else {}
    return {
        "external_id": raw.get("place_id"),
        "source": "google",
        "name": raw.get("name"),
        "address": raw.get("formatted_address") or raw.get("vicinity"),
        "lat": loc.get("lat"),
        "lon": loc.get("lng"),
        "category": ", ".join(raw.get("types", [])) if raw.get("types") else None,
        "rating": raw.get("rating"),
        "user_ratings_total": raw.get("user_ratings_total"),
        "price_level": raw.get("price_level"),
        "raw": raw
    }

def normalize_fsq_place(raw: Dict) -> Dict[str, Any]:
    # Foursquare structure: name, geocodes -> main -> latitude/longitude, location -> formatted_address
    geocodes = raw.get("geocodes", {})
    main = geocodes.get("main", {}) if geocodes else {}
    location = raw.get("location", {})
    categories = raw.get("categories") or []
    cat_names = [c.get("name") for c in categories if c.get("name")]
    return {
        "external_id": raw.get("fsq_id"),
        "source": "foursquare",
        "name": raw.get("name"),
        "address": location.get("formatted_address"),
        "lat": main.get("latitude"),
        "lon": main.get("longitude"),
        "category": ", ".join(cat_names) if cat_names else None,
        "rating": raw.get("rating"),   # may be missing
        "user_ratings_total": raw.get("stats", {}).get("total_ratings") if raw.get("stats") else None,
        "price_level": raw.get("price"),  # may be present
        "raw": raw
    }
