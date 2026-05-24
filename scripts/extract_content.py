#!/usr/bin/env python3
"""One-time migration: parse each existing hand-written page into a content
JSON file under content/, which scripts/build_site.py then renders back into
a normalised page. The body content region is captured verbatim so no prose
is lost; hero, cover image, breadcrumb, subnav and footer dedication are
lifted into fields.
"""
import glob
import html as _html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")

SECTION_NAMES = {
    "heritage": "Heritage", "dynasties": "Dynasties", "language": "Language",
    "sufism": "Sufism", "cities": "Cities", "landmarks": "Landmarks",
    "sacred-sites": "Sacred Sites", "about": "About",
}


def url_for(rel):
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    return "/" + rel[:-len("index.html")] if rel.endswith("/index.html") else "/" + rel


def section_for(rel):
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return "Home"
    return SECTION_NAMES.get(rel.split("/")[0], rel.split("/")[0].replace("-", " ").title())


def find(rx, s, g=1, flags=re.S | re.I):
    m = re.search(rx, s, flags)
    return m.group(g).strip() if m else None


def inner_block(s, start_tag_rx):
    """Return (full, inner) for the first element matching start_tag_rx,
    balancing nested same-name tags."""
    m = re.search(start_tag_rx, s, re.S | re.I)
    if not m:
        return None, None
    tag = re.match(r"<(\w+)", m.group(0)).group(1)
    i = m.end()
    depth = 1
    for mm in re.finditer(rf"<(/?){tag}\b", s[i:], re.I):
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            end = i + mm.start()
            close = s.find(">", i + mm.start()) + 1
            return s[m.start():close], s[i:end]
    return None, None


def extract(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    s = open(path, encoding="utf-8").read()
    url = url_for(rel)
    page = {"url": url, "section": section_for(rel)}

    title = find(r"<title>(.*?)</title>", s) or ""
    title = re.split(r"\s+[—|]\s+", _html.unescape(title))[0].strip()
    page["title"] = "Home" if url == "/" else title
    page["description"] = _html.unescape(find(r'<meta name="description" content="(.*?)"', s) or "")

    # footer dedication: © <span>..</span> Dakhni.org · DEDICATION · Built with love...
    ded = find(r'class="ft-copy">.*?Dakhni\.org\s*·\s*(.*?)\s*·\s*Built with love', s)
    if ded:
        page["dedication"] = _html.unescape(re.sub(r"<[^>]+>", "", ded)).strip()

    body_region = s[s.index("<body>") + len("<body>"):]
    # cut nav off the front
    nav_end = body_region.find("</nav>")
    after_nav = body_region[nav_end + len("</nav>"):] if nav_end >= 0 else body_region
    # strip the END SHARED NAV comment if present
    after_nav = re.sub(r"^\s*<!--.*?-->", "", after_nav, count=1, flags=re.S)

    # HERO
    home = url == "/"
    hero_full, hero_inner = (None, None)
    for rx in [r'<header class="(?:city-hero|page-hero)(?:\s[^"]*)?"[^>]*>',
               r'<section class="(?:city-hero|page-hero)(?:\s[^"]*)?"[^>]*>',
               r'<div class="(?:city-hero|page-hero)(?:\s[^"]*)?"[^>]*>',
               r'<section class="hero(?:\s[^"]*)?"[^>]*>']:
        hero_full, hero_inner = inner_block(after_nav, rx)
        if hero_full:
            break
    if home and hero_full:
        page["level"] = "home"
        page["hero_html"] = hero_full
    elif hero_inner is not None:
        page["eyebrow"] = re.sub(r"<[^>]+>", "", find(r'class="[\w-]*hero-eyebrow">(.*?)</span>', hero_inner) or "") or None
        urdu = find(r'class="[\w-]*hero-urdu">(.*?)</p>', hero_inner)
        page["urdu"] = re.sub(r"<[^>]+>", "", urdu).strip() if urdu else None
        th = find(r'class="[\w-]*hero-title">(.*?)</h1>', hero_inner)
        page["title_html"] = th.strip() if th else None
        sub = find(r'class="[\w-]*hero-sub">(.*?)</p>', hero_inner)
        page["subtitle"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", sub)).strip() if sub else None
    # cover: url() inside the .city-hero CSS rule of this page
    cover = find(r"\.city-hero\s*\{[^}]*url\((['\"]?)([^'\")]+)\1\)", s, g=2)
    if cover:
        page["cover"] = cover

    # body region = everything after the hero, up to subnav-or-footer
    rest = after_nav[after_nav.index(hero_full) + len(hero_full):] if hero_full else after_nav
    # footer comment or <footer>
    fm = re.search(r"<!--\s*=+\s*SHARED FOOTER", rest) or re.search(r"<footer\b", rest)
    body = rest[:fm.start()] if fm else rest
    # subnav out of the body
    sn_full, _ = inner_block(body, r'<nav class="subnav"[^>]*>')
    if sn_full:
        page["subnav_html"] = sn_full.strip()
        body = body.replace(sn_full, "")
    # breadcrumb out of the body
    crumb = find(r'<p class="crumb">(.*?)</p>', body)
    if crumb:
        page["crumb_html"] = crumb.strip()
        body = re.sub(r'<p class="crumb">.*?</p>', "", body, count=1, flags=re.S)
    # strip the END/START nav comment leftovers and the page-hero comment
    body = re.sub(r"<!--\s*=+.*?=+\s*-->", "", body, flags=re.S)
    page["body_html"] = body.strip()

    # extra (non-shared) inline scripts in the body region (e.g. homepage quiz)
    shared_markers = ("dataLayer", "disclosure_seen", "ds-search-input", "aria-current",
                      "IntersectionObserver")
    extra = []
    for sc in re.findall(r"<script>(.*?)</script>", rest, re.S):
        if not any(mk in sc for mk in shared_markers):
            extra.append(sc.strip())
    if extra:
        page["extra_scripts"] = extra

    return {k: v for k, v in page.items() if v is not None}


def main():
    os.makedirs(CONTENT, exist_ok=True)
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        page = extract(path)
        rel = page["url"].strip("/") or "home"
        out = os.path.join(CONTENT, rel + ".json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(page, fh, ensure_ascii=False, indent=1)
        n += 1
    print(f"Extracted {n} content files")


if __name__ == "__main__":
    main()
