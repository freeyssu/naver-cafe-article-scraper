import requests
from bs4 import BeautifulSoup
from config import settings


class SessionExpired(Exception):
    """Raised when the Naver session cookie is no longer valid."""


def create_session() -> requests.Session:
    import pickle
    from pathlib import Path

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    })

    cookie_path = settings.cookie_path
    if cookie_path.exists():
        with open(cookie_path, "rb") as f:
            cookies = pickle.load(f)
        for c in cookies:
            if c.get("domain") and ".naver.com" in c.get("domain", ""):
                session.cookies.set(
                    c["name"], c["value"],
                    domain=c["domain"],
                    path=c.get("path", "/")
                )
    return session


def get_article_links(
    session: requests.Session,
    page: int = 1,
    user_display: int = 50,
) -> list[dict]:
    url = (
        f"https://cafe.naver.com/{settings.cafe_name}"
        f"/ArticleList.nhn?search.clubid={settings.cafe_id}"
        f"&search.menuid={settings.menu_id}"
        f"&search.page={page}&userDisplay={user_display}"
    )

    r = session.get(url, headers={"Referer": f"https://cafe.naver.com/{settings.cafe_name}/"}, timeout=15)
    r.raise_for_status()

    if _is_login_url(r.url):
        raise SessionExpired(
            "Session expired — redirected to login page"
        )

    soup = BeautifulSoup(r.text, "lxml")

    links = soup.select("a.article")
    if not links:
        if _is_login_page(soup):
            raise SessionExpired(
                "Session expired — login page returned instead of article list"
            )
        return []

    result = []
    for a in links:
        href = a.get("href", "")
        if href and "/ArticleRead.nhn" in href:
            full_url = f"https://cafe.naver.com/{settings.cafe_name}{href}"
            article_id = _extract_article_id(href)
            result.append({"url": full_url, "article_id": article_id})

    return result


def _is_login_url(url: str) -> bool:
    return "nid.naver.com" in url or "/login" in url.lower()


def _is_login_page(soup: BeautifulSoup) -> bool:
    indicators = [
        ".btn_login",
        "#login_form",
        "#log.login",
        ".login_btn",
        "#login_popup",
        "#frmNIDLogin",
        "#naverIdLogin",
        ".login_form_wrap",
        "input#id",
        "input#pw",
    ]
    for sel in indicators:
        if soup.select_one(sel):
            return True

    title_tag = soup.select_one("title")
    if title_tag and "로그인" in title_tag.get_text():
        return True

    return False


def _extract_article_id(href: str) -> str:
    import re
    m = re.search(r"articleid=(\d+)", href)
    return m.group(1) if m else ""
