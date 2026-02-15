from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from wordfreq import top_n_list, zipf_frequency


@dataclass(frozen=True)
class RelativeFreqResult:
    df: pd.DataFrame


def build_language_reference(lang: str, n: int = 2000) -> dict[str, float]:
    """
    Returns {word: zipf_frequency(word, lang)} for top-n words.
    zipf_frequency is a stable scale; higher = more common in language.
    """
    words = top_n_list(lang, n)
    return {w: float(zipf_frequency(w, lang)) for w in words}


def compute_relative_freq(article_counts: dict[str, int], lang_ref: dict[str, float], top_k: int) -> RelativeFreqResult:
    """
    article_counts: {word: count}
    lang_ref: {word: language_freq_score}
    """
    article_series = pd.Series(article_counts, dtype="int64")
    article_series = article_series.sort_values(ascending=False)

    top_words = article_series.head(top_k).index.tolist()

    rows = []
    for w in top_words:
        rows.append(
            {
                "word": w,
                "freq_article": int(article_counts[w]),
                "freq_language": lang_ref.get(w, float("nan")),
            }
        )

    df = pd.DataFrame(rows)
    return RelativeFreqResult(df=df)


def sort_relative_df(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode == "article":
        return df.sort_values(by=["freq_article", "word"], ascending=[False, True]).reset_index(drop=True)
    if mode == "language":
        # NaN should go last (rare/unknown words)
        return df.sort_values(by=["freq_language", "word"], ascending=[False, True], na_position="last").reset_index(drop=True)
    raise ValueError(f"Unknown mode: {mode}")