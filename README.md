# tum-events-sync

Mirrors the event lists of TUM Campus Heilbronn as two subscribable calendars:

| Calendar | Source | Subscribe URL |
|---|---|---|
| TUM CHN Events | https://chn.tum.de/events | `https://anilaladag.github.io/tum-events-sync/tum-events.ics` |
| TUM CHN Events for Freshers | https://chn.tum.de/events/events-for-freshers | `https://anilaladag.github.io/tum-events-sync/tum-events-for-freshers.ics` |

The site has no list-level calendar feed, only one ICS file per event. A GitHub
Actions job runs every 6 hours: it reads the list pages, downloads each event's
ICS file, merges them per list and publishes the result on GitHub Pages.

Events that have already ended stay in the calendar. Events that disappear from
the site before they happen are treated as cancelled and removed.

## Subscribe (Apple Calendar)

1. Calendar on the Mac → **File → New Calendar Subscription…**
2. Paste one of the URLs above.
3. Set **Location: iCloud** (so it shows up on iPhone too) and **Auto-refresh: Every hour**.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
.venv/bin/python -m tum_events_sync --state state/events.json --out public
```

## Notes

- No secrets are needed; the workflow only uses the automatic `GITHUB_TOKEN`.
- A run aborts without changing anything if a list comes back empty or more
  than 30% of event downloads fail; GitHub then emails a failure notice.
- GitHub pauses scheduled workflows in repos without activity for 60 days;
  re-enable it from the Actions tab if that happens.
