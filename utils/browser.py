import os
import ssl
import certifi
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def create_driver() -> webdriver.Chrome:
    # Fix SSL certificate issue on macOS
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ["SSL_CERT_FILE"] = certifi.where()

    # Try to install chromedriver, skip if already installed
    try:
        chromedriver_autoinstaller.install()
    except Exception:
        pass

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=ko_KR")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.implicitly_wait(10)
    return driver


def restart_driver(driver: webdriver.Chrome) -> webdriver.Chrome:
    try:
        driver.quit()
    except Exception:
        pass
    return create_driver()