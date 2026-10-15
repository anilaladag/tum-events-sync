from collections.abc import Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .config import MAX_PAGES

EVENT_PATH = "/event/event/"


def page_url(list_url: str, page: int) -> str:
    if page == 1:
        return list_url
    return f"{list_url}?tx_solrevents%5Bpage%5D={page}"


def parse_event_urls(html: str, base_url: str) -> list[str]:
    """Event detail URLs from the list items of one list page, in page order."""
    soup = BeautifulSoup(html, "html.parser")
    urls: dict[str, None] = {}
    for item in soup.select("article.c-events-solr-list__item"):
        for link in item.select(f'a[href*="{EVENT_PATH}"]'):
            url = urljoin(base_url, link["href"]).split("?")[0].split("#")[0]
            urls[url] = None
    return list(urls)


def list_event_urls(list_url: str, get: Callable[[str], str]) -> list[str]:
    """All event URLs of a list, following pagination until a page adds nothing new."""
    urls: dict[str, None] = {}
    for page in range(1, MAX_PAGES + 1):
        found = parse_event_urls(get(page_url(list_url, page)), list_url)
        new = [u for u in found if u not in urls]
        if not new:
            break
        urls.update(dict.fromkeys(new))
    return list(urls)
