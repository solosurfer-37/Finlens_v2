from app.core.cache import get_cache, invalidate_investigation_cache, set_cache


def test_invalidate_removes_all_three_views_for_that_investigation():
    for prefix in ("investigation", "graph", "report"):
        set_cache(f"{prefix}:1:5", {"x": 1})

    invalidate_investigation_cache(1, 5)

    for prefix in ("investigation", "graph", "report"):
        assert get_cache(f"{prefix}:1:5") is None


def test_invalidate_leaves_other_users_and_investigations_alone():
    set_cache("graph:1:5", {"x": 1})
    set_cache("graph:2:5", {"x": 2})
    set_cache("graph:1:6", {"x": 3})

    invalidate_investigation_cache(1, 5)

    assert get_cache("graph:1:5") is None
    assert get_cache("graph:2:5") == {"x": 2}
    assert get_cache("graph:1:6") == {"x": 3}