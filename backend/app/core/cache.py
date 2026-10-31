import json

import redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_cache(key: str) -> dict | list | None:
    """Returns cached value as parsed JSON, or None if not found."""
    value = redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


def set_cache(key: str, value: dict | list, ttl_seconds: int = 300) -> None:
    """Stores value as JSON with a time-to-live (default 5 minutes)."""
    redis_client.set(key, json.dumps(value), ex=ttl_seconds)


def delete_cache(key: str) -> None:
    redis_client.delete(key)


def invalidate_investigation_cache(user_id: int, investigation_id: int) -> None:
    """Drop every cached view of one investigation (detail, graph, report)."""
    for prefix in ("investigation", "graph", "report"):
        delete_cache(f"{prefix}:{user_id}:{investigation_id}")
