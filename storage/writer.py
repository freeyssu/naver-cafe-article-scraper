import re
import pandas as pd
from pathlib import Path
from typing import List
from datetime import datetime

from config import settings
from scraper.article_parser import Article


def save_articles(articles: List[Article], suffix: str = "") -> Path:
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"articles_{timestamp}{suffix}"
    ext = settings.output_format.lower()

    if ext == "csv":
        path = output_dir / f"{filename}.csv"
        _save_csv(articles, path)
    elif ext == "json":
        path = output_dir / f"{filename}.json"
        _save_json(articles, path)
    elif ext in ("xlsx", "excel"):
        path = output_dir / f"{filename}.xlsx"
        _save_excel(articles, path)
    elif ext == "md":
        path = output_dir / f"{filename}.md"
        _save_markdown(articles, path)
    else:
        path = output_dir / f"{filename}.csv"
        _save_csv(articles, path)

    print(f"Saved {len(articles)} articles to {path}")
    return path


def _save_csv(articles: List[Article], path: Path) -> None:
    data = [a.model_dump() for a in articles]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def _save_json(articles: List[Article], path: Path) -> None:
    data = [a.model_dump() for a in articles]
    df = pd.DataFrame(data)
    df.to_json(path, orient="records", force_ascii=False, indent=2)


def _save_excel(articles: List[Article], path: Path) -> None:
    data = [a.model_dump() for a in articles]
    df = pd.DataFrame(data)
    df.to_excel(path, index=False, engine="openpyxl")


def _extract_article_id(url: str) -> str:
    m = re.search(r"articleid=(\d+)", url)
    return m.group(1) if m else ""


def _save_markdown(articles: List[Article], path: Path) -> None:
    lines: List[str] = []
    for article in articles:
        article_id = _extract_article_id(article.url)
        date_str = (
            article.published_at.strftime("%Y-%m-%d %H:%M")
            if article.published_at else ""
        )
        lines.append(
            "## {article_id}, {published_at}, {title}".format(
                article_id=article_id,
                published_at=date_str,
                title=article.title,
            )
        )
        lines.append("")
        lines.append("```")
        lines.append(article.content)
        lines.append("```")
        lines.append("")
        lines.append("-" * 75)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")