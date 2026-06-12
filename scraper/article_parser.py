import re
import time
from datetime import datetime
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class Article(BaseModel):
    url: str
    title: str
    content: str
    author: str
    published_at: Optional[datetime] = None
    cafe_name: str = ""
    board_name: str = ""
    view_count: Optional[int] = None
    comment_count: Optional[int] = None
    scraped_at: datetime = Field(default_factory=datetime.now)


def parse_article(driver: WebDriver, url: str) -> Optional[Article]:
    from config import settings

    driver.get(url)
    time.sleep(1)

    try:
        driver.switch_to.frame("cafe_main")
    except Exception:
        pass

    soup = BeautifulSoup(driver.page_source, "lxml")

    title = _extract_title(soup)
    content = _extract_content(soup)
    author = _extract_author(soup)
    published_at = _extract_date(soup)
    view_count = _extract_view_count(soup)

    driver.switch_to.default_content()

    if not title and not content:
        return None

    return Article(
        url=url,
        title=title or "",
        content=content or "",
        author=author or "",
        published_at=published_at,
        cafe_name=settings.cafe_name,
        view_count=view_count,
    )


def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    el = soup.select_one("h3.title_text")
    if el:
        return el.get_text(strip=True)
    el = soup.select_one("h2.title")
    if el:
        return el.get_text(strip=True)
    return None


def _extract_content(soup: BeautifulSoup) -> Optional[str]:
    el = soup.select_one(".se-main-container")
    if el:
        return el.get_text(separator="\n", strip=True)
    el = soup.select_one(".ArticleContentBox .article")
    if el:
        return el.get_text(separator="\n", strip=True)
    return None


def _extract_author(soup: BeautifulSoup) -> Optional[str]:
    el = soup.select_one("button.nickname")
    if el:
        return el.get_text(strip=True)
    el = soup.select_one(".article-info .writer")
    if el:
        return el.get_text(strip=True)
    return None


def _extract_date(soup: BeautifulSoup) -> Optional[datetime]:
    el = soup.select_one("span.date")
    if el:
        date_text = el.get_text(strip=True)
        return _parse_date_string(date_text)
    return None


def _parse_date_string(date_text: str) -> Optional[datetime]:
    patterns = [
        ("%Y.%m.%d. %H:%M", None),
        ("%Y.%m.%d. %p %I:%M", None),
        ("%Y-%m-%d %H:%M:%S", None),
        ("%Y-%m-%d %H:%M", None),
    ]
    for fmt, _ in patterns:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    return None


def _extract_view_count(soup: BeautifulSoup) -> Optional[int]:
    el = soup.select_one(".count")
    if el:
        text = el.get_text(strip=True)
        try:
            return int(re.sub(r"[^\d]", "", text))
        except ValueError:
            pass
    return None