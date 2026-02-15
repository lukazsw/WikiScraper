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

    def extract_article_text(self, html: str) -> str:
        """
        Extracts main article text from #mw-content-text.
        We remove tables (often infoboxes/charts) to focus on prose.
        """
        soup = BeautifulSoup(html, "lxml")
        content = soup.select_one("#mw-content-text")
        if content is None:
            raise ValueError("Could not find main content container (#mw-content-text).")

        # remove tables (navigation, infobox, charts) from text counting
        for t in content.find_all("table"):
            t.decompose()

        text = content.get_text(" ", strip=True)
        return text
    
    def extract_article_links(self, html: str) -> list[str]:
        """
        Returns list of internal /wiki/... links (titles) from main content.
        We filter out namespaces like File:, Category:, Special:, etc.
        Output is page titles like 'Pikachu' or 'Type' (without '/wiki/').
        """
        soup = BeautifulSoup(html, "lxml")
        content = soup.select_one("#mw-content-text")
        if content is None:
            return []

        titles: list[str] = []
        seen: set[str] = set()

        for a in content.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("/wiki/"):
                continue

            # strip fragment
            href = href.split("#", 1)[0]
            if href == "/wiki/" or href == "/wiki":
                continue

            title = href[len("/wiki/") :]
            # decode percent-encoding (e.g. Pok%C3%A9mon)
            from urllib.parse import unquote
            title = unquote(title)

            # filter namespaces like File:, Category:, Special:, etc.
            if ":" in title:
                continue

            # avoid empty
            title = title.strip()
            if not title:
                continue

            if title not in seen:
                seen.add(title)
                titles.append(title)

        return titles