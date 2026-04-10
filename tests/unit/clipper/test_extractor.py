from app.clipper.extractor import extract_page


def test_extract_page_picks_article_with_most_paragraph_text() -> None:
    """When multiple <article> tags exist, the one with the most <p> text is chosen."""
    html = """
    <html><body>
      <article class="sidebar">Related: <a href="/x">Short link</a></article>
      <article class="main">
        <h1>Main Article</h1>
        <p>This is the real content with a lot of text that should be selected
        because it has more characters than the sidebar article above.</p>
      </article>
    </body></html>
    """
    page = extract_page(html, "https://example.com/article")
    assert "Main Article" in page.content_html
    assert "This is the real content" in page.content_html
    assert 'class="sidebar"' not in page.content_html


def test_extract_page_single_article() -> None:
    html = """
    <html><body>
      <article><h1>Only Article</h1><p>Content here.</p></article>
    </body></html>
    """
    page = extract_page(html, "https://example.com/article")
    assert "Only Article" in page.content_html
    assert "Content here." in page.content_html


def test_extract_page_falls_back_to_main_when_no_article() -> None:
    html = """
    <html><body>
      <main><p>Main tag content</p></main>
    </body></html>
    """
    page = extract_page(html, "https://example.com/article")
    assert "Main tag content" in page.content_html


def test_extract_page_removes_noise_tags() -> None:
    html = """
    <html><body>
      <article>
        <h1>Article</h1>
        <script>alert("xss")</script>
        <nav>Navigation</nav>
        <p>Real paragraph</p>
      </article>
    </body></html>
    """
    page = extract_page(html, "https://example.com/article")
    assert "Real paragraph" in page.content_html
    assert "<script>" not in page.content_html
    assert "<nav>" not in page.content_html


def test_extract_page_extracts_og_metadata() -> None:
    html = """
    <html>
      <head>
        <meta property="og:title" content="OG Title"/>
        <meta property="og:site_name" content="My Site"/>
        <meta property="article:published_time" content="2024-06-01T10:00:00Z"/>
        <meta property="og:url" content="https://example.com/canonical"/>
      </head>
      <body><article><p>Content</p></article></body>
    </html>
    """
    page = extract_page(html, "https://example.com/article")
    assert page.title == "OG Title"
    assert page.site_name == "My Site"
    assert page.published_time == "2024-06-01T10:00:00Z"
    assert page.canonical_url == "https://example.com/canonical"


def test_extract_page_makes_relative_links_absolute() -> None:
    html = """
    <html><body>
      <article>
        <a href="/about">About</a>
        <img src="/images/photo.jpg" alt="photo"/>
      </article>
    </body></html>
    """
    page = extract_page(html, "https://example.com/article")
    assert 'href="https://example.com/about"' in page.content_html
    assert 'src="https://example.com/images/photo.jpg"' in page.content_html


def test_extract_page_sidebar_without_paragraphs_falls_back_to_main_tag() -> None:
    """em.com.br bug: all <article> tags have no <p> content, falls back to <main>."""
    html = """
    <html><body>
      <article>
        <a href="/other"><figure><img src="/img.jpg"/></figure></a>
      </article>
      <main class="edm-cms-content">
        <h1>Real Article Title</h1>
        <p>First paragraph of the actual article content.</p>
        <p>Second paragraph with more details.</p>
      </main>
    </body></html>
    """
    page = extract_page(html, "https://news.example.com/article")
    assert "Real Article Title" in page.content_html
    assert "First paragraph" in page.content_html


def test_extract_page_sidebar_larger_but_no_paragraphs_is_excluded() -> None:
    """Reproduces the otempo.com.br bug: sidebar has more total text but no <p> tags."""
    sidebar_items = " ".join(
        f"<li>Item {i}: some long text here</li>" for i in range(20)
    )

    html = f"""
    <html><body>
      <article class="articles__wrapper">
        <ul class="list__container">{sidebar_items}</ul>
      </article>
      <article class="main-content">
        <h1>Real News Article</h1>
        <p>Actual article content in a paragraph.</p>
      </article>
    </body></html>
    """
    page = extract_page(html, "https://news.example.com/article")
    assert "Real News Article" in page.content_html
    assert "Actual article content" in page.content_html
    assert 'class="articles__wrapper"' not in page.content_html
