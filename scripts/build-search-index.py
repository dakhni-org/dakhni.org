#!/usr/bin/env python3
"""Build a client-side search index from the static HTML pages.

Walks every *.html file, extracts a clean page title, the top-level
section and the meta description, and writes assets/search-index.json
(a compact array consumed by the in-nav search overlay).

Run from the repo root:  python3 scripts/build-search-index.py
"""
import glob
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', re.I | re.S
)

SECTION_NAMES = {
    "heritage": "Heritage",
    "dynasties": "Dynasties",
    "language": "Language",
    "sufism": "Sufism",
    "cities": "Cities",
    "landmarks": "Landmarks",
    "sacred-sites": "Sacred Sites",
}


def clean_title(raw):
    raw = html.unescape(raw).strip()
    # Page name is the text before the first " — " or " | " separator.
    raw = re.split(r"\s+[—|]\s+", raw)[0]
    return raw.strip()


def url_for(relpath):
    relpath = relpath.replace(os.sep, "/")
    if relpath == "index.html":
        return "/"
    if relpath.endswith("/index.html"):
        return "/" + relpath[: -len("index.html")]
    return "/" + relpath


def section_for(relpath):
    relpath = relpath.replace(os.sep, "/")
    if relpath == "index.html":
        return "Home"
    top = relpath.split("/")[0]
    return SECTION_NAMES.get(top, top.replace("-", " ").title())


def main():
    entries = []
    for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        tm = TITLE_RE.search(src)
        if not tm:
            continue
        title = clean_title(tm.group(1))
        dm = DESC_RE.search(src)
        desc = html.unescape(dm.group(1)).strip() if dm else ""
        rel_norm = rel.replace(os.sep, "/")
        title = "Home" if rel_norm == "index.html" else title
        entries.append(
            {"u": url_for(rel), "t": title, "s": section_for(rel), "d": desc}
        )

    out = os.path.join(ROOT, "assets", "search-index.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    print(f"Wrote {len(entries)} entries to {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
