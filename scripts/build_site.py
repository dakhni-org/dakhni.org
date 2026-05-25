#!/usr/bin/env python3
"""Static-site generator for dakhni.org.

Reads one JSON content file per page from content/ and renders a fully
normalised HTML page: an identical shell (head meta, nav, footer, AI
disclosure, search overlay) on every page, a single cover-style hero, the
shared /assets/site.css and /assets/site.js, and the page's body content.

This is the foundation for adding pages by filling fields rather than
hand-writing HTML. Run from the repo root:  python3 scripts/build_site.py
"""
import glob
import html as _html
import json
import os
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
NAV_FILE = os.path.join(CONTENT, "navigation.json")

GA = "G-N9RETSEPQ9"
KEYWORDS = ("Dakhni, Dakkani, Dakhini, Deccan, Deccani, Hyderabad, Hyderabadi, Bidar, "
            "Gulbarga, Bijapur, Aurangabad, Bahmani, Qutb Shahi, Adil Shahi, Asaf Jahi, "
            "Nizam, Dakhni Urdu, Deccani Urdu, Deccan Sultanates, qawwali, dargah, Sufi "
            "shrines, biryani, haleem, Charminar, Golconda, Bidriware, Deccan heritage")
FALLBACK_COVER = "/assets/dakhni-pattern.png"

PAGE_TYPES = {"home", "section_hub", "city_leaf", "saint_leaf", "institution_leaf", "heritage_leaf", "dynasty_leaf", "language_leaf", "sacred_site_leaf", "general_leaf"}

BASE_REQUIRED_FIELDS = {
    "title": str,
    "description": str,
    "url": str,
    "section": str,
    "dedication": str,
}

LEAF_REQUIRED_FIELDS = {
    "eyebrow": str,
    "title_html": str,
    "subtitle": str,
}

def validate_page(page: Dict[str, Any], source: str) -> List[str]:
    errors: List[str] = []
    required = dict(BASE_REQUIRED_FIELDS)
    if page.get("level") != "home":
        required.update(LEAF_REQUIRED_FIELDS)

    for key, expected in required.items():
        if key not in page:
            errors.append(f"{source}: missing required field '{key}'")
            continue
        if not isinstance(page[key], expected):
            errors.append(f"{source}: field '{key}' must be {expected.__name__}")
    has_body_html = isinstance(page.get("body_html"), str)
    has_blocks = isinstance(page.get("blocks"), list)
    if not has_body_html and not has_blocks:
        errors.append(f"{source}: provide either 'body_html' (string) or 'blocks' (array)")
    if "body_html" in page and not isinstance(page["body_html"], str):
        errors.append(f"{source}: field 'body_html' must be string when provided")
    if "blocks" in page and not isinstance(page["blocks"], list):
        errors.append(f"{source}: field 'blocks' must be array when provided")
    if isinstance(page.get("blocks"), list):
        for i, block in enumerate(page["blocks"]):
            if not isinstance(block, dict):
                errors.append(f"{source}: blocks[{i}] must be object")
                continue
            if not isinstance(block.get("type"), str):
                errors.append(f"{source}: blocks[{i}].type must be string")
                continue
            btype = block["type"]
            if btype in ("html", "intro"):
                if not isinstance(block.get("html"), str):
                    errors.append(f"{source}: blocks[{i}].html must be string for type '{btype}'")
            elif btype == "section":
                if not isinstance(block.get("title"), str):
                    errors.append(f"{source}: blocks[{i}].title must be string for type 'section'")
                if not isinstance(block.get("html"), str):
                    errors.append(f"{source}: blocks[{i}].html must be string for type 'section'")
            elif btype == "cards":
                cards = block.get("items")
                if not isinstance(cards, list):
                    errors.append(f"{source}: blocks[{i}].items must be array for type 'cards'")
                else:
                    for j, card in enumerate(cards):
                        if not isinstance(card, dict):
                            errors.append(f"{source}: blocks[{i}].items[{j}] must be object")
                            continue
                        if not isinstance(card.get("title"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].title must be string")
                        if not isinstance(card.get("html"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].html must be string")
            elif btype == "facts":
                items = block.get("items")
                if not isinstance(items, list):
                    errors.append(f"{source}: blocks[{i}].items must be array for type 'facts'")
                else:
                    for j, item in enumerate(items):
                        if not isinstance(item, dict):
                            errors.append(f"{source}: blocks[{i}].items[{j}] must be object")
                            continue
                        if not isinstance(item.get("key"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].key must be string")
                        if not isinstance(item.get("value"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].value must be string")
            elif btype == "timeline":
                items = block.get("items")
                if not isinstance(items, list):
                    errors.append(f"{source}: blocks[{i}].items must be array for type 'timeline'")
                else:
                    for j, item in enumerate(items):
                        if not isinstance(item, dict):
                            errors.append(f"{source}: blocks[{i}].items[{j}] must be object")
                            continue
                        if not isinstance(item.get("year"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].year must be string")
                        if not isinstance(item.get("text"), str):
                            errors.append(f"{source}: blocks[{i}].items[{j}].text must be string")
    for key in ("crumb_html", "subnav_html", "urdu", "cover", "hero_html", "level"):
        if key in page and not isinstance(page[key], str):
            errors.append(f"{source}: field '{key}' must be string when provided")
    if "extra_scripts" in page:
        val = page["extra_scripts"]
        if not isinstance(val, list) or any(not isinstance(x, str) for x in val):
            errors.append(f"{source}: field 'extra_scripts' must be an array of strings")
    url = page.get("url")
    if isinstance(url, str):
        if not url.startswith("/"):
            errors.append(f"{source}: url must start with '/'")
        if not url.endswith("/") and url != "/":
            errors.append(f"{source}: non-root url must end with '/'")
    page_type = page.get("page_type")
    if page_type is not None:
        if not isinstance(page_type, str):
            errors.append(f"{source}: field 'page_type' must be string")
        elif page_type not in PAGE_TYPES:
            errors.append(f"{source}: unknown page_type '{page_type}'; allowed: {sorted(PAGE_TYPES)}")
    tags = page.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
            errors.append(f"{source}: field 'tags' must be an array of strings")
    return errors


def validate_nav(nav_data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    brand = nav_data.get("brand")
    if not isinstance(brand, dict):
        return ["content/navigation.json: missing 'brand' object"]
    for key in ("label", "href", "logo", "aria_label"):
        if not isinstance(brand.get(key), str):
            errors.append(f"content/navigation.json: brand.{key} must be string")
    items = nav_data.get("items")
    if not isinstance(items, list):
        return errors + ["content/navigation.json: 'items' must be an array"]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"content/navigation.json: items[{i}] must be object")
            continue
        for key in ("label", "href"):
            if not isinstance(item.get(key), str):
                errors.append(f"content/navigation.json: items[{i}].{key} must be string")
        children = item.get("children")
        if children is not None:
            if not isinstance(children, list):
                errors.append(f"content/navigation.json: items[{i}].children must be array")
            else:
                for j, child in enumerate(children):
                    if not isinstance(child, dict):
                        errors.append(f"content/navigation.json: items[{i}].children[{j}] must be object")
                        continue
                    for key in ("label", "href"):
                        if not isinstance(child.get(key), str):
                            errors.append(f"content/navigation.json: items[{i}].children[{j}].{key} must be string")
    return errors


def render_nav(nav_data: Dict[str, Any]) -> str:
    brand = nav_data["brand"]
    items = nav_data["items"]
    out = ['<nav>']
    out.append(f'  <a href="{esc(brand["href"])}" class="nav-brand" aria-label="{esc(brand["aria_label"])}">')
    out.append(f'    <img class="nav-mark" src="{esc(brand["logo"])}" alt=""/>')
    out.append(f'    <span>{esc(brand["label"])}</span>')
    out.append('  </a>')
    out.append('  <button class="nav-search-btn" type="button" aria-label="Search" aria-expanded="false" aria-controls="ds-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg></button>')
    out.append('  <button class="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button>')
    out.append('  <ul class="nav-links">')
    for item in items:
        children = item.get("children", [])
        if children:
            out.append(f'    <li class="has-dropdown"><a href="{esc(item["href"])}">{esc(item["label"])}</a><ul class="dropdown">')
            for child in children:
                out.append(f'      <li><a href="{esc(child["href"])}">{esc(child["label"])}</a></li>')
            out.append('    </ul></li>')
        else:
            out.append(f'    <li><a href="{esc(item["href"])}">{esc(item["label"])}</a></li>')
    out.append('  </ul>')
    out.append('</nav>')
    return "\n".join(out)


def render_blocks(page: Dict[str, Any]) -> str:
    blocks = page.get("blocks")
    if not isinstance(blocks, list):
        return page.get("body_html", "")
    out: List[str] = []
    for block in blocks:
        btype = block.get("type")
        if btype == "html":
            out.append(block.get("html", ""))
        elif btype == "intro":
            out.append(f'<section class="content-intro">{block.get("html", "")}</section>')
        elif btype == "section":
            title = esc(block.get("title", ""))
            html = block.get("html", "")
            out.append(f'<section class="content-section"><h2>{title}</h2>{html}</section>')
        elif btype == "cards":
            out.append('<section class="content-cards"><div class="cards-grid">')
            for card in block.get("items", []):
                out.append(f'<article class="content-card"><h3>{esc(card.get("title", ""))}</h3>{card.get("html", "")}</article>')
            out.append('</div></section>')
        elif btype == "facts":
            out.append('<section class="facts-strip" aria-label="Key facts">')
            for item in block.get("items", []):
                key = esc(item.get("key", ""))
                val = esc(item.get("value", ""))
                out.append(f'<div class="fact"><span class="fact-key">{key}</span><span class="fact-val">{val}</span></div>')
            out.append('</section>')
        elif btype == "timeline":
            eyebrow = esc(block.get("eyebrow", ""))
            title = esc(block.get("title", ""))
            out.append(f'<section class="timeline-wrap" id="timeline">')
            if eyebrow or title:
                out.append('<header class="timeline-hdr">')
                if eyebrow:
                    out.append(f'<span class="timeline-eyebrow">{eyebrow}</span>')
                if title:
                    out.append(f'<h2 class="timeline-title">{title}</h2>')
                out.append('</header>')
            out.append('<ol class="tl-list">')
            for item in block.get("items", []):
                year = esc(item.get("year", ""))
                text = item.get("text", "")  # allow HTML in text
                out.append(f'<li class="tl-item reveal"><span class="tl-year">{year}</span><span class="tl-text">{text}</span></li>')
            out.append('</ol></section>')
    return "\n".join(out)

DISCLOSURE = '''<div id="ai-disclosure" role="dialog" aria-modal="true" aria-labelledby="disclosure-title">
  <div class="disclosure-backdrop"></div>
  <div class="disclosure-card">
    <div class="disclosure-ornament">✦</div>
    <p class="disclosure-label">A Note on Our Content</p>
    <h2 class="disclosure-title" id="disclosure-title">AI-Assisted Research</h2>
    <div class="disclosure-rule"></div>
    <p class="disclosure-body">The information on this website is compiled and synthesised with the assistance of artificial intelligence, drawing from publicly available historical records, academic publications, and cultural archives. While every effort is made to ensure accuracy, AI-generated content may occasionally reflect interpretations rather than universally established fact.</p>
    <p class="disclosure-body disclosure-body--note">Dakhni.org is an independent cultural project, not affiliated with any institution or government body. We encourage readers to consult primary sources for scholarly research.</p>
    <button class="disclosure-btn" id="disclosure-accept">I Understand</button>
  </div>
</div>'''

SEARCH = '''<div class="ds-search" id="ds-search" hidden>
  <div class="ds-search-backdrop" data-close></div>
  <div class="ds-search-box" role="dialog" aria-modal="true" aria-label="Search Dakhni.org">
    <div class="ds-search-bar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input type="search" id="ds-search-input" class="ds-search-input" placeholder="Search Dakhni.org…" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" aria-label="Search Dakhni.org"/>
      <button type="button" class="ds-search-cancel" data-close>Esc</button>
    </div>
    <ul class="ds-search-results" id="ds-search-results" role="listbox" aria-label="Search results"></ul>
    <p class="ds-search-hint" id="ds-search-hint">Search heritage, dynasties, cities, language, Sufism and more.</p>
  </div>
</div>'''


def esc(s):
    return _html.escape(s or "", quote=True)


def parent_url(url: str) -> str:
    parts = [p for p in url.strip("/").split("/") if p]
    if len(parts) <= 1:
        return "/"
    return "/" + "/".join(parts[:-1]) + "/"

def build_page_maps(pages):
    """Return (url_to_page, hub_urls, subnav_map).

    hub_urls: set of URLs that have at least one child page.
    subnav_map: url -> {prev, next, index_href} for each leaf page.
    """
    url_to_page = {p["url"]: p for p in pages if p.get("url")}
    hub_urls = {parent_url(p["url"]) for p in pages if p.get("url") and parent_url(p["url"]) != p["url"]}

    from collections import defaultdict
    groups = defaultdict(list)
    for page in pages:
        url = page.get("url", "")
        if not url or page.get("level") == "home":
            continue
        if url in hub_urls:
            continue  # hub pages don't get subnav
        p = parent_url(url)
        groups[p].append(page)

    subnav_map = {}
    for p_url, group in groups.items():
        sorted_g = sorted(group, key=lambda pg: (pg.get("sort_order", 999), pg.get("title", "")))
        for i, page in enumerate(sorted_g):
            subnav_map[page["url"]] = {
                "prev": sorted_g[i - 1] if i > 0 else None,
                "next": sorted_g[i + 1] if i < len(sorted_g) - 1 else None,
                "index_href": p_url,
            }
    return url_to_page, hub_urls, subnav_map

def render_auto_crumb(page: Dict[str, Any], url_to_page: Dict[str, Any]) -> str:
    url = page["url"]
    parts = [p for p in url.strip("/").split("/") if p]
    items = ['<a href="/">Home</a>']
    for i in range(len(parts) - 1):
        href = "/" + "/".join(parts[: i + 1]) + "/"
        hub = url_to_page.get(href)
        label = hub["title"] if hub else parts[i].replace("-", " ").title()
        items.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    items.append(esc(page["title"]))
    sep = '<span class="crumb-sep">›</span>'
    return sep.join(items)

def render_auto_subnav(page: Dict[str, Any], subnav_map: Dict, url_to_page: Dict) -> str:
    data = subnav_map.get(page.get("url", ""))
    if not data:
        return ""
    prev_pg = data.get("prev")
    next_pg = data.get("next")
    index_href = data["index_href"]
    if not prev_pg and not next_pg and index_href == "/":
        return ""  # lone child of home — no useful subnav
    index_page = url_to_page.get(index_href)
    index_title = "Back to " + (index_page["title"] if index_page else index_href.strip("/").split("/")[-1].replace("-", " ").title())
    out = ['<nav class="subnav" aria-label="Page navigator">']
    if prev_pg:
        out.append(f'<a class="prev" href="{esc(prev_pg["url"])}"><span class="subnav-eyebrow">‹ Prev</span><span class="subnav-title">{esc(prev_pg["title"])}</span></a>')
    out.append(f'<a class="index" href="{esc(index_href)}"><span class="subnav-eyebrow">Index</span><span class="subnav-title">{esc(index_title)}</span></a>')
    if next_pg:
        out.append(f'<a class="next" href="{esc(next_pg["url"])}"><span class="subnav-eyebrow">Next ›</span><span class="subnav-title">{esc(next_pg["title"])}</span></a>')
    out.append("</nav>")
    return "\n".join(out)


def footer(dedication):
    ded = dedication or "Built with love for the Deccan"
    return f'''<footer>
  <div class="flag-banner"><img src="/assets/dakhni-org-logo.png" alt="Dakhni.org"/></div>
  <div class="ft-divider"></div>
  <div class="ft-name">DAKHNI.ORG</div>
  <p class="ft-tagline">Preserving the soul of the Deccan, one story at a time.</p>
  <ul class="ft-links">
    <li><a href="/heritage/">Heritage</a></li>
    <li><a href="/dynasties/">Dynasties</a></li>
    <li><a href="/language/">Language</a></li>
    <li><a href="/sufism/">Sufism</a></li>
    <li><a href="/cities/">Cities</a></li>
    <li><a href="/#quiz">Quiz</a></li>
    <li><a href="/about/">About</a></li>
  </ul>
  <p class="ft-copy">© <span id="year">2025</span> Dakhni.org · {esc(ded)} · Built with love for the Deccan</p>
</footer>'''


def head(page):
    url = page["url"]
    canonical = "https://dakhni.org" + url
    title = page["title"]
    full_title = "Dakhni.org — Heritage of the Deccan" if url == "/" else f'{title} — Dakhni.org'
    desc = page.get("description", "")
    cover = page.get("cover") or ""
    og_img = ("https://dakhni.org" + cover) if cover.startswith("/") else (cover or "https://dakhni.org/assets/dakhni-org-logo.png")
    page_tags = page.get("tags", [])
    all_keywords = KEYWORDS + (", " + ", ".join(page_tags) if page_tags else "")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA}');
</script>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{esc(full_title)}</title>
  <link rel="icon" type="image/png" href="/assets/dakhni-org-logo.png"/>
  <meta name="description" content="{esc(desc)}"/>
  <meta name="keywords" content="{esc(all_keywords)}"/>
  <meta name="author" content="Dakhni.org"/>
  <meta name="robots" content="index, follow, max-image-preview:large"/>
  <meta name="theme-color" content="#1A1814"/>
  <link rel="canonical" href="{canonical}"/>
  <meta property="og:type" content="website"/>
  <meta property="og:title" content="{esc(full_title)}"/>
  <meta property="og:description" content="{esc(desc)}"/>
  <meta property="og:url" content="{canonical}"/>
  <meta property="og:image" content="{esc(og_img)}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500&family=Lateef:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/assets/site.css"/>
</head>'''


def hero(page):
    cover = page.get("cover") or FALLBACK_COVER
    no_photo = "" if page.get("cover") else " page-hero--pattern"
    eyebrow = page.get("eyebrow", "")
    urdu = page.get("urdu", "")
    title_html = page.get("title_html") or esc(page["title"])
    subtitle = page.get("subtitle", "")
    parts = ['<header class="city-hero page-hero--cover%s" style="--cover:url(\'%s\')">' % (no_photo, esc(cover))]
    parts.append('  <div class="city-hero-inner">')
    if eyebrow:
        parts.append(f'    <span class="city-hero-eyebrow">{esc(eyebrow)}</span>')
    if urdu:
        parts.append(f'    <p class="city-hero-urdu">{esc(urdu)}</p>')
    parts.append(f'    <h1 class="city-hero-title">{title_html}</h1>')
    parts.append('    <div class="city-hero-rule"></div>')
    if subtitle:
        parts.append(f'    <p class="city-hero-sub">{esc(subtitle)}</p>')
    parts.append('  </div>')
    parts.append('</header>')
    return "\n".join(parts)


def render(page, nav_html, url_to_page, subnav_map):
    body = render_blocks(page)
    crumb = page.get("crumb_html") or render_auto_crumb(page, url_to_page)
    subnav = page.get("subnav_html") or render_auto_subnav(page, subnav_map, url_to_page)
    out = [head(page), "<body>", nav_html]
    if page.get("level") == "home":
        out.append(page.get("hero_html", ""))
        out.append('<main class="page-main page-main--home">')
        out.append(body)
        out.append('</main>')
    else:
        out.append(hero(page))
        out.append('<main class="page-main">')
        if crumb:
            out.append(f'  <p class="crumb">{crumb}</p>')
        out.append(body)
        out.append('</main>')
    if subnav:
        out.append(subnav)
    out.append(footer(page.get("dedication")))
    out.append(DISCLOSURE)
    out.append(SEARCH)
    for sc in page.get("extra_scripts", []):
        out.append("<script>\n" + sc + "\n</script>")
    out.append('<script defer src="/assets/site.js"></script>')
    out.append("</body>\n</html>")
    return "\n".join(out) + "\n"


def main():
    with open(NAV_FILE, encoding="utf-8") as fh:
        nav_data = json.load(fh)
    nav_errors = validate_nav(nav_data)
    if nav_errors:
        print("Navigation validation failed:")
        for err in nav_errors:
            print(f"- {err}")
        raise SystemExit(1)
    nav_html = render_nav(nav_data)

    pages = []
    errors: List[str] = []
    for jf in sorted(glob.glob(os.path.join(CONTENT, "**", "*.json"), recursive=True)):
        if os.path.abspath(jf) == os.path.abspath(NAV_FILE):
            continue
        with open(jf, encoding="utf-8") as fh:
            page = json.load(fh)
        pages.append(page)
        errors.extend(validate_page(page, os.path.relpath(jf, ROOT)))
    if errors:
        print("Content validation failed:")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    url_to_page, hub_urls, subnav_map = build_page_maps(pages)
    n = 0
    for page in pages:
        rel = page["url"].strip("/")
        outdir = os.path.join(ROOT, rel) if rel else ROOT
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(render(page, nav_html, url_to_page, subnav_map))
        n += 1
    print(f"Rendered {n} pages")


if __name__ == "__main__":
    main()
