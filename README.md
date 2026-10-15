# TUM Campus Heilbronn events in your calendar

Get every event from the TUM Campus Heilbronn website in your iPhone and Mac
calendar. The calendar keeps itself up to date, so you only set it up once.

There are two calendars. Add one or both:

| Calendar | What's in it | Link to copy |
|---|---|---|
| **TUM CHN Events** | Everything on [chn.tum.de/events](https://chn.tum.de/events) | `https://anilaladag.github.io/tum-events-sync/tum-events.ics` |
| **TUM CHN Events for Freshers** | Everything on [chn.tum.de/events/events-for-freshers](https://chn.tum.de/events/events-for-freshers) | `https://anilaladag.github.io/tum-events-sync/tum-events-for-freshers.ics` |

> This is an unofficial, student-made project. It is not run by TUM.
> If an event looks wrong, check the event page on chn.tum.de, which every
> calendar entry links to.

---

## Setup

Do **either** the Mac steps **or** the iPhone steps, not both, otherwise
every event shows up twice. If you have a Mac, use the Mac steps: the calendar
then appears on your iPhone too, and you can choose how often it refreshes.

### On a Mac (recommended, also puts it on your iPhone)

1. Open the **Calendar** app.
2. In the menu bar, click **File → New Calendar Subscription…**
3. Paste one of the links from the table above and click **Subscribe**.
4. In the window that opens:
   - **Name:** leave it, or type your own.
   - **Color:** pick any color you like.
   - **Location:** choose **iCloud**. ⚠️ This is the important one: if you
     pick "On My Mac", the calendar will not appear on your iPhone.
   - **Auto-refresh:** choose **Every hour**.
5. Click **OK**.
6. Want both calendars? Repeat steps 2–5 with the second link.

After a minute or so the calendar also shows up on your iPhone (Calendar app →
**Calendars** at the bottom). If it doesn't, check that iCloud Calendar is on:
iPhone **Settings → [your name] → iCloud → Calendars**.

### On an iPhone only (no Mac)

1. Copy one of the links from the table above.
2. Open **Settings → Apps → Calendar → Calendar Accounts → Add Account**.
   (On iOS 17 and older: **Settings → Calendar → Accounts → Add Account**.)
3. Tap **Other → Add Subscribed Calendar**.
4. Paste the link into **Server** and tap **Next**.
5. Tap **Save**.
6. Want both calendars? Repeat with the second link.

### Other calendar apps

- **Google Calendar:** on a computer go to calendar.google.com → **+** next
  to "Other calendars" → **From URL** → paste the link. Google refreshes it
  roughly once or twice a day.
- **Outlook:** **Add calendar → Subscribe from web** → paste the link.

---

## How often does it update?

Two steps happen before a new event shows up in your calendar:

1. **The bot copies the website every 6 hours.** It runs four times a day,
   at about **02:17, 08:17, 14:17 and 20:17 German time**. In winter
   (standard time) that's 01:17, 07:17, 13:17 and 19:17. GitHub sometimes
   starts it 5–30 minutes late.
2. **Your calendar app downloads the new version.**
   - Mac: as often as you set under **Auto-refresh**. "Every hour" is
     recommended. To change it later, right-click the calendar →
     **Get Info**.
   - iPhone-only setup: iOS decides when to refresh.

So a new event normally appears in your calendar **within about 7 hours**
(6 hours for the bot, plus up to 1 hour for your Mac).

## What happens when events change?

- **New event on the website:** it shows up in your calendar after the next update.
- **Event time or details changed:** your calendar shows the new version.
- **Event cancelled or removed before it happens:** it disappears from your calendar.
- **Event already happened:** it stays in your calendar, so you can look back.
- **Event listed in both calendars:** some events appear on both website pages.
  If you add both calendars, you'll see these events twice, once in each color.

## Removing a calendar

- **Mac:** in the Calendar sidebar, right-click the calendar → **Unsubscribe**.
- **iPhone-only setup:** **Settings → Apps → Calendar → Calendar Accounts** → tap
  the subscription → **Delete Account**.

---

## How it works (for the curious)

The website has no single calendar feed; each event has its own calendar file.
A GitHub Actions job (`.github/workflows/sync.yml`) runs every 6 hours. It reads
both event lists, downloads every event's calendar file, merges them into the
two calendars above and publishes them with GitHub Pages.

- **Schedule:** the timing is the `cron: "17 */6 * * *"` line in
  `.github/workflows/sync.yml`. Change `*/6` to change the interval in hours.
- **Run it now:** go to **Actions → sync → Run workflow**.
- **If something breaks:** if the website is down or returns no events, the bot
  changes nothing and keeps the last good calendars online. GitHub emails the
  repo owner about the failed run.
- **No secrets:** the bot needs no passwords or tokens. It only reads a public
  website.
- **If the schedule stops:** GitHub pauses scheduled jobs in repositories with
  no activity for 60 days. If the calendars stop updating, re-enable the job
  from the **Actions** tab.
