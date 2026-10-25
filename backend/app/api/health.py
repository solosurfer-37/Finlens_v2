from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.cache import redis_client
from app.database.session import get_db

router = APIRouter(tags=["Health"])


def _check_database(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    try:
        return bool(redis_client.ping())
    except Exception:
        return False


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Readiness probe: 200 if Postgres and Redis respond, else 503."""
    checks = {
        "database": "ok" if _check_database(db) else "down",
        "redis": "ok" if _check_redis() else "down",
    }
    healthy = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ok" if healthy else "unhealthy", **checks},
    )