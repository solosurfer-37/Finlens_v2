# FinLens - AI Powered Financial Crime Investigation Platform

[![CI](https://github.com/solosurfer-37/Finlens_v2/actions/workflows/ci.yml/badge.svg)](https://github.com/solosurfer-37/Finlens_v2/actions/workflows/ci.yml)

Backend that ingests bank transaction CSVs, detects suspicious behaviour with a pluggable detection engine, scores risk, and generates AI investigation reports.

- Live API: https://finlens-v2.onrender.com
- Interactive docs: https://finlens-v2.onrender.com/docs
- Health check: https://finlens-v2.onrender.com/health

Hosted on free tiers: the first request after idle can take 30-60 seconds.

## Tech stack

FastAPI, SQLAlchemy 2.0, PostgreSQL (Neon), Alembic, Pydantic v2, Redis, JWT, Google Gemini, Docker, pytest.

## Features

- CSV upload with validation (extension, size limit, schema, amounts)
- 10 pluggable fraud detectors producing evidence with related accounts and transactions
- Risk scoring from evidence severity (capped at 100)
- Transaction graph with suspicious nodes and edges highlighted
- AI-written investigation reports (Google Gemini) with a template fallback
- JWT authentication, per-user data isolation, Redis caching, rate limiting

## Architecture

    app/api            routers (HTTP only)
    app/controllers    thin orchestration, error translation
    app/services       business logic (CSV parsing, transactions, graph building)
    app/repositories   all database access
    app/engine         detection, evidence and report engines
    app/detectors      one class per fraud pattern
    app/ai             Gemini client, prompts, report generator
    app/models         SQLAlchemy 2.0 models
    app/schemas        Pydantic schemas
    app/core           cache, security, rate limiter, time helper

Upload flow: save file, parse CSV, create investigation, resolve accounts and transactions, run detectors, persist evidence and risk score, generate report. If any step fails, the investigation is marked Failed and the uploaded file is removed.

## Detectors

benford, centrality, cycle_detection, dsu, fan_out, historical_baseline, large_transfer, structuring, velocity, watchlist.

Examples: structuring flags 3+ transactions between the same pair on one day at 85-100% of the 10 lakh reporting threshold; velocity flags 5+ transactions from one sender within an hour; cycle_detection finds circular money flows (all simple cycles, capped at 50).


## API

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create a user |
| POST | /auth/login | Get a JWT |
| POST | /upload/ | Upload a CSV and run the full pipeline |
| GET | /investigations/ | List your investigations |
| GET | /investigations/{id} | Investigation detail |
| GET | /investigations/{id}/evidence | Evidence found |
| GET | /investigations/{id}/graph | Transaction graph |
| GET | /investigations/{id}/report | AI investigation report |
| GET | /health | Database and Redis health |

## Local setup

    cd backend
    pip install -r requirements-dev.txt
    copy .env.example .env
    alembic upgrade head
    py -m uvicorn app.main:app --reload

Fill in `.env` first (DATABASE_URL, REDIS_URL, SECRET_KEY, GEMINI_API_KEY). Python 3.14 is used in development.

Or run the app and Redis with Docker:

    cd backend
    docker compose up -d --build
## Testing and CI

Tests need a local Postgres database named `finlens_test` and Redis on localhost:6379.

    cd backend
    py -m pytest -q

GitHub Actions runs the suite on every push against Postgres 16 and Redis 7.

## Design decisions

- Multi-tenant isolation: accounts are unique per user, every query is scoped by owner, ownership is checked before cache reads.
- Money is Decimal / Numeric(18,2), never float.
- Container runs as a non-root user.
- Caches are TTL-based and explicitly invalidated after upload.
- Gemini failures are logged and fall back to a template report instead of failing the upload.
- Uploads are stored on ephemeral disk by design (no object storage).