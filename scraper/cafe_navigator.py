import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup

from config import settings
from utils.helpers import random_delay


def get_article_links(driver: WebDriver, page: int) -> list[str]:
    url = settings.board_url.format(page=page)
    driver.get(url)
    time.sleep(1)

    try:
        driver.switch_to.frame("cafe_main")
    except Exception:
        pass

    soup = BeautifulSoup(driver.page_source, "lxml")
    links = []
    for a in soup.select("a.article"):
        href = a.get("href", "")
        if href and "/ArticleRead.nhn" in href:
            full_url = f"https://cafe.naver.com{href}"
            links.append(full_url)

    driver.switch_to.default_content()
    return links


def get_article_links_with_retry(
    driver: WebDriver, page: int, max_retries: int = 3
) -> list[str]:
    for attempt in range(max_retries):
        try:
            return get_article_links(driver, page)
        except Exception as e:
            if attempt < max_retries - 1:
                random_delay(settings.min_delay, settings.max_delay)
            else:
                raise e
    return []