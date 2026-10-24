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

@pytest.fixture
def auth_headers(client):
    def _make(email: str, password: str = "StrongPass123") -> dict:
        client.post("/auth/register", json={"email": email, "password": password})
        resp = client.post("/auth/login", json={"email": email, "password": password})
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _make


@pytest.fixture
def sample_csv() -> bytes:
    header = (
        "transaction_reference,sender_account_number,sender_account_holder,"
        "sender_bank_name,receiver_account_number,receiver_account_holder,"
        "receiver_bank_name,amount,currency,transaction_time"
    )
    row = "TX-1,ACC-A,Alice,BankX,ACC-B,Bob,BankY,1200000,INR,2026-01-01 10:00:00"
    return f"{header}\n{row}\n".encode("utf-8")

@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """Never call the real Gemini API in tests; force the template fallback path."""

    def _fail(self, prompt):
        raise RuntimeError("Gemini disabled in tests")

    monkeypatch.setattr("app.ai.gemini_client.GeminiClient.generate", _fail)