from __future__ import annotations

import csv
from pathlib import Path


def write_csv(path: str, rows: list[list[str]]) -> None:
    p = Path(path)
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)