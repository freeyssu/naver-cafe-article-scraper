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

Omit `--max-pages` to scrape all pages automatically.

## Formats

| Format | Use case | Included fields |
|--------|----------|-----------------|
| JSON | Downstream apps, scripting | All fields — title, content, author, published_at, scraped_at, view_count, comment_count, url |
| MD | Human reading | Title, author, date, full content |
| CSV / XLSX | Spreadsheet analysis | Same as JSON, flattened |

### Example (joonggonara, menu 1256)

```bash
python main.py scrape --cafe joonggonara --menu-id 1256 --max-pages 1 \
    --min-delay 0.5 --max-delay 1.0 --format json
```

```json
[
  {
    "title": "[공지] 중고차 카테고리 서비스 일시중단 및 개편안내",
    "content": "안녕하세요, 중고나라입니다...",
    "author": "중고나라카페스탭(jn_p****)",
    "published_at": 1781105220000
  },
  ...
]
```

```bash
python main.py scrape --cafe joonggonara --menu-id 1256 --max-pages 1 \
    --min-delay 0.5 --max-delay 1.0 --format md
```

```markdown
## 1130548849, 2026-06-10 15:27, [공지] 중고차 카테고리 서비스 일시중단 및 개편안내

```
안녕하세요, 중고나라입니다...
```
...
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
| `--max-pages N` | 0 (all) | Max pages to scrape (0 = all pages) |
| `--min-delay N` | 2.0 | Min delay between requests (seconds) |
| `--max-delay N` | 5.0 | Max delay between requests (seconds) |
| `--threads N` | 10 | Parallel threads |
| `--format {csv,json,xlsx,md}` | md | Output format (see Formats section) |

## Config

Copy `.env.example` to `.env`:

```
CAFE_NAME=joonggonara
MENU_ID=335
MAX_PAGES=0          # 0 = all pages
OUTPUT_FORMAT=md     # csv, json, xlsx, md
MIN_DELAY=2
MAX_DELAY=5
```

All fields are optional — use CLI flags instead. Cafe ID is auto-resolved
from the cafe name.
