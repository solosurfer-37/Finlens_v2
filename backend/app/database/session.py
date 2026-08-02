from sqlalchemy.orm import sessionmaker

from app.database.database import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)



from typing import Generator

from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — provides a DB session per request,
    and guarantees it closes afterward (even if an error occurs).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()