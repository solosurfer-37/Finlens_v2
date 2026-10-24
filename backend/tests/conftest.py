import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (registers all tables on Base.metadata)
from app.config import settings
from app.core.rate_limiter import limiter
from app.database.base import Base
from app.database.session import get_db
from app.main import app

TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/finlens_test"

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

CACHE_PATTERNS = ("graph:*", "report:*", "investigation:*")


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_state():
    yield
    table_names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with test_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    r = redis.from_url(settings.redis_url)
    for pattern in CACHE_PATTERNS:
        for key in r.scan_iter(pattern):
            r.delete(key)


@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    limiter.enabled = True