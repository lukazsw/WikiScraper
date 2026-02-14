from src.wikiscraper.parser import ArticleParser


def test_extract_first_paragraph_from_saved_html():
    html = open("data/pikachu.html", "r", encoding="utf-8").read()
    parser = ArticleParser()
    paragraph = parser.extract_first_paragraph(html)

    assert "Pikachu" in paragraph
    assert "Electric-type" in paragraph