from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ProcessedTable:
    df: pd.DataFrame
    counts_df: pd.DataFrame


def _pad_rows(rows: list[list[str]], pad: str = "") -> list[list[str]]:
    width = max((len(r) for r in rows), default=0)
    return [r + [pad] * (width - len(r)) for r in rows]


def process_table(rows: list[list[str]], first_row_is_header: bool) -> ProcessedTable:
    """
    Assumptions from spec:
    - first column = row headers
    - if first_row_is_header: first row = column headers
    We compute value counts excluding headers (row headers and optional column headers).
    Additionally, we try to drop "axis label" rows like 'Attacking type' that are not real data rows.
    """
    padded = _pad_rows(rows, pad="")

    header_row: list[str] | None
    body: list[list[str]]
    if first_row_is_header:
        header_row = padded[0]
        body = padded[1:]
    else:
        header_row = None
        body = padded

    if not body:
        raise ValueError("Table has no data rows after removing header row.")

    def is_axis_label_row(r: list[str]) -> bool:
        first = (r[0] or "").strip().lower()
        if first in {"attacking type", "defending type", "attack", "defense"}:
            return True
        return False

    body = [r for r in body if not is_axis_label_row(r)]
    if not body:
        raise ValueError("Table has no data rows after removing axis label rows.")

    row_headers = [r[0] for r in body]
    data = [r[1:] for r in body]
    data_width = len(data[0]) if data else 0

    if header_row is not None:
        col_headers = header_row[1 : 1 + data_width]
        if len(col_headers) < data_width:
            col_headers = col_headers + [f"col_{i+1}" for i in range(len(col_headers), data_width)]
    else:
        col_headers = [f"col_{i+1}" for i in range(data_width)]

    df = pd.DataFrame(data, index=row_headers, columns=col_headers)

    flat = pd.Series(df.to_numpy().ravel())
    flat = flat[flat.notna()]
    flat = flat.astype(str).str.strip()
    flat = flat[flat != ""]

    # Auto-detect "multiplier chart" tables (like Type Chart):
    # if most values look like e.g. '1×', '½×', '2×', '0×' -> count only those
    is_multiplier = flat.str.fullmatch(r".*×")
    if len(flat) > 0 and (is_multiplier.mean() >= 0.5):
        flat = flat[is_multiplier]

    counts = flat.value_counts().reset_index()
    counts.columns = ["value", "count"]

    return ProcessedTable(df=df, counts_df=counts)


def dataframe_to_csv_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    For CSV output we include row headers as a normal first column to keep index.
    """
    out = df.copy()
    out.insert(0, "row", out.index)
    out.reset_index(drop=True, inplace=True)
    return out