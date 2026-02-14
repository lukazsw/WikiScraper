from __future__ import annotations

import sys

from src.wikiscraper.app import WikiScraperApp
from src.wikiscraper.cli import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    app = WikiScraperApp()
    return app.run(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))