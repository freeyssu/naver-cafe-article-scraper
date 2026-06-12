# Naver Cafe Article Collector

## Line limit
- Max 150 characters per line
- Keep only major features and important explanations

## Code style
- Max 120 characters per line
- Follow BlackFormatter basic rules
- No f-strings — use .format() style
- Use Pydantic v2 BaseModel for data models

## Project structure
- `auth/` — manual Naver login + cookie management (Selenium)
- `scraper/` — HTTP article collection (requests + BeautifulSoup)
- `storage/` — CSV/JSON/Excel/Markdown output writer
- `utils/` — browser driver, helpers
- `main.py`, `config.py` — entry point and settings

## Key patterns
- Selenium only for login; scraping is HTTP-only (requests + BeautifulSoup)
- Login is always manual (browser) — no auto-fill; user types credentials + 2FA
- Cookies persisted to `data/naver_cookies.pkl`
- Session expiry mid-scrape triggers automatic manual re-login via browser
- Threading via `threading.Thread`; each thread creates its own `requests.Session`
- `--start-page N --pages M` for page range (e.g., `--start-page 1 --pages 10`)
- Session expiry detection via login page HTML indicators
- tqdm progress bar is thread-safe for page-level tracking

## Testing
```bash
python -m py_compile **/*.py
```
