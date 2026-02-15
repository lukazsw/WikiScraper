from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from pathlib import Path

import requests


@dataclass(frozen=True)
class FetchResult:
    final_url: str
    html: str


class PageFetcher:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def build_article_url(self, search_phrase: str) -> str:
        title = search_phrase.strip().replace(" ", "_")
        title = urllib.parse.quote(title, safe=":/_()'-,")
        return self.base_url + title

    def fetch_article_html(self, search_phrase: str) -> FetchResult:
        url = self.build_article_url(search_phrase)
        resp = requests.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": "WikiScraper/1.0 (Educational project)"},
        )
        if resp.status_code == 404:
            raise FileNotFoundError(f"Article not found for phrase: {search_phrase}")
        resp.raise_for_status()
        return FetchResult(final_url=str(resp.url), html=resp.text)

    def read_html_file(self, html_file: str) -> FetchResult:
        path = Path(html_file)
        if not path.exists():
            raise FileNotFoundError(f"HTML file does not exist: {html_file}")
        html = path.read_text(encoding="utf-8", errors="replace")
        # final_url is unknown in offline mode; keep file path for debugging
        return FetchResult(final_url=str(path.resolve()), html=html)