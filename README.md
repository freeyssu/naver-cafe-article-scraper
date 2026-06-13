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
- **Menu listing** — browse all boards in a cafe
- **Auto cafe ID resolution** — no need to look up numeric cafe ID manually

## Quick Start

```bash
pip install -r requirements.txt
```

### 1. Login (one-time)

```bash
python main.py login
```

Complete 2FA in the browser window. Cookies saved automatically.

### 2. List cafe menus/boards

```bash
python main.py list-menus --cafe CAFE_NAME
```

### 3. Scrape articles

```bash
python main.py scrape --cafe CAFE_NAME --menu-id MENU_ID \
    --max-pages 10 --threads 10
```

## CLI

| Command | Description |
|---------|-------------|
| `login` | Open browser for manual login + save cookies |
| `list-menus --cafe NAME` | List all boards with name and ID |
| `scrape [flags]` | Scrape articles from a board |

### scrape flags

| Flag | Default | Description |
|------|---------|-------------|
| `--cafe NAME` | (from .env) | Cafe name |
| `--menu-id ID` | (from .env) | Menu/Board ID |
| `--start-page N` | 1 | Starting page number |
| `--max-pages N` | 1 | Max pages to scrape |
| `--min-delay N` | 2.0 | Min delay between requests (seconds) |
| `--max-delay N` | 5.0 | Max delay between requests (seconds) |
| `--threads N` | 10 | Parallel threads |
| `--format {csv,json,xlsx,md}` | md | Output format |

## Config

Copy `.env.example` to `.env`:

```
CAFE_NAME=joonggonara
MENU_ID=335
MAX_PAGES=50
OUTPUT_FORMAT=md
MIN_DELAY=2
MAX_DELAY=5
```

All fields are optional — use CLI flags instead. Cafe ID is auto-resolved
from the cafe name.
