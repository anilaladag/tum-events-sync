from collections.abc import Mapping
from datetime import timedelta

from icalendar import Calendar, Event
from icalendar.prop import vDuration

REFRESH = timedelta(hours=6)


def build_calendar(feed: str, title: str, state: Mapping[str, dict]) -> bytes:
    cal = Calendar()
    cal.add("PRODID", "-//tum-events-sync//EN")
    cal.add("VERSION", "2.0")
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("METHOD", "PUBLISH")
    cal.add("X-WR-CALNAME", title)
    cal.add("NAME", title)
    cal.add("X-WR-TIMEZONE", "Europe/Berlin")
    cal["REFRESH-INTERVAL"] = vDuration(REFRESH)
    cal["REFRESH-INTERVAL"].params["VALUE"] = "DURATION"
    cal["X-PUBLISHED-TTL"] = vDuration(REFRESH)

    events = []
    for url, record in state.items():
        if feed not in record["feeds"]:
            continue
        for raw in record["vevents"]:
            event = Event.from_ical(raw)
            if "URL" not in event:
                event.add("URL", url)
            events.append(event)

    events.sort(key=lambda e: (e.decoded("DTSTART").isoformat(), str(e["UID"])))
    for event in events:
        cal.add_component(event)
    return cal.to_ical()
