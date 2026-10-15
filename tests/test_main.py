import json
from datetime import datetime, timezone

import pytest

from tum_events_sync.__main__ import SyncAborted, run
from tum_events_sync.config import Feed
from tum_events_sync.fetch import ics_url
from tum_events_sync.scrape import page_url

NOW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
LIST = "https://chn.tum.de/events"
FEEDS = (Feed("tum-events", "TUM CHN Events", LIST),)


def site(fixture_text, broken_events=0):
    """A fake site: one list page with 10 events, then an empty page."""
    from tum_events_sync.scrape import parse_event_urls

    p1 = fixture_text("events_p1.html")
    urls = parse_event_urls(p1, LIST)
    pages = {page_url(LIST, 1): p1, page_url(LIST, 2): fixture_text("events_p4.html")}
    timed = fixture_text("timed.ics")
    for i, url in enumerate(urls):
        body = "<html>oops</html>" if i < broken_events else timed.replace(
            "calendarize-master-in-information-engineering-info-session-15102026", f"uid-{i}"
        )
        pages[ics_url(url)] = body
    return pages.__getitem__, urls


def test_run_writes_state_and_calendars(tmp_path, fixture_text):
    get, urls = site(fixture_text)
    state_path, out = tmp_path / "state.json", tmp_path / "public"

    run(get, state_path, out, NOW, FEEDS, delay=0)

    state = json.loads(state_path.read_text())
    assert sorted(state) == sorted(urls)
    ics = (out / "tum-events.ics").read_text()
    assert ics.count("BEGIN:VEVENT") == 10
    assert "tum-events.ics" in (out / "index.html").read_text()


def test_run_tolerates_a_few_failures(tmp_path, fixture_text):
    get, _ = site(fixture_text, broken_events=2)
    run(get, tmp_path / "s.json", tmp_path / "out", NOW, FEEDS, delay=0)
    assert len(json.loads((tmp_path / "s.json").read_text())) == 8


def test_run_aborts_when_too_many_fetches_fail(tmp_path, fixture_text):
    get, _ = site(fixture_text, broken_events=4)
    state_path = tmp_path / "s.json"
    state_path.write_text('{"keep": "me"}')
    with pytest.raises(SyncAborted):
        run(get, state_path, tmp_path / "out", NOW, FEEDS, delay=0)
    assert state_path.read_text() == '{"keep": "me"}'
    assert not (tmp_path / "out").exists()


def test_run_aborts_on_empty_list(tmp_path, fixture_text):
    empty = fixture_text("events_p4.html")
    with pytest.raises(SyncAborted):
        run(lambda url: empty, tmp_path / "s.json", tmp_path / "out", NOW, FEEDS, delay=0)
    assert not (tmp_path / "s.json").exists()
