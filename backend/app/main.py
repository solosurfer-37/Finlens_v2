from fastapi import FastAPI

from app.api import upload, investigation , evidence

app = FastAPI(
    title="FinLens Backend",
    version="1.0.0",
)

app.include_router(upload.router)
app.include_router(investigation.router)
app.include_router(evidence.router)

@app.get("/")
def root():
    return {"message": "FinLens Backend Running"}