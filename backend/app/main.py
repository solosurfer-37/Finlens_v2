from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import upload, investigation, evidence, report, graph, auth, health
from app.config import settings
from app.core.rate_limiter import limiter

app = FastAPI(
    title="FinLens Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(upload.router)
app.include_router(investigation.router)
app.include_router(evidence.router)
app.include_router(report.router)
app.include_router(graph.router)
app.include_router(auth.router)
app.include_router(health.router)


@app.get("/")
def root():
    return {"message": "FinLens Backend Running"}