from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import upload, investigation, evidence, report, graph, auth
from app.core.rate_limiter import limiter

app = FastAPI(
    title="FinLens Backend",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(upload.router)
app.include_router(investigation.router)
app.include_router(evidence.router)
app.include_router(report.router)
app.include_router(graph.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "FinLens Backend Running"}
