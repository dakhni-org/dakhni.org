#!/usr/bin/env python3
"""Step 3 migration: extract timeline HTML into structured timeline blocks."""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")

TIMELINE_SECTION_RE = re.compile(
    r'<section[^>]*class="timeline-wrap"[^>]*>.*?</section>',
    re.DOTALL
)
TIMELINE_EYEBROW_RE = re.compile(
    r'<span[^>]*class="timeline-eyebrow"[^>]*>(.*?)</span>',
    re.DOTALL
)
TIMELINE_TITLE_RE = re.compile(
    r'<h2[^>]*class="timeline-title"[^>]*>(.*?)</h2>',
    re.DOTALL
)
TL_ITEM_RE = re.compile(
    r'<li[^>]*class="tl-item[^"]*"[^>]*>\s*<span[^>]*class="tl-year"[^>]*>(.*?)</span>\s*<span[^>]*class="tl-text"[^>]*>(.*?)</span>\s*</li>',
    re.DOTALL
)


def extract_timeline_from_html(html_str):
    """Return (timeline_block, remaining_html) or (None, html_str) if no timeline."""
    m = TIMELINE_SECTION_RE.search(html_str)
    if not m:
        return None, html_str
    section_html = m.group(0)

    eyebrow = ""
    title = ""
    em = TIMELINE_EYEBROW_RE.search(section_html)
    if em:
        eyebrow = em.group(1).strip()
    tm = TIMELINE_TITLE_RE.search(section_html)
    if tm:
        title = tm.group(1).strip()

    items = []
    for item_m in TL_ITEM_RE.finditer(section_html):
        year = item_m.group(1).strip()
        text = item_m.group(2).strip()
        items.append({"year": year, "text": text})

    timeline_block = {"type": "timeline", "eyebrow": eyebrow, "title": title, "items": items}

    remaining = html_str[:m.start()] + html_str[m.end():]
    remaining = remaining.strip()
    return timeline_block, remaining


def process_file(filepath):
    rel = os.path.relpath(filepath, ROOT)
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    changed = False

    # Case 1: page uses body_html with timeline
    body_html = data.get("body_html", "")
    if body_html and ("timeline-wrap" in body_html or "tl-list" in body_html):
        tl_block, remaining = extract_timeline_from_html(body_html)
        if tl_block and tl_block["items"]:
            rest_block = {"type": "html", "html": remaining}
            new_data = {}
            for k, v in data.items():
                if k == "body_html":
                    new_data["blocks"] = [rest_block, tl_block]
                else:
                    new_data[k] = v
            data = new_data
            changed = True
            print(f"Migrated body_html timeline: {rel}")

    # Case 2: page uses blocks with html blocks containing timeline
    elif "blocks" in data and isinstance(data["blocks"], list):
        new_blocks = []
        any_changed = False
        for block in data["blocks"]:
            if block.get("type") == "html" and ("timeline-wrap" in block.get("html", "") or "tl-list" in block.get("html", "")):
                tl_block, remaining = extract_timeline_from_html(block["html"])
                if tl_block and tl_block["items"]:
                    if remaining:
                        new_blocks.append({"type": "html", "html": remaining})
                    new_blocks.append(tl_block)
                    any_changed = True
                    continue
            new_blocks.append(block)
        if any_changed:
            data["blocks"] = new_blocks
            changed = True
            print(f"Migrated blocks timeline: {rel}")

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


all_files = sorted(glob.glob(os.path.join(CONTENT, "**", "*.json"), recursive=True))
nav_file = os.path.join(CONTENT, "navigation.json")

for filepath in all_files:
    if os.path.abspath(filepath) == os.path.abspath(nav_file):
        continue
    process_file(filepath)

print("Done.")
