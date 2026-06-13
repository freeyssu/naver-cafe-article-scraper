import math
import re
import threading
import requests
from typing import List
from tqdm import tqdm

from config import settings
from scraper.article_list import create_session, get_article_links, SessionExpired
from scraper.article_reader import fetch_article
from scraper.article_parser import Article
from storage.writer import save_articles
from utils.helpers import random_delay
from auth.manual_login import manual_login

_stop_event = threading.Event()
_login_lock = threading.Lock()


def _collect_pages(
    pages: List[int],
    result_list: List,
    lock: threading.Lock,
    pbar: tqdm,
    article_counter: List[int] | None = None,
) -> None:
    if not pages:
        return

    session = create_session()
    user_display = 50

    for page in pages:
        if _stop_event.is_set():
            return

        page_articles: List[Article] = []
        try:
            links = get_article_links(session, page, user_display)
            if links:
                links.sort(
                    key=lambda x: int(x["article_id"])
                    if x["article_id"].isdigit()
                    else 0,
                    reverse=True,
                )
                for link_info in links:
                    if _stop_event.is_set():
                        return
                    try:
                        article = fetch_article(session, link_info["url"])
                        if article:
                            page_articles.append(article)
                    except (requests.Timeout, requests.ConnectionError):
                        pass
                    except SessionExpired:
                        _stop_event.set()
                        tqdm.write("Session expired — stopping collection")
                        return
                    random_delay(settings.min_delay, settings.max_delay)
        except (requests.Timeout, requests.ConnectionError):
            pass
        except SessionExpired:
            _stop_event.set()
            tqdm.write("Session expired — stopping collection")
            return

        with lock:
            result_list.extend(page_articles)
            if article_counter is not None:
                article_counter[0] += len(page_articles)
                pbar.set_postfix_str(
                    "{n} articles".format(n=article_counter[0])
                )
            else:
                pbar.set_postfix_str(
                    "{n} articles".format(n=len(result_list))
                )
            pbar.update(1)


def _manual_login() -> bool:
    acquired = _login_lock.acquire(blocking=False)
    if not acquired:
        tqdm.write("Another thread is already handling re-login...")
        _login_lock.acquire()
        _login_lock.release()
        return settings.cookie_path.exists()

    try:
        return manual_login()
    finally:
        _login_lock.release()


def _run_collection(
    all_pages: List[int],
    results: List[Article],
    max_pages: int,
    num_threads: int,
) -> None:
    actual_threads = min(num_threads, max_pages)
    chunk_size = math.ceil(max_pages / actual_threads)
    page_chunks = [
        all_pages[i : i + chunk_size] for i in range(0, max_pages, chunk_size)
    ]

    lock = threading.Lock()
    per_chunk_results: List[List[Article]] = [[] for _ in page_chunks]
    article_counter: List[int] = [0]

    with tqdm(total=max_pages, desc="Pages") as pbar:
        if actual_threads <= 1:
            _collect_pages(
                all_pages, results, lock, pbar, article_counter
            )
            return

        def _run_chunk(
            chunk_idx: int,
            chunk_pages: List[int],
        ) -> None:
            local_results: List[Article] = []
            _collect_pages(
                chunk_pages, local_results, lock, pbar, article_counter
            )
            per_chunk_results[chunk_idx] = local_results

        threads = [
            threading.Thread(
                target=_run_chunk, args=(i, chunk)
            )
            for i, chunk in enumerate(page_chunks)
        ]
        for t in threads:
            t.start()
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            _stop_event.set()
            for t in threads:
                t.join(timeout=5)
            pbar.close()
            tqdm.write(
                "\nInterrupted. Collected {n} articles so far.".format(
                    n=sum(len(r) for r in per_chunk_results)
                )
            )

    # merge in page order
    for chunk_results in per_chunk_results:
        results.extend(chunk_results)


def collect_articles(
    max_pages: int | None = None,
    num_threads: int = 1,
    start_page: int = 1,
) -> List[Article]:
    if max_pages is None:
        max_pages = settings.max_pages
    if max_pages < 1:
        return []

    if not settings.cookie_path.exists():
        tqdm.write("No saved cookies found. Opening browser for login...")
        if not _manual_login():
            tqdm.write(
                "Login failed. Proceeding without authentication "
                "- only public articles will be collected."
            )

    tqdm.write(
        "Threads: {threads} | Delay: {min_delay}-{max_delay}s | "
        "Pages: {start}-{end}".format(
            threads=num_threads,
            min_delay=settings.min_delay,
            max_delay=settings.max_delay,
            start=start_page,
            end=start_page + max_pages - 1,
        )
    )

    all_pages = list(range(start_page, start_page + max_pages))
    results: List[Article] = []
    retries = 0

    while retries < 2:
        _stop_event.clear()
        results.clear()
        _run_collection(all_pages, results, max_pages, num_threads)

        if not _stop_event.is_set():
            break

        retries += 1
        if retries < 2:
            tqdm.write("\nSession expired. Re-logging in...")
            _manual_login()
            # recreate session after re-login
            tqdm.write("Re-login complete. Resuming collection...\n")

    # sort all articles by ID descending (newest first)
    results.sort(
        key=lambda a: int(m.group(1))
        if (m := re.search(r"articleid=(\d+)", a.url))
        else 0,
        reverse=True,
    )

    return results


def run_collection(
    max_pages: int | None = None,
    num_threads: int = 1,
    start_page: int = 1,
) -> None:
    articles = collect_articles(max_pages, num_threads, start_page)
    if articles:
        save_articles(articles)
    else:
        print("No articles collected.")
