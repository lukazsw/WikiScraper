from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict
import unicodedata


_word_re = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)


def _normalize(text: str) -> str:
    # Normalize unicode to reduce weird splits
    return unicodedata.normalize("NFKC", text)


def tokenize(text: str) -> list[str]:
    text = _normalize(text)
    toks = [m.group(0).lower() for m in _word_re.finditer(text)]
    # drop 1-letter tokens like "s"
    toks = [t for t in toks if len(t) >= 2]
    return toks


def load_counts(path: str) -> Dict[str, int]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))

    out: Dict[str, int] = {}

    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, int):
            out[k] = v
    return out


def save_counts(path: str, counts: Dict[str, int]) -> None:
    p = Path(path)
    p.write_text(json.dumps(counts, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def update_counts_file(path: str, tokens: list[str]) -> Dict[str, int]:
    counts = load_counts(path)
    for tok in tokens:
        counts[tok] = counts.get(tok, 0) + 1
    save_counts(path, counts)
    return counts