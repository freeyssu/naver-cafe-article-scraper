import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional

from config import settings
from scraper.article_parser import Article
from scraper.article_list import SessionExpired, _is_login_page, _is_login_url


def fetch_article(session: requests.Session, url: str) -> Optional[Article]:
    r = session.get(url, headers={
        "Referer": f"https://cafe.naver.com/{settings.cafe_name}/",
    }, timeout=15)
    if r.status_code != 200:
        return None

    if _is_login_url(r.url):
        raise SessionExpired(
            "Session expired — redirected to login page"
        )

    soup = BeautifulSoup(r.text, "lxml")

    title = _extract_text(soup, "span.b.m-tcol-c")
    content = _extract_content(soup)
    author = _extract_text(soup, "td.b.nick")
    date = _extract_date(soup)
    view_count = _extract_views(soup)

    if not title and not content:
        if _is_login_page(soup):
            raise SessionExpired(
                "Session expired — login page returned instead of article"
            )
        return None

    return Article(
        url=url,
        title=title or "",
        content=content or "",
        author=author or "",
        published_at=date,
        cafe_name=settings.cafe_name,
        view_count=view_count,
    )


def _extract_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None


def _extract_content(soup: BeautifulSoup) -> Optional[str]:
    container = soup.select_one(".se-main-container")
    if not container:
        return None

    parts = []
    for p in container.select(".se-module-text p.se-text-paragraph"):
        txt = p.get_text(strip=True)
        if txt:
            parts.append(txt)
    return "\n".join(parts) if parts else None


def _extract_date(soup: BeautifulSoup) -> Optional[datetime]:
    el = soup.select_one("td.date")
    if not el:
        return None
    date_text = el.get_text(strip=True)
    patterns = [
        ("%Y.%m.%d. %H:%M",),
        ("%Y.%m.%d. %p %I:%M",),
        ("%Y-%m-%d %H:%M:%S",),
    ]
    for fmt in patterns:
        try:
            return datetime.strptime(date_text, fmt[0])
        except ValueError:
            continue
    return None


def _extract_views(soup: BeautifulSoup) -> Optional[int]:
    el = soup.select_one(".reply-box")
    if el:
        text = el.get_text(strip=True)
        m = re.search(r"조회수([\d,]+)", text)
        if m:
            return int(m.group(1).replace(",", ""))
    return None
