# WikiScraper (Bulbapedia)

CLI tool for scraping Bulbapedia (MediaWiki) pages and performing basic text/table analyses.

## Requirements
- Python 3.12+ (works on 3.11+ as well)
- Dependencies listed in `requirements.txt`

## Setup (macOS/Linux)
Run in the project root (where `wiki_scraper.py` and `requirements.txt` are located):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

> VS Code: select interpreter `WikiScraper/.venv/bin/python` and (for notebooks) choose the kernel from `.venv`.

## Run (CLI)

General form:

```bash
python wiki_scraper.py "<search_phrase>" <mode> [options]
```

Help:

```bash
python wiki_scraper.py --help
```

### 1) Summary (`--summary`)
Prints the first meaningful paragraph (summary) of the article.

Online:
```bash
python wiki_scraper.py "Pikachu" --summary
```

Offline (deterministic, for testing):
```bash
python wiki_scraper.py "Pikachu" --summary --html-file data/pikachu.html
```

### 2) Table (`--table N`)
Extracts the N-th `<table>` (1-indexed) from the article content, saves it to CSV, and prints value counts
(excluding headers). For “chart-like” tables (e.g., Type Chart), it automatically counts only multiplier-like
values containing `×`.

Online:
```bash
python wiki_scraper.py "Type" --table 2 --first-row-is-header
```

Offline:
```bash
python wiki_scraper.py "Type" --table 2 --first-row-is-header --html-file data/type.html
```

CSV output file: `<search_phrase>.csv` (e.g., `Type.csv`).

### 3) Count words (`--count-words`)
Updates `word-counts.json` with word frequencies for the article text.
The file is cumulative: running it multiple times adds counts (merges into existing JSON).

Offline:
```bash
python wiki_scraper.py "Pikachu" --count-words --html-file data/pikachu.html
```

Online:
```bash
python wiki_scraper.py "Pikachu" --count-words
```

### 4) Analyze relative word frequency (`--analyze-relative-word-frequency`)
Compares word counts from `word-counts.json` with a language reference from `wordfreq`.

Sorting mode:
- `--mode article` (default): sort by article frequency
- `--mode language`: sort by language frequency (NaNs last)

```bash
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode article --n 20
python wiki_scraper.py "x" --analyze-relative-word-frequency --mode language --n 20
```

> `search_phrase` is required by the CLI, but this mode uses `word-counts.json` (the phrase is not used).

### 5) Chart (`--chart`)
Generates a bar chart comparing `freq_article` vs `freq_language` for top `n` words.
Output: `relative_frequency.png`

```bash
python wiki_scraper.py "x" --chart --mode article --n 20
```

### 6) Auto count words (crawler) (`--auto-count-words DEPTH`)
Breadth-first crawl from the start article up to `DEPTH`, updating `word-counts.json`.

Options:
- `--wait` – delay between requests (seconds)
- `--max-pages` – hard limit on visited pages (prevents crawl explosion)

Examples:
```bash
python wiki_scraper.py "Pikachu" --auto-count-words 0 --wait 0.2 --max-pages 10
python wiki_scraper.py "Pikachu" --auto-count-words 1 --wait 0.2 --max-pages 30
```

## Offline HTML (data/)
For deterministic tests, HTML pages can be saved into `data/`.

Pikachu:
```bash
mkdir -p data
python - <<'PY'
import requests
url = "https://bulbapedia.bulbagarden.net/wiki/Pikachu"
html = requests.get(url, headers={"User-Agent": "WikiScraper/1.0 (Educational project)"}).text
open("data/pikachu.html", "w", encoding="utf-8").write(html)
print("saved: data/pikachu.html")
PY
```

Type:
```bash
python - <<'PY'
import requests
url = "https://bulbapedia.bulbagarden.net/wiki/Type"
html = requests.get(url, headers={"User-Agent": "WikiScraper/1.0 (Educational project)"}).text
open("data/type.html", "w", encoding="utf-8").write(html)
print("saved: data/type.html")
PY
```

## Tests

### Unit tests (pytest)
```bash
python -m pytest -q
```

### Integration test (offline)
A standalone runnable integration test script:

```bash
python wiki_scraper_integration_test.py
```

Returns exit code `0` on success and non-zero on failure.

## Notebook (language confidence score)
Notebook: `notebooks/lang_detection.ipynb`

Contains:
- `lang_confidence_score(text, language, top_words)`
- experiments for languages `en/pl/de` and k = 3/10/100/1000
- tables, plots, method explanation and limitations

## Project structure (short)
- `wiki_scraper.py` – CLI entrypoint
- `src/wikiscraper/` – implementation:
  - `app.py` – mode routing and application logic
  - `cli.py` – argparse interface
  - `fetcher.py` – HTML fetching + offline file mode
  - `parser.py` – parsing summaries, text and links
  - `table_extractor.py`, `table_processing.py` – table extraction/processing/counts
  - `word_counting.py` – tokenization and `word-counts.json`
  - `relative_frequency.py` – `wordfreq` comparison utilities
  - `crawler.py` – `--auto-count-words` crawler
- `tests/` – unit tests
- `data/` – optional offline HTML inputs
- `notebooks/` – notebook experiments

## Attribution / source notice
Content is sourced from Bulbapedia (Bulbagarden). This project is educational.
