from src.wikiscraper.parser import ArticleParser


def test_extract_article_links_filters_namespaces_and_nonwiki():
    html = """
    <div id="mw-content-text">
      <p>
        <a href="/wiki/Pikachu">Pikachu</a>
        <a href="/wiki/Type#Chart">Type chart</a>
        <a href="/wiki/File:Something.png">file</a>
        <a href="/wiki/Category:Stuff">cat</a>
        <a href="https://example.com/wiki/Pikachu">external</a>
        <a href="/notwiki/Whatever">no</a>
        <a href="/wiki/">empty</a>
      </p>
    </div>
    """
    p = ArticleParser()
    links = p.extract_article_links(html)
    assert "Pikachu" in links
    assert "Type" in links
    assert all(":" not in x for x in links)
