from datetime import datetime, timezone

from tum_events_sync.reconcile import reconcile

NOW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
PAST = "2026-10-01T10:00:00+00:00"
FUTURE = "2026-11-01T10:00:00+00:00"


def rec(url, ends, feeds=(), body="v1"):
    return {"url": url, "ends": ends, "vevents": [body], "feeds": list(feeds)}


def strip(record):
    return {k: v for k, v in record.items() if k != "feeds"}


def test_new_event_is_added_with_its_feeds():
    fetched = {"a": strip(rec("a", FUTURE))}
    state = reconcile({}, {"tum-events": ["a"], "freshers": ["a"]}, fetched, NOW)
    assert state["a"]["feeds"] == ["freshers", "tum-events"]


def test_seen_event_is_updated():
    old = {"a": rec("a", FUTURE, ["tum-events"], body="v1")}
    fetched = {"a": strip(rec("a", FUTURE, body="v2"))}
    state = reconcile(old, {"tum-events": ["a"]}, fetched, NOW)
    assert state["a"]["vevents"] == ["v2"]


def test_unseen_past_event_is_kept():
    old = {"a": rec("a", PAST, ["tum-events"])}
    state = reconcile(old, {"tum-events": []}, {}, NOW)
    assert state["a"]["feeds"] == ["tum-events"]


def test_unseen_future_event_is_dropped():
    old = {"a": rec("a", FUTURE, ["tum-events"])}
    assert reconcile(old, {"tum-events": []}, {}, NOW) == {}


def test_retention_is_per_feed():
    old = {"a": rec("a", FUTURE, ["freshers", "tum-events"])}
    fetched = {"a": strip(rec("a", FUTURE))}
    state = reconcile(old, {"tum-events": ["a"], "freshers": []}, fetched, NOW)
    assert state["a"]["feeds"] == ["tum-events"]


def test_seen_but_failed_fetch_keeps_previous_copy():
    old = {"a": rec("a", FUTURE, ["tum-events"], body="old")}
    state = reconcile(old, {"tum-events": ["a"]}, {}, NOW)
    assert state["a"]["vevents"] == ["old"]
    assert state["a"]["feeds"] == ["tum-events"]


def test_seen_failed_and_unknown_event_is_skipped():
    assert reconcile({}, {"tum-events": ["a"]}, {}, NOW) == {}


def test_old_state_is_not_mutated():
    old = {"a": rec("a", PAST, ["tum-events"])}
    reconcile(old, {"tum-events": []}, {}, NOW)
    assert old["a"]["feeds"] == ["tum-events"]
