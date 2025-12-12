# app/services/places/foursquare.py
import os
import requests
from typing import Dict, List, Optional

FSQ_KEY = os.getenv("FOURSQUARE_API_KEY")
SEARCH_URL = "https://api.foursquare.com/v3/places/search"

HEADERS = {
    "Accept": "application/json",
    "Authorization": FSQ_KEY
}

def fsq_search(query: str, ll: Optional[str] = None, radius: int = 5000, limit: int = 20) -> List[Dict]:
    """
    query: text query (e.g., 'restaurant')
    ll: 'lat,lon'
    """
    params = {"query": query, "limit": limit, "radius": radius}
    if ll:
        params["ll"] = ll
    resp = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Foursquare returns 'results' list
    return data.get("results", [])
