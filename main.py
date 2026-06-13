import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from config import settings
from utils.browser import create_driver
from auth.manual_login import manual_login
from auth.naver_login import NaverAuth
from scraper.collector import run_collection
from scraper.menu_list import list_menus, resolve_cafe_id
from scraper.article_list import create_session, SessionExpired


def parse_args():
    parser = argparse.ArgumentParser(
        description="Naver Cafe Article Collector"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # login
    subparsers.add_parser(
        "login", help="Open browser for manual login + save cookies"
    )

    # list-menus
    list_parser = subparsers.add_parser(
        "list-menus", help="List all available menus/boards in the cafe"
    )
    list_parser.add_argument(
        "--cafe", type=str, required=True, help="Cafe name"
    )
    # scrape
    scrape_parser = subparsers.add_parser(
        "scrape", help="Scrape articles from a cafe board"
    )
    scrape_parser.add_argument(
        "--cafe", type=str, help="Cafe name (overrides config)"
    )
    scrape_parser.add_argument(
        "--menu-id", type=int, help="Menu/Board ID (overrides config)"
    )
    scrape_parser.add_argument(
        "--start-page", type=int, default=1,
        help="Starting page number (default: 1)"
    )
    scrape_parser.add_argument(
        "--max-pages", type=int, default=1,
        help="Max pages to scrape (default: 1)"
    )
    scrape_parser.add_argument(
        "--format", type=str, default="md",
        choices=["csv", "json", "xlsx", "md"],
        help="Output format (default: md)"
    )
    scrape_parser.add_argument(
        "--min-delay", type=float, default=None,
        help="Min delay between requests in seconds (default: 2.0)"
    )
    scrape_parser.add_argument(
        "--max-delay", type=float, default=None,
        help="Max delay between requests in seconds (default: 5.0)"
    )
    scrape_parser.add_argument(
        "--threads", type=int, default=10,
        help="Number of threads for parallel scraping (default: 10)"
    )

    return parser.parse_args()


def validate_cafe_settings():
    errors = []
    if not settings.cafe_name:
        errors.append("CAFE_NAME")
    if not settings.menu_id:
        errors.append("MENU_ID")
    if errors:
        print(
            "Missing cafe settings: {0}".format(", ".join(errors))
        )
        print(
            "Set them in .env or use --cafe, --menu-id flags"
        )
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


def do_list_menus() -> None:
    if not settings.cookie_path.exists():
        print("No saved cookies found. Opening browser for login...")
        if not manual_login():
            print("Login failed. Cannot list menus without authentication.")
            sys.exit(1)

    session = create_session()
    try:
        menus = list_menus(session)
    except SessionExpired:
        print("Session expired. Re-logging in...")
        if not manual_login():
            print("Login failed.")
            sys.exit(1)
        session = create_session()
        menus = list_menus(session)

    if not menus:
        print("No menus found.")
        return

    print("")
    print(
        "Available menus for {cafe} (clubid={id}):".format(
            cafe=settings.cafe_name, id=settings.cafe_id
        )
    )
    print(
        "  {:<6} {:<28} {}".format("ID", "Name", "Articles")
    )
    print(
        "  {:<6} {:<28} {}".format("-" * 4, "-" * 28, "-" * 7)
    )
    for m in menus:
        count_str = "{:,}".format(m.article_count) if m.article_count else "-"
        print("  {:<6} {:<28} {}".format(m.menu_id, m.menu_name, count_str))
    print("")


def do_scrape(args) -> None:
    validate_cafe_settings()
    run_collection(
        max_pages=args.max_pages,
        num_threads=args.threads,
        start_page=args.start_page,
    )


def main():
    args = parse_args()

    if args.command == "login":
        do_login()
        print("Login successful!")
        return

    if args.command == "list-menus":
        settings.cafe_name = args.cafe
        print("Resolving cafe ID from name...")
        session = create_session()
        settings.cafe_id = resolve_cafe_id(session, args.cafe)
        print(
            "Resolved cafe ID: {cafe_id}".format(cafe_id=settings.cafe_id)
        )
        do_list_menus()
        return

    if args.command == "scrape":
        if args.cafe is not None:
            settings.cafe_name = args.cafe
        if args.menu_id is not None:
            settings.menu_id = args.menu_id
        if args.min_delay is not None:
            settings.min_delay = args.min_delay
        if args.max_delay is not None:
            settings.max_delay = args.max_delay
        if not settings.cafe_id and settings.cafe_name:
            print("Resolving cafe ID from name...")
            session = create_session()
            settings.cafe_id = resolve_cafe_id(session, settings.cafe_name)
            print(
                "Resolved cafe ID: {cafe_id}".format(cafe_id=settings.cafe_id)
            )
        settings.output_format = args.format
        do_scrape(args)
        return


if __name__ == "__main__":
    main()
