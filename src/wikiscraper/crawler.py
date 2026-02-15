from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from .fetcher import PageFetcher
from .parser import ArticleParser
from .word_counting import tokenize, update_counts_file


@dataclass(frozen=True)
class CrawlStats:
    pages_visited: int
    tokens_added: int
    unique_pages: int


class WikiCrawler:
    def __init__(self, fetcher: PageFetcher, parser: ArticleParser) -> None:
        self.fetcher = fetcher
        self.parser = parser

     def auto_count_words(self, start_title: str, max_depth: int, wait_s: float, max_pages: int, counts_path: str = "word-counts.json") -> CrawlStats:
        """
        Breadth-first traversal from start_title up to max_depth.
        Depth 0 => only start page.
        Uses visited set to avoid duplicates.
        """
        if max_pages < 1:
            raise ValueError("--max-pages must be >= 1")
        if max_depth < 0:
            raise ValueError("DEPTH must be >= 0")

        q = deque([(start_title, 0)])
        visited: set[str] = set()
        pages_visited = 0
        tokens_added = 0

        while q:
            if pages_visited >= max_pages:
                break
            title, depth = q.popleft()
            if title in visited:
                continue
            visited.add(title)

            # polite waiting (skip before the very first request)
            if pages_visited > 0 and wait_s > 0:
                time.sleep(wait_s)

            try:
                result = self.fetcher.fetch_article_html(title)
            except FileNotFoundError:
                print(f"[skip] 404 title={title}")
                continue
            pages_visited += 1

            text = self.parser.extract_article_text(result.html)
            tokens = tokenize(text)
            tokens_added += len(tokens)
            update_counts_file(counts_path, tokens)

            print(f"[{pages_visited}] depth={depth} title={title} tokens={len(tokens)}")

            if depth >= max_depth:
                continue

            links = self.parser.extract_article_links(result.html)
            for nxt in links:
                if nxt not in visited:
                    q.append((nxt, depth + 1))

        return CrawlStats(pages_visited=pages_visited, tokens_added=tokens_added, unique_pages=len(visited))