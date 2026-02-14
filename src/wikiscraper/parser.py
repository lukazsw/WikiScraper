from __future__ import annotations

from bs4 import BeautifulSoup


class ArticleParser:
    def extract_first_paragraph(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        content = soup.select_one("#mw-content-text")
        if content is None:
            raise ValueError("Could not find main content container (#mw-content-text).")

        for p in content.find_all("p", recursive=True):
            text = p.get_text(" ", strip=True)
            if not text:
                continue
            if len(text) < 40:
                continue
            return text

        raise ValueError("Could not find a suitable first paragraph in the article.")