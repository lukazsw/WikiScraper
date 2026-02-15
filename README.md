# WikiScraper (Bulbapedia)

CLI tool for scraping Bulbapedia (MediaWiki) pages and performing basic table/text analyses.

## Requirements
- Python 3.11+ (tested on 3.12)
- Dependencies in `requirements.txt`

## Setup (macOS / Linux)
Run in the project root (where `wiki_scraper.py` and `requirements.txt` are located):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

> VS Code: select interpreter `.venv/bin/python` (and choose the same kernel for notebooks).

## Usage (CLI)

General form:

```bash
python wiki_scraper.py "<search_phrase>" <mode> [options]
```

Help:

```bash
python wiki_scraper.py --help
```

### 1) Summary (`--summary`)
Prints the first meaningful paragraph of the article (without HTML tags).

Online:
```bash
python wiki_scraper.py "Pikachu" --summary
```

Offline (deterministic, for testing):
```bash
python wiki_scraper.py "Pikachu" --summary --html-file data/pikachu.html
```

### 2) Table (`--table N`)
Extracts the N-th `<table>` (1-indexed), saves it to CSV, and prints value counts (excluding headers).

- Output file: `<search_phrase>.csv` (e.g. `Type.csv`)
- If `--first-row-is-header` is set, the first row is treated as column headers.
- For “multiplier chart” tables (e.g. Type Chart), if most cells look like `1×`, `½×`, `2×`, `0×`,
  value counts are computed only for those multiplier-like values (to avoid counting headings).

Example (Type Chart on Bulbapedia):
```bash
python wiki_scraper.py "Type" --table 2 --first-row-is-header
```

Offline:
```bash
python wiki_scraper.py "Type" --table 2 --first-row-is-header --html-file data/type.html
```

### 3) Count words (`--count-words`)
Extracts article text (without menus), tokenizes it, and updates a cumulative `word-counts.json`.

Offline:
```bash
python wiki_scraper.py "Pikachu" --count-words --html-file data/pikachu.html
```

Online:
```bash
python wiki_scraper.py "Pikachu" --count-words
```

### 4) Analyze relative word frequency (`--analyze-relative-word-frequency`)
Compares `word-counts.json` to a language reference (from `wordfreq`) and prints a table with:

- `word`
- `freq_article` (frequency in collected wiki text)
- `freq_language` (frequency in wiki language reference)

Sorting:
- `--mode article` (default): sorted by article frequency; `freq_language` can be NaN for missing words (e.g. names)
- `--mode language`: sorted by language frequency; `freq_article` can be NaN if a common language word is absent in wiki counts

Examples:
```bash
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode article --n 20
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode language --n 20
```

> Note: `search_phrase` is required by the CLI; this mode uses `word-counts.json` and does not need the phrase.

#### Chart (`--chart [PATH]`)
Optionally saves a bar chart comparing normalized frequencies (0..1) for the top `n` words.

Default path:
```bash
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode article --n 20 --chart
```

Custom path:
```bash
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode article --n 20 --chart out.png
```

### 5) Auto count words (crawler) (`--auto-count-words DEPTH`)
Crawls linked pages up to `DEPTH` (BFS/graph traversal), updating `word-counts.json`.

Options:
- `--wait` – delay between requests (seconds) to reduce risk of rate-limits
- `--max-pages` – hard cap on visited pages (prevents crawl explosion)

Examples:
```bash
python wiki_scraper.py "Pikachu" --auto-count-words 0 --wait 0.2 --max-pages 10
python wiki_scraper.py "Pikachu" --auto-count-words 1 --wait 0.2 --max-pages 30
```

## Tests

Unit tests:
```bash
python -m pytest -q
```

Integration test (offline):
```bash
python wiki_scraper_integration_test.py
```

## Notebook (language confidence score)
Notebook: `notebooks/lang_detection.ipynb`

Contains:
- implementation of `lang_confidence_score(...)`
- experiments for languages `en/pl/de` and `k = 3/10/100/1000`
- plots + discussion (as required by the assignment)

## Project structure (short)
- `wiki_scraper.py` – CLI entrypoint
- `src/wikiscraper/` – implementation
  - `app.py` – mode routing and application logic
  - `cli.py` – argparse interface
  - `fetcher.py` – HTML fetching + offline file mode
  - `parser.py` – parsing summaries, text and links
  - `table_extractor.py`, `table_processing.py` – table extraction/processing/counts
  - `word_counting.py` – tokenization + `word-counts.json`
  - `relative_frequency.py` – language reference + comparison utilities
  - `crawler.py` – `--auto-count-words` crawler
- `tests/` – unit tests
- `data/` – optional offline HTML inputs
- `notebooks/` – notebook experiments

## Attribution / source notice
Content is sourced from Bulbapedia (Bulbagarden). This project is educational.
