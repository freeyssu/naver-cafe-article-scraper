import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from config import settings
from utils.browser import create_driver
from auth.naver_login import NaverAuth
from scraper.collector import run_collection


def parse_args():
    parser = argparse.ArgumentParser(description="Naver Cafe Article Collector")
    parser.add_argument("--login", action="store_true", help="Open browser for manual login + save cookies")
    parser.add_argument("--cafe", type=str, help="Cafe name (overrides config)")
    parser.add_argument("--cafe-id", type=int, help="Cafe ID (overrides config)")
    parser.add_argument("--menu-id", type=int, help="Menu/Board ID (overrides config)")
    parser.add_argument("--start-page", type=int, default=1, help="Starting page number (default: 1)")
    parser.add_argument("--pages", type=int, help="Max pages to scrape (overrides config)")
    parser.add_argument("--format", type=str, default="md", choices=["csv", "json", "xlsx", "md"], help="Output format (default: md)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads for parallel scraping (default: 10)")
    return parser.parse_args()


def validate_cafe_settings():
    errors = []
    if not settings.cafe_name:
        errors.append("CAFE_NAME")
    if not settings.cafe_id:
        errors.append("CAFE_ID")
    if not settings.menu_id:
        errors.append("MENU_ID")
    if errors:
        print("Missing cafe settings: {0}".format(", ".join(errors)))
        print("Set them in .env or use --cafe, --cafe-id, --menu-id flags")
        sys.exit(1)


def do_login() -> None:
    driver = create_driver()
    auth = NaverAuth(driver)
    try:
        if not auth.login():
            print("Login failed.")
            sys.exit(1)
    finally:
        driver.quit()


def do_scrape(args) -> None:
    validate_cafe_settings()
    run_collection(
        max_pages=args.pages,
        num_threads=args.threads,
        start_page=args.start_page,
    )


def main():
    args = parse_args()

    if args.cafe:
        settings.cafe_name = args.cafe
    if args.cafe_id:
        settings.cafe_id = args.cafe_id
    if args.menu_id:
        settings.menu_id = args.menu_id
    if args.format:
        settings.output_format = args.format

    if args.login:
        do_login()
        print("Login successful!")
        return

    do_scrape(args)


if __name__ == "__main__":
    main()
