from sqlalchemy import create_engine
from app import models
from app.config import settings
from app.database.base import Base

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def create_tables():
    """
    Creates all registered database tables.
    """
    Base.metadata.create_all(bind=engine)