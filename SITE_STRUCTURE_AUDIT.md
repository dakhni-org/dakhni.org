# Site Structure & Scalability Audit

_Date: 2026-05-25_

## Current architecture (what is already good)

- The site is already generated from JSON content files under `content/` via `scripts/build_site.py`, which creates a shared shell (head, nav, hero/footer/search/disclosure) for all pages.
- This means broad visual consistency is mostly centralized in `assets/site.css` and `assets/site.js`.
- Re-running the generator updates all pages, indicating a single-source rendering workflow.

## Inconsistencies / scalability risks found

1. **Content is stored as raw HTML (`body_html`, `subnav_html`, `crumb_html`)**
   - This bypasses structural safeguards and makes form-based authoring difficult.
   - It also allows style drift (different wrappers/classes per page) as the site grows.

2. **No explicit schema validation for content JSON**
   - `build_site.py` assumes fields exist and are valid.
   - Missing or malformed fields can silently degrade layout or metadata.

3. **Navigation is hard-coded in the generator**
   - `NAV` is embedded as a large HTML string.
   - Adding new sections/pages requires script edits, not only content updates.

4. **Page-type conventions are implicit**
   - There is no typed model for `hub` / `subcategory` / `leaf` pages.
   - Authors must manually compose the right `body_html` blocks.

5. **Leaf-page composition is not componentized**
   - Repeating patterns (e.g., timeline cards, facts, related links, galleries) are not represented as reusable JSON blocks.

## Recommended enhancements (for form-driven scalability)

### 1) Move from HTML blobs to block-based JSON

Introduce structured `blocks` arrays instead of long `body_html` strings:

```json
{
  "url": "/cities/hyderabad/",
  "title": "Hyderabad",
  "page_type": "leaf_city",
  "blocks": [
    {"type": "intro", "text": "..."},
    {"type": "facts", "items": [{"label": "Founded", "value": "1591"}]},
    {"type": "landmarks", "cards": [...]},
    {"type": "related_links", "links": [...]}
  ]
}
```

Then render each `type` in `build_site.py` with fixed templates/classes.

### 2) Add JSON Schema validation in build step

- Add a schema per page type (`schemas/home.schema.json`, `schemas/city.schema.json`, etc.).
- Validate all content before rendering and fail fast with clear errors.
- This unlocks “simple form” pipelines because fields become predictable.

### 3) Externalize navigation and taxonomy

- Move nav structure to `content/navigation.json`.
- Generate desktop nav + mobile nav from the same file.
- Enables adding a section/page without touching Python templates.

### 4) Define explicit page models

Use `page_type` with required block sets:

- `home`
- `section_hub` (e.g., `/heritage/`)
- `section_leaf` (e.g., `/heritage/music/`)
- `person_leaf` (e.g., `/sufism/shah-raju/`)
- `city_leaf`

This reduces manual composition and enforces structure.

### 5) Add content authoring forms (thin CMS layer)

- Build a minimal admin form generator from JSON Schemas.
- Editors fill fields; system writes valid JSON; renderer outputs styled pages.
- Start with the most repeated leaf type (cities or institutions).

### 6) Add quality gates

- Run `build_site.py` + schema validation in CI.
- Add HTML lint + link-check + image alt checks.
- Prevent regressions when many contributors add content.

## Suggested implementation roadmap

1. Add schemas + validation (no visual changes).
2. Add `navigation.json` and generate nav from data.
3. Add block renderer while supporting legacy `body_html` for migration.
4. Migrate high-volume sections first (cities, institutions).
5. Remove legacy raw-HTML fields when migration completes.

## Optional homepage grid improvement note

For `.heartland-grid`, if strict visual rhythm is desired regardless of text length,
add a minimum card height token (e.g., `--card-min-h`) and clamp subtitle lines to keep all
rows balanced even with longer labels.
