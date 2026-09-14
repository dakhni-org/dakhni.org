#!/usr/bin/env python3
"""One-time migration of Dakhni.org branding from raster logo assets to SVG."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = "/assets/dakhni-org-logo.svg"
SVG_URL = "https://dakhni.org/assets/dakhni-org-logo.svg"
OLD_LOGO_PATH = "/assets/dakhni-org-logo-256.png"
OLD_SOCIAL_URL = "https://dakhni.org/assets/icon-512.png"

build_path = ROOT / "scripts" / "build_site.py"
build = build_path.read_text(encoding="utf-8")

old_favicon_block = '''  <link rel="icon" href="/assets/favicon.ico" sizes="32x32"/>
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png"/>
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"/>
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png"/>
'''
new_favicon_block = f'''  <link rel="icon" type="image/svg+xml" href="{SVG_PATH}"/>
'''

build = build.replace(old_favicon_block, new_favicon_block)
build = build.replace(OLD_LOGO_PATH, SVG_PATH)
build = build.replace(OLD_SOCIAL_URL, SVG_URL)
build_path.write_text(build, encoding="utf-8")

# Navigation and the homepage hero store their logo path in JSON source.
# Replace only the known legacy logo path so unrelated PNG/JPG content remains untouched.
for content_path in (ROOT / "content").rglob("*.json"):
    text = content_path.read_text(encoding="utf-8")
    updated = text.replace(OLD_LOGO_PATH, SVG_PATH).replace(OLD_SOCIAL_URL, SVG_URL)
    if updated != text:
        content_path.write_text(updated, encoding="utf-8")

manifest_path = ROOT / "assets" / "site.webmanifest"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["icons"] = [
    {"src": SVG_PATH, "sizes": "any", "type": "image/svg+xml"}
]
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

readme_path = ROOT / "assets" / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    "- `dakhni-org-logo.png` — site logo / favicon (`/assets/dakhni-org-logo.png`)",
    "- `dakhni-org-logo.svg` — canonical site logo and favicon (`/assets/dakhni-org-logo.svg`)",
)
readme_path.write_text(readme, encoding="utf-8")

for filename in [
    "dakhni-org-logo-256.png",
    "dakhni-org-logo.png",
    "favicon-16.png",
    "favicon-32.png",
    "favicon-48.png",
    "favicon.ico",
    "apple-touch-icon.png",
    "icon-192.png",
    "icon-512.png",
]:
    (ROOT / "assets" / filename).unlink(missing_ok=True)

print("Migrated site branding to the canonical SVG logo.")
