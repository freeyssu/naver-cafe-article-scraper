# Naver Cafe Article Collector

Collect Naver Cafe articles (title, content, date, author) via HTTP scraping
with manual browser login supporting 2FA.

## Features

- **HTTP-based scraping** (requests + BeautifulSoup) — fast, no browser needed
  for scraping
- **Manual login** with 2FA support (Naver App OTP)
- **Cookie persistence** — login once, reuse session for days/weeks
- **Multi-threaded collection** — configurable parallel page scraping
- **Output formats** — CSV, JSON, Excel, Markdown
- **Session expiry detection** — stops and auto re-logs in when cookie expires

## Quick Start

```bash
pip install -r requirements.txt
```

### 1. Login (one-time)

```bash
python main.py --login
```

Complete 2FA in the browser window. Cookies saved automatically.

### 2. Scrape articles

```bash
python main.py --cafe CAFE_NAME --cafe-id CAFE_ID --menu-id MENU_ID \
    --pages 10 --threads 10
```

## CLI

| Flag | Default | Description |
|------|---------|-------------|
| `--login` | — | Open browser for manual login + save cookies |
| `--cafe NAME` | (from .env) | Cafe name |
| `--cafe-id ID` | (from .env) | Cafe ID |
| `--menu-id ID` | (from .env) | Menu/Board ID |
| `--start-page N` | 1 | Starting page number |
| `--pages N` | 50 | Pages to scrape |
| `--threads N` | 10 | Parallel threads |
| `--format {csv,json,xlsx,md}` | md | Output format |

## Config

Copy `.env.example` to `.env`:

```
CAFE_NAME=joonggonara
CAFE_ID=10050146
MENU_ID=335
MAX_PAGES=50
OUTPUT_FORMAT=md
MIN_DELAY=2
MAX_DELAY=5
```

All fields are optional — use CLI flags instead.
