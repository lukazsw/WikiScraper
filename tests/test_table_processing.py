from src.wikiscraper.table_extractor import TableExtractor
from src.wikiscraper.table_processing import process_table


def test_type_chart_counts_contains_multipliers_only_or_mostly():
    html = open("data/type.html", "r", encoding="utf-8").read()
    table = TableExtractor().extract_nth_table(html, 2)

    processed = process_table(table.rows, first_row_is_header=True)
    counts = dict(zip(processed.counts_df["value"], processed.counts_df["count"]))

    # The core multipliers must exist
    assert "1×" in counts
    assert "2×" in counts
    assert "½×" in counts
    assert "0×" in counts
