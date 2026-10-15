import copy
from collections.abc import Mapping, Sequence
from datetime import datetime


def reconcile(
    old: Mapping[str, dict],
    seen: Mapping[str, Sequence[str]],
    fetched: Mapping[str, dict],
    now: datetime,
) -> dict[str, dict]:
    """Merge one run into the stored state, keyed by event URL.

    Per feed: events listed this run are kept (fresh copy if fetched, else the
    previous copy); unlisted events are kept only if they already ended.
    """
    state: dict[str, dict] = {}

    def keep(url: str, feed: str, record: dict) -> None:
        entry = state.setdefault(url, {**copy.deepcopy(record), "feeds": []})
        if feed not in entry["feeds"]:
            entry["feeds"].append(feed)

    for feed, urls in seen.items():
        listed = set(urls)
        for url in urls:
            record = fetched.get(url) or old.get(url)
            if record:
                keep(url, feed, {k: v for k, v in record.items() if k != "feeds"})
        for url, record in old.items():
            if url in listed or feed not in record["feeds"]:
                continue
            if datetime.fromisoformat(record["ends"]) < now:
                keep(url, feed, {k: v for k, v in record.items() if k != "feeds"})

    for entry in state.values():
        entry["feeds"].sort()
    return state
