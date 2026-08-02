from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Every SQLAlchemy model in FinLens will inherit from this class.
    """
    pass