#!/usr/bin/env python3
"""Validate generated canonical pages before publishing to GitHub Pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import sys
ROOT = Path(__file__).resolve().parents[1]
HOST = "dakhni.org"
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canon = []
        self.meta = {}
        self.h1 = 0
        self.titles = []
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and "canonical" in a.get("rel","").split():
            self.canon.append(a.get("href"))
        if tag == "meta" and "name" in a:
            self.meta[a["name"].lower()] = a.get("content","")
        if tag == "h1": self.h1 += 1
        if tag == "title": self.in_title = True
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.titles.append(data)
def main():
    ns = {"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [e.text for e in ET.parse(ROOT/"sitemap.xml").findall("s:url/s:loc",ns)]
    errors, titles, descriptions = [], {}, {}
    if len(urls) != len(set(urls)): errors.append("Duplicate sitemap URLs")
    for url in urls:
        u = urlsplit(url or "")
        if u.scheme != "https" or u.netloc != HOST or not u.path.endswith("/") or u.query or u.fragment:
            errors.append(f"Invalid sitemap URL: {url}")
            continue
        path = ROOT / u.path.strip("/") / "index.html"
        if not path.is_file():
            errors.append(f"{url}: missing generated HTML")
            continue
        raw = path.read_text(encoding="utf-8")
        p = Page()
        p.feed(raw)
        if p.canon != [url]: errors.append(f"{url}: canonical mismatch {p.canon}")
        if "noindex" in p.meta.get("robots","").lower(): errors.append(f"{url}: noindex in sitemap")
        if p.h1 != 1: errors.append(f"{url}: expected one H1, found {p.h1}")
        title = "".join(p.titles).strip()
        desc = p.meta.get("description","").strip()
        for value, seen, label in [(title,titles,"title"),(desc,descriptions,"description")]:
            if not value: errors.append(f"{url}: missing {label}")
            elif value in seen: errors.append(f"{url}: duplicate {label} with {seen[value]}")
            else: seen[value] = url
        if "\u2014" in raw or "&mdash;" in raw or "&#8212;" in raw or "&#x2014;" in raw.lower():
            errors.append(f"{url}: em dash remains")
    print(f"Checked {len(urls)} sitemap URLs; {len(errors)} findings.")
    for error in errors: print(error)
    return bool(errors)
if __name__ == "__main__":
    sys.exit(main())
