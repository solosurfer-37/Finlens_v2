from fastapi import FastAPI

from app.database.database import create_tables

app = FastAPI(
    title="FinLens Backend",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/")
def root():
    return {"message": "FinLens Backend Running 🚀"}