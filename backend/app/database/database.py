from sqlalchemy import create_engine

from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

# Schema is managed exclusively through Alembic migrations now.
# Run: py -m alembic upgrade head
