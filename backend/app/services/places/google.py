# app/services/places/google.py
import os
import requests
from typing import Dict, List, Optional

GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def google_text_search(query: str, location: Optional[str] = None, radius: Optional[int] = None, limit: int = 20) -> List[Dict]:
    """
    Simple wrapper around Google Places Text Search.
    location: "lat,lng" string (optional)
    radius: meters (optional)
    """
    params = {"key": GOOGLE_KEY, "query": query}
    if location:
        params["location"] = location
    if radius:
        params["radius"] = radius
    resp = requests.get(TEXT_SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])[:limit]
    return results

def google_place_details(place_id: str, fields: Optional[List[str]] = None) -> Dict:
    params = {"key": GOOGLE_KEY, "place_id": place_id}
    if fields:
        params["fields"] = ",".join(fields)
    resp = requests.get(DETAILS_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("result", {})
