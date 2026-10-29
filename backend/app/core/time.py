from datetime import UTC, datetime


def utc_now() -> datetime:
    """Current UTC time as a naive datetime, matching the timezone-less DateTime columns."""
    return datetime.now(UTC).replace(tzinfo=None)