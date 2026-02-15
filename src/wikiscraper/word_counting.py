from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict


_word_re = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")  # simple English-ish tokens


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _word_re.finditer(text)]


def load_counts(path: str) -> Dict[str, int]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    # be defensive
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