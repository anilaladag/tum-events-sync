from datetime import datetime, timezone

import pytest

from tum_events_sync.fetch import FetchError, fetch_event, ics_url, parse_ics

EVENT = "https://chn.tum.de/event/event/master-in-information-engineering-info-session-15102026"


def test_ics_url():
    assert ics_url(EVENT) == EVENT + "?tx_calendarize_calendar%5Bformat%5D=ics&type=1600"


def test_parse_timed_event(fixture_text):
    record = parse_ics(fixture_text("timed.ics"), EVENT)
    assert record["url"] == EVENT
    assert record["ends"] == "2026-10-15T14:00:00+00:00"
    assert len(record["vevents"]) == 1
    assert "UID:calendarize-master-in-information-engineering" in record["vevents"][0]


def test_parse_all_day_event_uses_end_date(fixture_text):
    record = parse_ics(fixture_text("allday.ics"), "https://chn.tum.de/event/event/x")
    assert record["ends"] == datetime(2027, 1, 1, tzinfo=timezone.utc).isoformat()


def test_parse_rejects_non_calendar():
    with pytest.raises(FetchError):
        parse_ics("<!DOCTYPE html><html></html>", EVENT)


def test_parse_rejects_calendar_without_events():
    with pytest.raises(FetchError):
        parse_ics("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n", EVENT)


def test_fetch_event_requests_ics_url(fixture_text):
    seen = []

    def get(url):
        seen.append(url)
        return fixture_text("timed.ics")

    assert fetch_event(EVENT, get)["url"] == EVENT
    assert seen == [ics_url(EVENT)]
