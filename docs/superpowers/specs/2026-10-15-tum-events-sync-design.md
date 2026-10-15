# TUM CHN events sync — design

## Goal
Keep every event from https://chn.tum.de/events and
https://chn.tum.de/events/events-for-freshers in Apple Calendar (iCloud)
automatically, via two subscribable ICS feeds.

## Source facts
- No list-level ICS/JSON/RSS feed exists (list pages with `type=1600` → HTTP 500).
- Each event page exposes an ICS file:
  `https://chn.tum.de/event/event/<slug>?tx_calendarize_calendar%5Bformat%5D=ics&type=1600`
  with a stable `UID:calendarize-<slug>`.
- Lists paginate with `?tx_solrevents%5Bpage%5D=N`; event links look like
  `https://chn.tum.de/event/event/<slug>`.
- Events may appear in both lists.

## Output
- `tum-events.ics` and `tum-events-for-freshers.ics`, each mirroring its list
  (overlap allowed), published on GitHub Pages:
  `https://anilaladag.github.io/tum-events-sync/<feed>.ics`.

## Retention
Per feed:
- seen this run → upsert;
- not seen, start in the past → keep;
- not seen, start in the future → drop (treated as cancelled).

## Components
| Module | Responsibility |
|---|---|
| `config.py` | feed names → list URLs, HTTP settings |
| `scrape.py` | collect event URLs from a list, following pagination |
| `fetch.py` | download one event's ICS, return its VEVENTs |
| `state.py` | load/save `state/events.json` |
| `reconcile.py` | pure retention logic |
| `build.py` | render one VCALENDAR per feed |
| `__main__.py` | orchestration + safety guards |

## Safety
- Abort without writing if a list yields 0 events or >30% of ICS fetches fail.
- A single failed event keeps its previous stored copy.

## Automation
GitHub Actions every 6 h (+ manual trigger): run, commit `state/events.json`
if changed, deploy `public/` to Pages. No secrets; only the automatic
`GITHUB_TOKEN` with minimal permissions.

## Public-repo hygiene
No credentials needed. `.gitignore` excludes env/key files and `public/`.
Commits use the GitHub noreply address. Secret-pattern scan before each push.
