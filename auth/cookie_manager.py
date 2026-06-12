import pickle
import time
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver

from config import settings


def save_cookies(driver: WebDriver, path: Path | None = None) -> None:
    if path is None:
        path = settings.cookie_path
    path.parent.mkdir(parents=True, exist_ok=True)
    cookies = driver.get_cookies()
    naver_cookies = [c for c in cookies if ".naver.com" in c.get("domain", "")]
    with open(path, "wb") as f:
        pickle.dump(naver_cookies, f)


def load_cookies(driver: WebDriver, path: Path | None = None) -> bool:
    if path is None:
        path = settings.cookie_path
    if not path.exists():
        return False
    try:
        with open(path, "rb") as f:
            cookies = pickle.load(f)
        driver.get("https://www.naver.com")
        for cookie in cookies:
            if "expiry" in cookie:
                del cookie["expiry"]
            driver.add_cookie(cookie)
        return True
    except Exception:
        return False


def is_cookie_expired(path: Path | None = None) -> bool:
    if path is None:
        path = settings.cookie_path
    if not path.exists():
        return True
    try:
        with open(path, "rb") as f:
            cookies = pickle.load(f)
        now = time.time()
        for c in cookies:
            if c.get("expiry") and c["expiry"] < now:
                return True
        return False
    except Exception:
        return True