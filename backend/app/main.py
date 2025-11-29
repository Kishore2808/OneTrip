from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Trip Planner API running on Windows!"}
