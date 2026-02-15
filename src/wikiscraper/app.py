from __future__ import annotations

from dataclasses import dataclass

from .fetcher import PageFetcher
from .parser import ArticleParser
from .csv_writer import write_csv
from .table_extractor import TableExtractor
from .utils import sanitize_filename
from .word_counting import tokenize, update_counts_file
from .relative_frequency import build_language_reference, compute_relative_freq, sort_relative_df
from .word_counting import load_counts
from .crawler import WikiCrawler

import pandas as pd

from .table_processing import dataframe_to_csv_rows, process_table


@dataclass(frozen=True)
class Config:
    base_url: str = "https://bulbapedia.bulbagarden.net/wiki/"


class WikiScraperApp:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.fetcher = PageFetcher(self.config.base_url)
        self.parser = ArticleParser()
        self.table_extractor = TableExtractor()
        self.crawler = WikiCrawler(self.fetcher, self.parser)

    def run(self, args) -> int:
        if args.summary:
            return self._run_summary(args.search_phrase, args.html_file)
        if args.table is not None:
            self._first_row_is_header = args.first_row_is_header
            return self._run_table(args.search_phrase, args.table, args.html_file)
        if args.count_words:
            return self._run_count_words(args.search_phrase, args.html_file)
        if args.analyze_relative_word_frequency:
            return self._run_relative_freq(args.mode, args.n)
        if args.auto_count_words is not None:
            return self._run_auto_count_words(args.search_phrase, args.auto_count_words, args.wait, args.max_pages)
        if args.chart:
            return self._run_relative_freq_chart(args.mode, args.n)

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

        try:
            processed = process_table(table.rows, first_row_is_header=getattr(self, "_first_row_is_header", False))
        except Exception as e:
            print(f"Failed to process table: {e}")
            return 5

        filename = f"{sanitize_filename(search_phrase)}.csv"
        try:
            csv_df = dataframe_to_csv_rows(processed.df)
            csv_df.to_csv(filename, index=False)
        except Exception as e:
            print(f"Failed to write CSV: {e}")
            return 6

        print(f"Saved table {table_number} to: {filename}")
        print()
        print("Value counts (excluding headers):")
        # pandas-like printing
        with pd.option_context("display.max_rows", 50, "display.max_colwidth", 80):
            print(processed.counts_df)
        return 0
    
    def _run_count_words(self, search_phrase: str, html_file: str | None) -> int:
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
            text = self.parser.extract_article_text(result.html)
            tokens = tokenize(text)
        except Exception as e:
            print(f"Failed to extract/tokenize text: {e}")
            return 4

        counts_path = "word-counts.json"
        try:
            update_counts_file(counts_path, tokens)
        except Exception as e:
            print(f"Failed to update {counts_path}: {e}")
            return 5

        print(f"Updated {counts_path} with {len(tokens)} tokens from: {result.final_url}")
        return 0
    
    def _run_relative_freq(self, mode: str, n: int) -> int:
        # Use cumulative word-counts.json (as in PDF workflow)
        counts_path = "word-counts.json"
        try:
            counts = load_counts(counts_path)
        except Exception as e:
            print(f"Failed to load {counts_path}: {e}")
            return 2

        if not counts:
            print(f"{counts_path} is empty. Run --count-words first.")
            return 3

        # Bulbapedia is English
        try:
            lang_ref = build_language_reference(lang="en", n=2000)
        except Exception as e:
            print(f"Failed to build language reference: {e}")
            return 4

        try:
            result = compute_relative_freq(counts, lang_ref, top_k=n)
            out = sort_relative_df(result.df, mode=mode)
        except Exception as e:
            print(f"Failed to compute relative frequency: {e}")
            return 5

        print(out)
        return 0
    
    def _run_relative_freq_chart(self, mode: str, n: int) -> int:
        import matplotlib.pyplot as plt

        counts_path = "word-counts.json"
        try:
            counts = load_counts(counts_path)
        except Exception as e:
            print(f"Failed to load {counts_path}: {e}")
            return 2

        if not counts:
            print(f"{counts_path} is empty. Run --count-words first.")
            return 3

        try:
            lang_ref = build_language_reference(lang="en", n=2000)
            result = compute_relative_freq(counts, lang_ref, top_k=n)
            df = sort_relative_df(result.df, mode=mode)
        except Exception as e:
            print(f"Failed to compute relative frequency: {e}")
            return 4

        df = df.copy()
        df["freq_language"] = df["freq_language"].fillna(0.0)

        words = df["word"].tolist()
        fa = df["freq_article"].tolist()
        fl = df["freq_language"].tolist()

        x = list(range(len(words)))
        w = 0.4

        plt.figure()
        plt.bar([i - w / 2 for i in x], fa, width=w, label="Article")
        plt.bar([i + w / 2 for i in x], fl, width=w, label="Language")

        plt.xticks(x, words, rotation=45, ha="right")
        plt.title("Relative word frequency")
        plt.legend()
        plt.tight_layout()

        out = "relative_frequency.png"
        plt.savefig(out, dpi=150)
        print(f"Saved chart to: {out}")
        return 0
    
    def _run_auto_count_words(self, search_phrase: str, depth: int, wait_s: float, max_pages: int) -> int:
        try:
            stats = self.crawler.auto_count_words(
                start_title=search_phrase.strip().replace(" ", "_"),
                max_depth=depth,
                wait_s=wait_s,
                max_pages=max_pages,
                counts_path="word-counts.json",
            )
        except Exception as e:
            print(f"Auto count failed: {e}")
            return 2

        print()
        print(f"Done. Visited pages: {stats.pages_visited}, unique pages: {stats.unique_pages}, tokens added: {stats.tokens_added}")
        return 0