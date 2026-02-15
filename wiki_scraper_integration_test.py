from __future__ import annotations

import sys
from pathlib import Path

from wiki_scraper import main


def run_test() -> int:
    """
    Integration test:
    - runs CLI in offline mode on a saved HTML file
    - checks that summary contains an expected keyword
    - returns non-zero exit code on failure
    """
    html_path = Path("data/pikachu.html")
    if not html_path.exists():
        print("Missing data/pikachu.html. Create it first.")
        return 2

    # run CLI
    code = main(["Pikachu", "--summary", "--html-file", str(html_path)])
    if code != 0:
        print(f"CLI returned non-zero exit code: {code}")
        return 3

    # Extra check: parse summary directly to validate content deterministically
    # (keeps test robust even if CLI printing format changes a bit)
    from src.wikiscraper.parser import ArticleParser

    html = html_path.read_text(encoding="utf-8", errors="replace")
    summary = ArticleParser().extract_first_paragraph(html)
    if "Pikachu" not in summary:
        print("Summary validation failed: missing 'Pikachu'")
        return 4

    print("Integration test: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_test())
