from tum_events_sync.scrape import list_event_urls, page_url, parse_event_urls

BASE = "https://chn.tum.de/events"


def test_parse_event_urls_returns_absolute_unique_urls(fixture_text):
    urls = parse_event_urls(fixture_text("events_p1.html"), BASE)
    assert len(urls) == 10
    assert len(set(urls)) == 10
    assert all(u.startswith("https://chn.tum.de/event/event/") for u in urls)
    assert all("?" not in u for u in urls)


def test_parse_event_urls_empty_page(fixture_text):
    assert parse_event_urls(fixture_text("events_p4.html"), BASE) == []


def test_parse_event_urls_freshers(fixture_text):
    urls = parse_event_urls(fixture_text("freshers_p1.html"), BASE)
    assert len(urls) == 9
    assert (
        "https://chn.tum.de/event/event/europe-germany-and-heilbronn-a-historical-and-cultural-journey-of-discovery"
        in urls
    )


def test_page_url():
    assert page_url(BASE, 1) == BASE
    assert page_url(BASE, 3) == BASE + "?tx_solrevents%5Bpage%5D=3"


def test_list_event_urls_follows_pages_until_empty(fixture_text):
    pages = {
        page_url(BASE, 1): fixture_text("events_p1.html"),
        page_url(BASE, 2): fixture_text("events_p3.html"),
        page_url(BASE, 3): fixture_text("events_p4.html"),
    }
    requested = []

    def get(url):
        requested.append(url)
        return pages[url]

    urls = list_event_urls(BASE, get)
    assert len(urls) == 19  # 10 + 9 on the last non-empty page
    assert requested == [page_url(BASE, n) for n in (1, 2, 3)]


def test_list_event_urls_stops_when_page_repeats(fixture_text):
    # A site that ignores the page parameter must not loop forever.
    html = fixture_text("freshers_p1.html")
    calls = []

    def get(url):
        calls.append(url)
        return html

    assert len(list_event_urls(BASE, get)) == 9
    assert len(calls) == 2
