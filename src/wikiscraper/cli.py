from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki_scraper",
        description="WikiScraper - CLI tool for scraping Bulbapedia pages.",
    )
    parser.add_argument(
        "search_phrase",
        help="Search phrase used to find the wiki article (quotes recommended).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--summary", action="store_true", help="Print first paragraph summary.")
    mode.add_argument("--table", type=int, help="Extract N-th table and save as CSV.")
    mode.add_argument("--count-words", action="store_true", help="Update word-counts.json for article.")
    mode.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true",
        help="Compare article word frequency with language frequency.",
    )
    mode.add_argument(
        "--auto-count-words",
        type=int,
        metavar="DEPTH",
        help="Recursively count words on linked articles up to depth DEPTH.",
    )
    mode.add_argument(
        "--chart",
        action="store_true",
        help="Generate a bar chart for relative word frequency analysis.",
    )
    parser.add_argument(
        "--first-row-is-header",
        action="store_true",
        help="Treat first row of extracted table as header row.",
    )
    parser.add_argument(
        "--mode",
        choices=["article", "language"],
        default="article",
        help="Sorting mode for relative frequency analysis.",
    )
    parser.add_argument("--n", type=int, default=20, help="Number of top words to display in frequency analysis.")
    parser.add_argument("--wait", type=float, default=0.0, help="Delay between requests in auto mode (seconds).")
    parser.add_argument(
        "--html-file",
        type=str,
        default=None,
        help="Optional path to a local HTML file (offline mode for testing).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=200,
        help="Maximum number of pages to visit in --auto-count-words.",
    )
    return parser