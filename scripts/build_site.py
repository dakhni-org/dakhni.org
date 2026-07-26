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
import re
from typing import Any, Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
NAV_FILE = os.path.join(CONTENT, "navigation.json")

GA = "G-N9RETSEPQ9"
KEYWORDS = ("Dakhni, Dakkani, Dakhini, Deccan, Deccani, Hyderabad, Hyderabadi, Bidar, "
            "Gulbarga, Bijapur, Aurangabad, Bahmani, Qutb Shahi, Adil Shahi, Asaf Jahi, "
            "Nizam, Dakhni Urdu, Deccani Urdu, Deccan Sultanates, qawwali, dargah, Sufi "
            "shrines, biryani, haleem, Charminar, Golconda, Bidriware, Deccan heritage")
FALLBACK_COVER = "/assets/dakhni-pattern.png"

# Disqus shortname — register a free site at https://disqus.com/admin/create/
# and replace this placeholder before comments will load. Until it's replaced,
# comments() renders a quiet "not yet enabled" notice instead of a broken widget.
DISQUS_SHORTNAME = "dakhni"

PAGE_TYPES = {"home", "section_hub", "city_leaf", "saint_leaf", "institution_leaf", "heritage_leaf", "dynasty_leaf", "language_leaf", "sacred_site_leaf", "general_leaf"}
LEAF_PAGE_TYPES = PAGE_TYPES - {"home", "section_hub"}

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
                        if "ref" in item and not _is_ref_value(item["ref"]):
                            errors.append(f"{source}: blocks[{i}].items[{j}].ref must be a string or array of strings")
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
    if "references" in page:
        refs = page["references"]
        if not isinstance(refs, list):
            errors.append(f"{source}: field 'references' must be an array")
        else:
            seen_ids = set()
            for i, ref in enumerate(refs):
                if not isinstance(ref, dict):
                    errors.append(f"{source}: references[{i}] must be object")
                    continue
                rid = ref.get("id")
                if not isinstance(rid, str) or not rid:
                    errors.append(f"{source}: references[{i}].id must be a non-empty string")
                elif rid in seen_ids:
                    errors.append(f"{source}: references[{i}].id '{rid}' is duplicated")
                else:
                    seen_ids.add(rid)
                if not isinstance(ref.get("text"), str) or not ref.get("text"):
                    errors.append(f"{source}: references[{i}].text must be a non-empty string")
                if "url" in ref and not isinstance(ref["url"], str):
                    errors.append(f"{source}: references[{i}].url must be a string")
    if "link_terms" in page:
        terms = page["link_terms"]
        if not isinstance(terms, list) or any(not isinstance(t, str) or not t for t in terms):
            errors.append(f"{source}: field 'link_terms' must be an array of non-empty strings")
    if "redirect_from" in page:
        olds = page["redirect_from"]
        if not isinstance(olds, list) or any(not isinstance(u, str) or not u for u in olds):
            errors.append(f"{source}: field 'redirect_from' must be an array of non-empty strings")
    if "extra_scripts" in page:
        val = page["extra_scripts"]
        if not isinstance(val, list) or any(not isinstance(x, str) for x in val):
            errors.append(f"{source}: field 'extra_scripts' must be an array of strings")
    if "tags" in page:
        val = page["tags"]
        if not isinstance(val, list) or any(not isinstance(x, str) for x in val):
            errors.append(f"{source}: field 'tags' must be an array of strings")
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
    return errors


# --- Citations -------------------------------------------------------
# Content marks a claim as sourced with an inline `<cite data-ref="id"></cite>`
# marker (or, inside a `facts` block item, an item["ref"] field). The build
# turns each marker into a small numbered, superscript backlink and appends
# a closed-by-default References section listing everything actually cited,
# in order of first appearance -- the same convention Wikipedia uses.
CITE_RE = re.compile(r'<cite\s+data-ref="([^"]+)"\s*/?>(?:\s*</cite>)?')


def _is_ref_value(val: Any) -> bool:
    if isinstance(val, str):
        return True
    if isinstance(val, list):
        return all(isinstance(v, str) for v in val)
    return False


def _normalize_ref_ids(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    return list(val)


def collect_cite_ids(page: Dict[str, Any]) -> List[str]:
    ids: List[str] = []
    if not isinstance(page.get("blocks"), list):
        for m in CITE_RE.findall(page.get("body_html", "") or ""):
            ids.extend(m.split())
        return ids
    for block in page.get("blocks") or []:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        texts: List[str] = []
        if btype in ("html", "intro", "section"):
            texts.append(block.get("html", "") or "")
        elif btype == "cards":
            texts += [item.get("html", "") or "" for item in block.get("items", []) if isinstance(item, dict)]
        elif btype == "timeline":
            texts += [item.get("text", "") or "" for item in block.get("items", []) if isinstance(item, dict)]
        for t in texts:
            for m in CITE_RE.findall(t):
                ids.extend(m.split())
        if btype == "facts":
            for item in block.get("items", []):
                if isinstance(item, dict):
                    ids.extend(_normalize_ref_ids(item.get("ref")))
    return ids


def check_citations(page: Dict[str, Any], source: str) -> List[str]:
    errors: List[str] = []
    refs = page.get("references")
    if not isinstance(refs, list):
        refs = []
    declared = {r["id"] for r in refs if isinstance(r, dict) and isinstance(r.get("id"), str)}
    cited = set(collect_cite_ids(page))
    for rid in sorted(cited - declared):
        errors.append(f"{source}: cites reference '{rid}' which is not declared in 'references'")
    for rid in sorted(declared - cited):
        errors.append(f"{source}: declares reference '{rid}' in 'references' but it is never cited in the content")
    return errors


_OPEN_A_RE = re.compile(r"<a[\s>]")
_CLOSE_A_RE = re.compile(r"</a>")


def _inside_anchor(html: str, pos: int) -> bool:
    """True if `pos` falls inside an unclosed <a>...</a> in `html`.

    Citation markers normally render as <a href="#ref-..."> links, but a few
    pages embed them inside card grids where the whole card is itself an
    <a class="card">. Nesting an <a> inside an <a> is invalid HTML -- browsers
    respond by force-closing the outer anchor at that point, which silently
    breaks the card's layout. Markers found inside an existing anchor fall
    back to a plain, non-linking <span> instead.
    """
    return len(_OPEN_A_RE.findall(html, 0, pos)) > len(_CLOSE_A_RE.findall(html, 0, pos))


def render_citations(body_html: str, references: Optional[List[Dict[str, Any]]]) -> "tuple[str, str]":
    """Replace <cite data-ref="id"> markers with numbered superscript
    backlinks and return (new_body_html, references_section_html)."""
    ref_by_id = {r["id"]: r for r in (references or []) if isinstance(r, dict)}
    order: List[str] = []
    numbers: Dict[str, int] = {}
    counts: Dict[str, int] = {}

    def replace(m: "re.Match[str]") -> str:
        linkable = not _inside_anchor(body_html, m.start())
        parts = []
        for rid in m.group(1).split():
            counts[rid] = counts.get(rid, 0) + 1
            if rid not in numbers:
                numbers[rid] = len(order) + 1
                order.append(rid)
            anchor = f"cite_ref-{esc(rid)}-{counts[rid]}"
            if linkable:
                parts.append(f'<a href="#ref-{esc(rid)}" id="{anchor}">{numbers[rid]}</a>')
            else:
                parts.append(f'<span id="{anchor}">{numbers[rid]}</span>')
        return '<sup class="ref-mark">[' + ",".join(parts) + ']</sup>'

    new_html = CITE_RE.sub(replace, body_html)
    if not order:
        return new_html, ""

    items = []
    for rid in order:
        ref = ref_by_id.get(rid, {"text": rid})
        backlinks = " ".join(
            f'<a class="refs-back" href="#cite_ref-{esc(rid)}-{k}" aria-label="Jump back to citation {k}">^</a>'
            for k in range(1, counts[rid] + 1)
        )
        url = ref.get("url")
        url_html = (
            f' <a class="refs-url" href="{esc(url)}" target="_blank" rel="noopener noreferrer">↗</a>'
            if url else ""
        )
        items.append(
            f'<li id="ref-{esc(rid)}"><span class="refs-back-group">{backlinks}</span> '
            f'<span class="refs-text">{esc(ref.get("text", rid))}</span>{url_html}</li>'
        )
    refs_html = (
        '<section class="refs-wrap">'
        '<details><summary class="refs-summary">References</summary>'
        '<ol class="refs-list">' + "".join(items) + "</ol>"
        "</details></section>"
    )
    return new_html, refs_html


# --- Cross-links -------------------------------------------------------
# Any page can declare `link_terms`: exact-phrase names for itself (its own
# title and any natural variants -- "Bahmani", "the Bahmanis", etc). Any of
# those phrases found as plain text on another page becomes a subtle link
# to this page, the way Wikipedia links a topic once per article -- first
# occurrence only, never linking a page to itself, never nesting inside an
# existing <a> or a heading.
LINK_SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "script", "style"}
_LINK_TAG_SPLIT_RE = re.compile(r'''(<(?:=\s*'[^']*'|[^>"]|"[^"]*")*>)''')
_LINK_TAG_NAME_RE = re.compile(r'^</?\s*([a-zA-Z0-9]+)')


def collect_link_terms(pages: List[Dict[str, Any]]) -> "tuple[Dict[str, str], List[str]]":
    term_to_url: Dict[str, str] = {}
    errors: List[str] = []
    for page in pages:
        terms = page.get("link_terms")
        url = page.get("url")
        if not isinstance(terms, list) or not url:
            continue
        for term in terms:
            if not isinstance(term, str) or not term:
                continue
            existing = term_to_url.get(term)
            if existing is not None and existing != url:
                errors.append(
                    f"link_terms conflict: '{term}' is claimed by both {existing} and {url}"
                )
                continue
            term_to_url[term] = url
    return term_to_url, errors


def render_crosslinks(body_html: str, current_url: str, term_to_url: Dict[str, str]) -> str:
    candidates = {t: u for t, u in term_to_url.items() if u != current_url}
    if not candidates:
        return body_html
    # Longest term first, so a declared multi-word phrase wins over a
    # shorter one that happens to be its prefix (e.g. "Qutb Shahi Dynasty"
    # before "Qutb Shahi").
    terms_sorted = sorted(candidates, key=len, reverse=True)
    # Negative lookahead excludes domain-like continuations (e.g. the site's
    # own name "Dakhni.org") -- a real word boundary is never immediately
    # followed by "." + a letter with no space, so this never touches
    # ordinary sentence-ending punctuation.
    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(t) for t in terms_sorted) + r")\b(?!\.[A-Za-z])"
    )

    segments = _LINK_TAG_SPLIT_RE.split(body_html)
    linked_targets: set = set()
    skip_depth = 0
    out: List[str] = []
    for seg in segments:
        if seg.startswith("<") and seg.endswith(">"):
            m = _LINK_TAG_NAME_RE.match(seg)
            name = m.group(1).lower() if m else ""
            if name in LINK_SKIP_TAGS:
                skip_depth += -1 if seg.startswith("</") else 1
                skip_depth = max(skip_depth, 0)
            out.append(seg)
            continue
        if skip_depth > 0 or not seg:
            out.append(seg)
            continue

        def replace(m: "re.Match[str]") -> str:
            term = m.group(0)
            url = candidates[term]
            if url in linked_targets:
                return term
            linked_targets.add(url)
            return f'<a class="xref-link" href="{esc(url)}">{term}</a>'

        out.append(pattern.sub(replace, seg))
    return "".join(out)


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
    out.append(f'    <img class="nav-mark" src="{esc(brand["logo"])}" alt="" width="30" height="30"/>')
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
                cite = "".join(f'<cite data-ref="{esc(rid)}"></cite>' for rid in _normalize_ref_ids(item.get("ref")))
                out.append(f'<div class="fact"><span class="fact-key">{key}</span><span class="fact-val">{val}{cite}</span></div>')
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

AI_NOTICE = '''<div id="ai-notice" class="ai-notice" role="status" hidden>
  <div class="ai-notice-inner">
    <p class="ai-notice-text">This site's content is compiled with AI assistance from historical sources — we recommend verifying important facts independently.<a href="/ai-policy/">Read more</a></p>
    <button class="ai-notice-close" id="ai-notice-close" type="button" aria-label="Dismiss this notice">&times;</button>
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

    By default, any page whose URL is another page's parent (hub_urls) is
    excluded from ever appearing in a subnav group -- it doesn't get its
    own Prev/Next, and it isn't listed as a sibling in its own parent's
    group either. That's correct for a pure listing page like
    content/heritage.json, which exists only to host its 7 pillar
    children and was never a "sibling" of anything itself.

    It's wrong, though, for a page that is itself a normal, contentful
    sibling in its parent's tour *and* separately hosts its own children
    -- e.g. content/heritage/crafts.json is one of the 7 heritage pillars
    (wants its own Prev/Next among the other 6) while also being the
    parent of content/heritage/crafts/bidriware.json (which wants its own
    Prev/Next among its own craft siblings, with index_href pointing at
    crafts, not all the way up at heritage). Such a page opts in with
    `"nested_hub": true`, which keeps it in its own parent's group despite
    having children of its own.
    """
    url_to_page = {p["url"]: p for p in pages if p.get("url")}
    hub_urls = {parent_url(p["url"]) for p in pages if p.get("url") and parent_url(p["url"]) != p["url"]}

    from collections import defaultdict
    groups = defaultdict(list)
    for page in pages:
        url = page.get("url", "")
        if not url or page.get("level") == "home":
            continue
        if (url in hub_urls and not page.get("nested_hub")) or page.get("no_subnav"):
            continue  # hub pages (unless nested_hub), and pages opted out via no_subnav, don't get subnav
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

def breadcrumb_items(page: Dict[str, Any], url_to_page: Dict[str, Any]) -> List[Dict[str, str]]:
    """Ordered [{name, url}] from Home down to the current page (url="" for the current page)."""
    url = page["url"]
    parts = [p for p in url.strip("/").split("/") if p]
    items = [{"name": "Home", "url": "/"}]
    for i in range(len(parts) - 1):
        href = "/" + "/".join(parts[: i + 1]) + "/"
        hub = url_to_page.get(href)
        label = hub["title"] if hub else parts[i].replace("-", " ").title()
        items.append({"name": label, "url": href})
    items.append({"name": page["title"], "url": ""})
    return items


def render_auto_crumb(page: Dict[str, Any], url_to_page: Dict[str, Any]) -> str:
    items = breadcrumb_items(page, url_to_page)
    sep = '<span class="crumb-sep">›</span>'
    parts = [esc(it["name"]) if not it["url"] else f'<a href="{esc(it["url"])}">{esc(it["name"])}</a>' for it in items]
    return sep.join(parts)


def breadcrumb_jsonld(page: Dict[str, Any], url_to_page: Dict[str, Any]) -> str:
    items = breadcrumb_items(page, url_to_page)
    if len(items) < 2:
        return ""
    entries = []
    for i, it in enumerate(items):
        entry = {"@type": "ListItem", "position": i + 1, "name": it["name"]}
        if it["url"]:
            entry["item"] = "https://dakhni.org" + it["url"]
        entries.append(entry)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": entries}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'

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
  <div class="flag-banner"><img src="/assets/dakhni-org-logo-256.png" alt="Dakhni.org" width="256" height="256" loading="lazy"/></div>
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
    <li><a href="/ai-policy/">AI Policy</a></li>
  </ul>
  <p class="ft-copy">© <span id="year">2025</span> Dakhni.org · {esc(ded)} · Built with love for the Deccan</p>
</footer>'''


def comments(page):
    if DISQUS_SHORTNAME == "REPLACE_WITH_YOUR_DISQUS_SHORTNAME":
        return '''<section class="comments-wrap" id="comments">
  <div class="comments-ornament">✦</div>
  <header class="comments-hdr">
    <span class="comments-eyebrow">Join the Conversation</span>
    <h2 class="comments-title">Comments</h2>
  </header>
  <div class="comments-panel">
    <p class="comments-pending">Comments are not yet enabled on this page.</p>
  </div>
</section>'''
    url = page["url"]
    page_url = json.dumps("https://dakhni.org" + url)
    page_id = json.dumps(url)
    return f'''<section class="comments-wrap" id="comments">
  <div class="comments-ornament">✦</div>
  <header class="comments-hdr">
    <span class="comments-eyebrow">Join the Conversation</span>
    <h2 class="comments-title">Comments</h2>
  </header>
  <div class="comments-panel">
    <div id="disqus_thread"></div>
    <script>
      var disqus_config = function () {{
        this.page.url = {page_url};
        this.page.identifier = {page_id};
      }};
      (function() {{
        var d = document, s = d.createElement('script');
        s.src = 'https://{DISQUS_SHORTNAME}.disqus.com/embed.js';
        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
      }})();
    </script>
    <noscript class="comments-noscript">Please enable JavaScript to view <a href="https://disqus.com/?ref_noscript">comments</a>.</noscript>
  </div>
  <script id="comments-count-script" src="//{DISQUS_SHORTNAME}.disqus.com/count.js" async></script>
</section>'''


def head(page, url_to_page: Dict[str, Any]):
    url = page["url"]
    canonical = "https://dakhni.org" + url
    title = page["title"]
    full_title = "Dakhni.org — Heritage of the Deccan" if url == "/" else f'{title} — Dakhni.org'
    desc = page.get("description", "")
    cover = page.get("cover") or ""
    og_img = ("https://dakhni.org" + cover) if cover.startswith("/") else (cover or "https://dakhni.org/assets/icon-512.png")
    page_tags = page.get("tags", [])
    all_keywords = KEYWORDS + (", " + ", ".join(page_tags) if page_tags else "")
    jsonld = [] if url == "/" else [breadcrumb_jsonld(page, url_to_page)]
    if url == "/":
        site_ld = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Dakhni.org",
            "alternateName": "Dakhni.org — Heritage of the Deccan",
            "url": "https://dakhni.org/",
            "description": desc,
            "publisher": {
                "@type": "Organization",
                "name": "Dakhni.org",
                "url": "https://dakhni.org/",
                "logo": "https://dakhni.org/assets/icon-512.png",
            },
        }
        jsonld.append(f'<script type="application/ld+json">{json.dumps(site_ld, ensure_ascii=False)}</script>')
    jsonld_html = "\n  ".join(j for j in jsonld if j)
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
  <link rel="icon" href="/assets/favicon.ico" sizes="32x32"/>
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png"/>
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"/>
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png"/>
  <link rel="manifest" href="/assets/site.webmanifest"/>
  <meta name="description" content="{esc(desc)}"/>
  <meta name="keywords" content="{esc(all_keywords)}"/>
  <meta name="author" content="Dakhni.org"/>
  <meta name="robots" content="index, follow, max-image-preview:large"/>
  <meta name="theme-color" content="#1A1814"/>
  <link rel="canonical" href="{canonical}"/>
  <meta property="og:type" content="website"/>
  <meta property="og:site_name" content="Dakhni.org"/>
  <meta property="og:locale" content="en_US"/>
  <meta property="og:title" content="{esc(full_title)}"/>
  <meta property="og:description" content="{esc(desc)}"/>
  <meta property="og:url" content="{canonical}"/>
  <meta property="og:image" content="{esc(og_img)}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="{esc(full_title)}"/>
  <meta name="twitter:description" content="{esc(desc)}"/>
  <meta name="twitter:image" content="{esc(og_img)}"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500&family=Lateef:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/assets/site.css"/>
  {jsonld_html}
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


def render(page, nav_html, url_to_page, subnav_map, term_to_url=None):
    body = render_blocks(page)
    body, refs_html = render_citations(body, page.get("references"))
    body = render_crosslinks(body, page.get("url", ""), term_to_url or {})
    crumb = page.get("crumb_html") or render_auto_crumb(page, url_to_page)
    subnav = page.get("subnav_html") or render_auto_subnav(page, subnav_map, url_to_page)
    out = [head(page, url_to_page), "<body>", AI_NOTICE, nav_html]
    if page.get("level") == "home":
        out.append(page.get("hero_html", ""))
        out.append('<main class="page-main page-main--home">')
        out.append(body)
        if refs_html:
            out.append(refs_html)
        out.append('</main>')
    else:
        out.append(hero(page))
        out.append('<main class="page-main">')
        if crumb:
            out.append(f'  <p class="crumb">{crumb}</p>')
        out.append(body)
        if refs_html:
            out.append(refs_html)
        out.append('</main>')
    if page.get("page_type") in LEAF_PAGE_TYPES:
        out.append(comments(page))
    if subnav:
        out.append(subnav)
    out.append(footer(page.get("dedication")))
    out.append(SEARCH)
    for sc in page.get("extra_scripts", []):
        out.append("<script>\n" + sc + "\n</script>")
    out.append('<script defer src="/assets/site.js"></script>')
    out.append("</body>\n</html>")
    return "\n".join(out) + "\n"


def write_sitemap(pages: List[Dict[str, Any]], page_files: Dict[str, str]) -> None:
    """Regenerate sitemap.xml from the actual content set so it can never
    drift out of sync with the pages the build produces (it previously did:
    two live pages were missing from the hand-maintained file).

    lastmod comes from `git log` on each source file, not filesystem mtime.
    Git doesn't preserve mtimes across clones -- every fresh checkout
    (including every CI run) stamps files with the checkout time, so an
    mtime-based lastmod would regenerate differently on every machine and
    never match what's actually committed."""
    import datetime
    import subprocess

    today = datetime.date.today().isoformat()

    def git_lastmod(jf: str) -> str:
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%ad", "--date=short", "--", jf],
                cwd=ROOT, capture_output=True, text=True, timeout=5,
            )
            date = out.stdout.strip()
            return date if date else today
        except Exception:
            return today

    def priority_freq(page):
        pt = page.get("page_type")
        if pt == "home":
            return "1.0", "monthly"
        if pt == "general_leaf":
            return "0.5", "yearly"
        if pt == "section_hub":
            return "0.9", "monthly"
        return "0.7", "monthly"

    entries = []
    for page in sorted(pages, key=lambda p: p.get("url", "")):
        url = page.get("url")
        if not url:
            continue
        jf = page_files.get(url)
        lastmod = git_lastmod(jf) if jf else today
        priority, freq = priority_freq(page)
        entries.append(
            f'  <url><loc>https://dakhni.org{esc(url)}</loc><lastmod>{lastmod}</lastmod>'
            f'<changefreq>{freq}</changefreq><priority>{priority}</priority></url>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)


REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Redirecting…</title>
<link rel="canonical" href="{canonical}"/>
<meta http-equiv="refresh" content="0; url={new_url}"/>
<meta name="robots" content="noindex"/>
</head>
<body>
<p>This page has moved to <a href="{new_url}">{new_url}</a>.</p>
</body>
</html>
"""


def validate_redirects(pages: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    live_urls = {p["url"] for p in pages if p.get("url")}
    for page in pages:
        for old_url in page.get("redirect_from") or []:
            if old_url in live_urls:
                errors.append(
                    f"redirect_from conflict: '{old_url}' on {page.get('url')} is still a live page URL"
                )
    return errors


def write_redirects(pages: List[Dict[str, Any]]) -> List[str]:
    """A page can declare `redirect_from`: a list of old URLs it used to
    live at. For each one, write a small static redirect stub (meta
    refresh + canonical, noindex) at the old output path, so a moved
    page's previously published URL doesn't start 404ing -- for
    visitors following a bookmark, and for search engines that already
    indexed it. Returns the list of URLs actually written, for the
    build summary."""
    live_urls = {p["url"] for p in pages if p.get("url")}
    written: List[str] = []
    for page in pages:
        new_url = page.get("url")
        if not new_url:
            continue
        for old_url in page.get("redirect_from") or []:
            if old_url in live_urls:
                continue  # a real page already owns this URL; never clobber it
            canonical = "https://dakhni.org" + new_url
            html = REDIRECT_TEMPLATE.format(canonical=esc(canonical), new_url=esc(new_url))
            rel = old_url.strip("/")
            outdir = os.path.join(ROOT, rel) if rel else ROOT
            os.makedirs(outdir, exist_ok=True)
            with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(html)
            written.append(old_url)
    return written


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
    page_files: Dict[str, str] = {}
    errors: List[str] = []
    for jf in sorted(glob.glob(os.path.join(CONTENT, "**", "*.json"), recursive=True)):
        if os.path.abspath(jf) == os.path.abspath(NAV_FILE):
            continue
        with open(jf, encoding="utf-8") as fh:
            page = json.load(fh)
        pages.append(page)
        if page.get("url"):
            page_files[page["url"]] = jf
        rel_source = os.path.relpath(jf, ROOT)
        errors.extend(validate_page(page, rel_source))
        errors.extend(check_citations(page, rel_source))
    term_to_url, link_term_errors = collect_link_terms(pages)
    errors.extend(link_term_errors)
    errors.extend(validate_redirects(pages))
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
            fh.write(render(page, nav_html, url_to_page, subnav_map, term_to_url))
        n += 1
    write_sitemap(pages, page_files)
    redirects = write_redirects(pages)
    print(f"Rendered {n} pages")
    if redirects:
        print(f"Wrote {len(redirects)} redirect stub(s): {', '.join(redirects)}")


if __name__ == "__main__":
    main()
