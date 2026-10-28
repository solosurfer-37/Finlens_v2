# FinLens - AI Powered Financial Crime Investigation Platform

[![CI](https://github.com/solosurfer-37/Finlens_v2/actions/workflows/ci.yml/badge.svg)](https://github.com/solosurfer-37/Finlens_v2/actions/workflows/ci.yml)

Backend that ingests bank transaction CSVs, detects suspicious behaviour with a pluggable detection engine, scores risk, and generates AI investigation reports.

- Live API: https://finlens-v2.onrender.com
- Interactive docs: https://finlens-v2.onrender.com/docs
- Health check: https://finlens-v2.onrender.com/health

Hosted on free tiers: the first request after idle can take 30-60 seconds.

## Tech stack

FastAPI, SQLAlchemy 2.0, PostgreSQL (Neon), Alembic, Pydantic v2, Redis, JWT, Google Gemini, Docker, pytest.