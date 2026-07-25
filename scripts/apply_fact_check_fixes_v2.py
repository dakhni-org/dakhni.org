#!/usr/bin/env python3
"""Run the fact-check correction pass deterministically and idempotently.

This wrapper preserves the correction catalogue in apply_fact_check_fixes.py,
but fixes two execution problems in the original runner:
1. required file-specific replacements must run before broad global replacements;
2. a repeated run must accept already-corrected text rather than fail.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apply_fact_check_fixes import (
    GLOBAL_REPLACEMENTS,
    PATH_REPLACEMENTS,
    REFERENCE_ADDITIONS,
    ROOT,
    add_references,
    remove_unverified_synagogue_card,
    replace_strings,
)


def contains_string(value: Any, needle: str) -> bool:
    """Return whether a decoded JSON value contains needle in any string."""
    if isinstance(value, str):
        return needle in value
    if isinstance(value, list):
        return any(contains_string(item, needle) for item in value)
    if isinstance(value, dict):
        return any(contains_string(item, needle) for item in value.values())
    return False


def update_json(path: Path) -> tuple[int, list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    original = path.read_text(encoding="utf-8")
    doc = json.loads(original)
    counts: dict[str, int] = {}

    # Exact corrections take precedence over broad substitutions. Several exact
    # phrases contain text also present in GLOBAL_REPLACEMENTS.
    required = PATH_REPLACEMENTS.get(rel, [])
    doc = replace_strings(doc, required, counts)

    missing = [
        old
        for old, new in required
        if counts.get(old, 0) == 0 and not contains_string(doc, new)
    ]
    if missing:
        return 0, [
            f"{rel}: neither original nor corrected phrase found: {old!r}"
            for old in missing
        ]

    doc = replace_strings(doc, GLOBAL_REPLACEMENTS, counts)

    if rel == "content/sacred-sites/religious-structures.json":
        doc = remove_unverified_synagogue_card(doc)

    add_references(doc, REFERENCE_ADDITIONS.get(rel, []))
    rendered = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if rendered != original:
        path.write_text(rendered, encoding="utf-8")

    return sum(counts.values()), []


def update_readme() -> int:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    replacements = [
        (
            "the region that gave the world its first form of Urdu",
            "the region that helped shape one of the earliest literary forms of Urdu/Hindustani",
        ),
        (
            "sitemap.xml             # Lists all 62 pages",
            "sitemap.xml             # Lists all generated pages",
        ),
    ]

    changed = 0
    for old, new in replacements:
        if old in text:
            changed += text.count(old)
            text = text.replace(old, new)
        elif new not in text:
            raise RuntimeError(
                f"README.md: neither original nor corrected phrase found: {old!r}"
            )

    path.write_text(text, encoding="utf-8")
    return changed


def main() -> None:
    errors: list[str] = []
    total = 0

    for path in sorted((ROOT / "content").rglob("*.json")):
        count, file_errors = update_json(path)
        total += count
        errors.extend(file_errors)

    total += update_readme()

    if errors:
        raise SystemExit("Fact-check correction pass failed:\n- " + "\n- ".join(errors))

    print(f"Applied {total} fact-check text corrections across canonical content.")


if __name__ == "__main__":
    main()
