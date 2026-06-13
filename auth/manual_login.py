from utils.browser import create_driver
from auth.naver_login import NaverAuth


def manual_login() -> bool:
    driver = create_driver()
    auth = NaverAuth(driver)
    try:
        return auth.login(force_manual=True)
    finally:
        driver.quit()
