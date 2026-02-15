from src.wikiscraper.word_counting import tokenize, update_counts_file, load_counts


def test_tokenize_basic():
    text = "Pikachu is Electric-type. Pikachu's tail!"
    tokens = tokenize(text)
    assert tokens.count("pikachu") == 1  # "Pikachu" appears once as token
    assert "electric" in tokens
    assert "type" in tokens
    assert "pikachu's" in tokens


def test_update_counts_file_merges(tmp_path):
    path = tmp_path / "counts.json"
    update_counts_file(str(path), ["a", "b", "a"])
    update_counts_file(str(path), ["b", "c"])

    counts = load_counts(str(path))
    assert counts["a"] == 2
    assert counts["b"] == 2
    assert counts["c"] == 1
