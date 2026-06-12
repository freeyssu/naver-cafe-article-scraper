import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from auth.cookie_manager import save_cookies, load_cookies


class NaverAuth:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def login(self, force_manual: bool = False) -> bool:
        if not force_manual:
            if load_cookies(self.driver):
                if self._verify_session():
                    print("Restored session from cookies")
                    return True

        return self._manual_login()

    def _manual_login(self) -> bool:
        self.driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)

        print("\n" + "=" * 50)
        print("MANUAL LOGIN MODE")
        print("=" * 50)
        print("1. Login with your ID/PW in the browser")
        print("2. Complete 2FA if prompted")
        print("3. Wait until you see the Naver homepage")
        print("=" * 50)
        print("Waiting for login... (checking every 3s, max 3 min)")

        logged_in = self._wait_for_login(timeout=180)

        if logged_in:
            save_cookies(self.driver)
            print("Login successful! Cookies saved.")
            return True

        print("Login timed out or failed.")
        return False

    def _wait_for_login(self, timeout: int = 180) -> bool:
        start = time.time()
        check_count = 0
        while time.time() - start < timeout:
            check_count += 1
            elapsed = int(time.time() - start)

            current_url = self.driver.current_url

            if "nid.naver.com" not in current_url and "naver.com" in current_url:
                time.sleep(2)
                if self._verify_session():
                    return True

            if check_count % 10 == 0:
                print("  Still waiting... ({0}s / {1}s)".format(elapsed, timeout))

            time.sleep(3)

        return False

    def _verify_session(self) -> bool:
        current_url = self.driver.current_url

        if "www.naver.com" not in current_url:
            self.driver.get("https://www.naver.com")
            time.sleep(3)

        for btn in self.driver.find_elements(By.CSS_SELECTOR, "a.btn_login"):
            try:
                if btn.is_displayed():
                    return False
            except Exception:
                pass

        return True
