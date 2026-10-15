import argparse
import html
import logging
import sys
import time
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .build import build_calendar
from .config import FEEDS, MAX_FAILURE_RATIO, REQUEST_DELAY_SECONDS, TIMEOUT_SECONDS, USER_AGENT, Feed
from .fetch import FetchError, fetch_event
from .reconcile import reconcile
from .scrape import list_event_urls
from .state import load_state, save_state

log = logging.getLogger("tum_events_sync")


class SyncAborted(Exception):
    pass


def http_getter() -> Callable[[str], str]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(total=3, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))

    def get(url: str) -> str:
        response = session.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        response.encoding = response.encoding or "utf-8"
        return response.text

    return get


def render_index(feeds: Sequence[Feed]) -> str:
    items = "\n".join(
        f'    <li><a href="{f.name}.ics">{html.escape(f.title)}</a> '
        f"(<code>{f.name}.ics</code>)</li>"
        for f in feeds
    )
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TUM CHN Calendars</title>
<body style="font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem">
  <h1>TUM CHN calendars</h1>
  <p>Subscribe to these feeds in your calendar app (Apple Calendar: File → New Calendar Subscription).</p>
  <ul>
{items}
  </ul>
</body>
</html>
"""


def run(
    get: Callable[[str], str],
    state_path: Path,
    out_dir: Path,
    now: datetime,
    feeds: Sequence[Feed] = FEEDS,
    delay: float = REQUEST_DELAY_SECONDS,
) -> None:
    seen: dict[str, list[str]] = {}
    for feed in feeds:
        urls = list_event_urls(feed.list_url, get)
        log.info("%s: %d events listed", feed.name, len(urls))
        if not urls:
            raise SyncAborted(f"{feed.name}: list returned no events")
        seen[feed.name] = urls

    all_urls = list(dict.fromkeys(u for urls in seen.values() for u in urls))
    fetched: dict[str, dict] = {}
    failures = 0
    for url in all_urls:
        time.sleep(delay)
        try:
            fetched[url] = fetch_event(url, get)
        except (FetchError, requests.RequestException) as exc:
            failures += 1
            log.warning("skipping %s: %s", url, exc)

    if failures > MAX_FAILURE_RATIO * len(all_urls):
        raise SyncAborted(f"{failures}/{len(all_urls)} event downloads failed")

    state = reconcile(load_state(state_path), seen, fetched, now)
    save_state(state_path, state)

    out_dir.mkdir(parents=True, exist_ok=True)
    for feed in feeds:
        (out_dir / f"{feed.name}.ics").write_bytes(build_calendar(feed.name, feed.title, state))
    (out_dir / "index.html").write_text(render_index(feeds), encoding="utf-8")
    log.info("wrote %d events to %s", len(state), out_dir)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tum_events_sync")
    parser.add_argument("--state", type=Path, default=Path("state/events.json"))
    parser.add_argument("--out", type=Path, default=Path("public"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run(http_getter(), args.state, args.out, datetime.now(timezone.utc))
    except SyncAborted as exc:
        log.error("aborted: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
