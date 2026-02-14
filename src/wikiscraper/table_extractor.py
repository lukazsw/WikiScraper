from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class TableData:
    rows: list[list[str]]  # each row: list of cell texts


class TableExtractor:
    def extract_nth_table(self, html: str, n: int) -> TableData:
        if n < 1:
            raise ValueError("Table number must be >= 1")

        soup = BeautifulSoup(html, "lxml")
        tables = soup.select("#mw-content-text table")

        if len(tables) < n:
            raise ValueError(f"Requested table {n}, but only {len(tables)} tables found.")

        table = tables[n - 1]

        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            if not cells:
                continue
            row = [c.get_text(" ", strip=True) for c in cells]
            rows.append(row)

        if not rows:
            raise ValueError("Extracted table is empty.")

        return TableData(rows=rows)