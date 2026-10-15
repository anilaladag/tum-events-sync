from icalendar import Calendar

from tum_events_sync.build import build_calendar
from tum_events_sync.fetch import parse_ics


def test_build_calendar_contains_only_feed_events(fixture_text):
    timed = parse_ics(fixture_text("timed.ics"), "https://chn.tum.de/event/event/timed")
    allday = parse_ics(fixture_text("allday.ics"), "https://chn.tum.de/event/event/allday")
    state = {
        timed["url"]: {**timed, "feeds": ["tum-events"]},
        allday["url"]: {**allday, "feeds": ["tum-events-for-freshers"]},
    }

    cal = Calendar.from_ical(build_calendar("tum-events", "TUM CHN Events", state))
    events = cal.walk("VEVENT")

    assert str(cal["X-WR-CALNAME"]) == "TUM CHN Events"
    assert cal["REFRESH-INTERVAL"].to_ical() == b"PT6H"
    assert len(events) == 1
    assert str(events[0]["URL"]) == "https://chn.tum.de/event/event/timed"
    assert str(events[0]["SUMMARY"]) == "Master in Information Engineering - Info Session"


def test_build_calendar_is_sorted_and_deterministic(fixture_text):
    timed = parse_ics(fixture_text("timed.ics"), "https://chn.tum.de/event/event/timed")
    allday = parse_ics(fixture_text("allday.ics"), "https://chn.tum.de/event/event/allday")
    state = {
        timed["url"]: {**timed, "feeds": ["f"]},
        allday["url"]: {**allday, "feeds": ["f"]},
    }
    first = build_calendar("f", "F", state)
    assert first == build_calendar("f", "F", dict(reversed(state.items())))
    summaries = [str(e["SUMMARY"]) for e in Calendar.from_ical(first).walk("VEVENT")]
    assert summaries[0].startswith("Europe")  # starts 2026-09-03, before 2026-10-15


def test_build_empty_calendar_is_valid():
    cal = Calendar.from_ical(build_calendar("f", "F", {}))
    assert cal.walk("VEVENT") == []
