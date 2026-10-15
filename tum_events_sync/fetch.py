from collections.abc import Callable
from datetime import date, datetime, timezone

from icalendar import Calendar

ICS_QUERY = "?tx_calendarize_calendar%5Bformat%5D=ics&type=1600"


class FetchError(Exception):
    pass


def ics_url(event_url: str) -> str:
    return event_url + ICS_QUERY


def _as_utc(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


def _end(vevent) -> datetime:
    prop = vevent.get("DTEND") or vevent.get("DTSTART")
    return _as_utc(prop.dt)


def parse_ics(text: str, event_url: str) -> dict:
    """Turn one event's ICS into a stored record: url, latest end time, raw VEVENTs."""
    if not text.lstrip().startswith("BEGIN:VCALENDAR"):
        raise FetchError(f"not an ICS document: {event_url}")
    try:
        vevents = Calendar.from_ical(text).walk("VEVENT")
    except ValueError as exc:
        raise FetchError(f"invalid ICS for {event_url}: {exc}") from exc
    if not vevents:
        raise FetchError(f"no events in ICS: {event_url}")
    return {
        "url": event_url,
        "ends": max(_end(v) for v in vevents).isoformat(),
        "vevents": [v.to_ical().decode("utf-8") for v in vevents],
    }


def fetch_event(event_url: str, get: Callable[[str], str]) -> dict:
    return parse_ics(get(ics_url(event_url)), event_url)
