from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

_NOISE_TAGS = frozenset(
    {
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "noscript",
        "iframe",
        "form",
        "button",
        "input",
        "select",
        "textarea",
    }
)


@dataclass(frozen=True)
class ExtractedPage:
    title: str
    description: str
    content_html: str
    canonical_url: str | None
    site_name: str | None
    published_time: str | None


def _extract_title(soup: BeautifulSoup) -> str:
    og_title = soup.find("meta", property="og:title")
    if isinstance(og_title, Tag) and og_title.get("content"):
        return str(og_title["content"])
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()
    return ""


def _extract_meta(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"name": name})
    if isinstance(tag, Tag) and tag.get("content"):
        return str(tag["content"])
    return ""


def _extract_og(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.find("meta", property=prop)
    if isinstance(tag, Tag) and tag.get("content"):
        return str(tag["content"])
    return None


def _extract_canonical(soup: BeautifulSoup, fallback_url: str) -> str | None:
    link = soup.find("link", rel="canonical")
    if isinstance(link, Tag) and link.get("href"):
        return str(link["href"])
    og_url = _extract_og(soup, "og:url")
    if og_url:
        return og_url
    return fallback_url


def _make_links_absolute(tag: Tag, base_url: str) -> None:
    for a in tag.find_all("a", href=True):
        href = a.get("href", "")
        if isinstance(href, str) and not href.startswith(
            ("http://", "https://", "mailto:", "#")
        ):
            a["href"] = urljoin(base_url, href)

    lazy_src_attrs = ("data-src", "data-lazy-src", "data-original", "data-lazy")
    lazy_srcset_attrs = ("data-srcset", "srcset")
    for img in tag.find_all("img"):
        src_raw = img.get("src", "")
        src = src_raw if isinstance(src_raw, str) else ""
        # Resolve lazy-loaded images: prefer lazy attr when src is missing/placeholder
        if (
            not src
            or "data:image" in src
            or src.endswith(("1x1.gif", "1x1.png", "placeholder"))
        ):
            # First try direct src attrs
            for attr in lazy_src_attrs:
                lazy = img.get(attr, "")
                if lazy and isinstance(lazy, str):
                    img["src"] = lazy
                    src = lazy
                    break
            # Fall back to srcset attrs — extract URL from first candidate
            if (
                not src
                or "data:image" in src
                or src.endswith(("1x1.gif", "1x1.png", "placeholder"))
            ):
                for attr in lazy_srcset_attrs:
                    lazy = img.get(attr, "")
                    if lazy and isinstance(lazy, str):
                        first_candidate = lazy.split(",")[0].strip().split()[0]
                        if first_candidate:
                            img["src"] = first_candidate
                            src = first_candidate
                            break
        if (
            isinstance(src, str)
            and src
            and not src.startswith(("http://", "https://", "data:"))
        ):
            img["src"] = urljoin(base_url, src)


def extract_page(html: str, url: str) -> ExtractedPage:
    """Extract readable content from raw HTML."""
    soup = BeautifulSoup(html, "html.parser")

    title = _extract_title(soup)
    description = _extract_meta(soup, "description")
    canonical_url = _extract_canonical(soup, url)
    site_name = _extract_og(soup, "og:site_name")
    published_time = _extract_og(soup, "article:published_time")

    # Score <article> elements by total <p> text length rather than raw text.
    # Sidebar widgets (related articles, promo cards) use <li>/<span>/<a> and
    # contain zero prose paragraphs; real editorial articles have <p> content.
    # Falling back to raw text would pick the sidebar whenever it has more
    # link/list text than the article body (observed on otempo.com.br).
    # If no <article> has any <p> text at all, best_article stays None and
    # the selector chain below takes over (e.g. em.com.br uses <main>).
    articles = soup.find_all("article")
    best_article: Tag | None = None
    if articles:
        best = max(
            articles,
            key=lambda t: sum(len(p.get_text()) for p in t.find_all("p")),
        )
        if any(p.get_text().strip() for p in best.find_all("p")):
            best_article = best
    content_tag = (
        best_article
        or soup.find("main")
        or soup.find(id="content")
        or soup.find(id="main-content")
        or soup.find(class_="content")
        or soup.find("body")
    )

    if content_tag and isinstance(content_tag, Tag):
        for noise in content_tag.find_all(lambda t: t.name in _NOISE_TAGS):
            noise.decompose()
        # Convert <amp-img> to <img> (used by AMP pages, e.g. G1/Globo)
        for amp_img in content_tag.find_all("amp-img"):
            img_tag = soup.new_tag("img")
            for attr in ("src", "srcset", "alt", "width", "height"):
                val = amp_img.get(attr)
                if val:
                    img_tag[attr] = val
            img_tag["style"] = "max-width: 100%; height: auto;"
            amp_img.replace_with(img_tag)
        _make_links_absolute(content_tag, url)
        content_html = str(content_tag)
    else:
        content_html = ""

    return ExtractedPage(
        title=title,
        description=description,
        content_html=content_html,
        canonical_url=canonical_url,
        site_name=site_name,
        published_time=published_time,
    )
