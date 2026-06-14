import re
from typing import List
from requests import Session
from bs4 import BeautifulSoup
from pydantic import BaseModel

from config import settings
from scraper.article_list import SessionExpired, _is_login_url


class MenuInfo(BaseModel):
    menu_id: int
    menu_name: str


def resolve_cafe_id(session: Session, cafe_name: str) -> int:
    url = "https://cafe.naver.com/{cafe}/".format(cafe=cafe_name)
    r = session.get(
        url,
        headers={"Referer": "https://cafe.naver.com/"},
        timeout=15,
    )
    r.raise_for_status()
    m = re.search(r"clubid[=/:](\d+)", r.text)
    if not m:
        raise ValueError(
            "Could not resolve cafe ID from page for '{cafe}'".format(
                cafe=cafe_name
            )
        )
    return int(m.group(1))


def list_menus(session: Session) -> List[MenuInfo]:
    url = "https://cafe.naver.com/{cafe}/".format(
        cafe=settings.cafe_name
    )
    r = session.get(
        url,
        headers={"Referer": "https://cafe.naver.com/"},
        timeout=15,
    )
    r.raise_for_status()

    if _is_login_url(r.url):
        raise SessionExpired(
            "Session expired — redirected to login page"
        )

    soup = BeautifulSoup(r.text, "lxml")
    seen_ids = set()
    menus = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"menuid=(\d+)", href)
        if not m:
            continue
        menu_id = int(m.group(1))
        if menu_id in seen_ids:
            continue
        seen_ids.add(menu_id)

        name = a.get_text(strip=True)

        menus.append(
            MenuInfo(menu_id=menu_id, menu_name=name)
        )

    menus.sort(key=lambda m: m.menu_id)
    return menus
