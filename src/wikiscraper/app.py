from __future__ import annotations

from dataclasses import dataclass

from .fetcher import PageFetcher
from .parser import ArticleParser
from .csv_writer import write_csv
from .table_extractor import TableExtractor
from .utils import sanitize_filename


@dataclass(frozen=True)
class Config:
    base_url: str = "https://bulbapedia.bulbagarden.net/wiki/"


class WikiScraperApp:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.fetcher = PageFetcher(self.config.base_url)
        self.parser = ArticleParser()
        self.table_extractor = TableExtractor()

    def run(self, args) -> int:
        if args.summary:
            return self._run_summary(args.search_phrase, args.html_file)
        if args.table is not None:
            return self._run_table(args.search_phrase, args.table, args.html_file)
        if args.count_words:
            raise NotImplementedError("--count-words not implemented yet")
        if args.analyze_relative_word_frequency:
            raise NotImplementedError("--analyze-relative-word-frequency not implemented yet")
        if args.auto_count_words is not None:
            raise NotImplementedError("--auto-count-words not implemented yet")

        return 0

    def _run_summary(self, search_phrase: str, html_file: str | None = None) -> int:
        try:
            if html_file:
                result = self.fetcher.read_html_file(html_file)
            else:
                result = self.fetcher.fetch_article_html(search_phrase)
        except FileNotFoundError as e:
            print(str(e))
            return 2
        except Exception as e:
            print(f"Failed to fetch page: {e}")
            return 3

        try:
            paragraph = self.parser.extract_first_paragraph(result.html)
        except Exception as e:
            print(f"Failed to parse summary: {e}")
            return 4

        print(paragraph)
        print()
        print("Source: Bulbapedia (content may be under CC BY-NC-SA).")
        print(f"URL: {result.final_url}")
        return 0
    
    def _run_table(self, search_phrase: str, table_number: int, html_file: str | None) -> int:
        try:
            if html_file:
                result = self.fetcher.read_html_file(html_file)
            else:
                result = self.fetcher.fetch_article_html(search_phrase)
        except FileNotFoundError as e:
            print(str(e))
            return 2
        except Exception as e:
            print(f"Failed to fetch page: {e}")
            return 3

        try:
            table = self.table_extractor.extract_nth_table(result.html, table_number)
        except Exception as e:
            print(f"Failed to extract table: {e}")
            return 4

        filename = f"{sanitize_filename(search_phrase)}.csv"
        try:
            write_csv(filename, table.rows)
        except Exception as e:
            print(f"Failed to write CSV: {e}")
            return 5

        print(f"Saved table {table_number} to: {filename}")
        return 0