# app/api/places.py
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from app.services.places.service import search_and_maybe_cache
from app.api.deps import get_db  # if you need db usage in future

router = APIRouter(prefix="/places", tags=["places"])

@router.get("/search")
def places_search(
    q: str = Query(..., description="text query e.g., 'restaurants in Chennai' or 'museum'"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius: int = Query(5000, description="radius in meters"),
    limit: int = Query(20, description="max number of results"),
    cache: bool = Query(True, description="whether to cache results in DB")
):
    ll = None
    if lat is not None and lon is not None:
        ll = f"{lat},{lon}"
    try:
        res = search_and_maybe_cache(query=q, ll=ll, radius=radius, limit=limit, use_cache=cache)
        return {"count": len(res), "results": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
