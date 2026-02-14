from __future__ import annotations

import re


def sanitize_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_\-]+", "", name)
    return name or "output"