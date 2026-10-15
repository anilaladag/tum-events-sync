from dataclasses import dataclass


@dataclass(frozen=True)
class Feed:
    name: str
    title: str
    list_url: str


FEEDS = (
    Feed("tum-events", "TUM CHN Events", "https://chn.tum.de/events"),
    Feed(
        "tum-events-for-freshers",
        "TUM CHN Events for Freshers",
        "https://chn.tum.de/events/events-for-freshers",
    ),
)

USER_AGENT = "tum-events-sync (+https://github.com/anilaladag/tum-events-sync)"
TIMEOUT_SECONDS = 30
REQUEST_DELAY_SECONDS = 1.0
MAX_PAGES = 20
MAX_FAILURE_RATIO = 0.3
