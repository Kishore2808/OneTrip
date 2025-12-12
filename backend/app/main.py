###first version 


# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Trip Planner API running on Windows!"}


###second version

from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.db import Base, engine

from app.api import trips  # ensure import

from app.api import places

# Auto-create DB tables (temporary for Week 1; migrations later)

# Base.metadata.create_all(bind=engine) #### commented out to use Alembic migrations

app = FastAPI(title="OneTrip API")

app.include_router(auth_router)
app.include_router(trips.router)
app.include_router(places.router)
@app.get("/")
def home():
    return {"message": "OneTrip backend running!"}
