# CLAUDE.md — dakhni.org

## What this site is

Dakhni.org is a static digital archive of Deccan heritage (1347–1948): dynasties, cities, Sufi saints, language, architecture, cuisine, and sacred sites. Maintained by Syed Azhar Farhan.

## Stack

| Layer | Tool |
|---|---|
| Generator | Python 3 — `scripts/build_site.py` |
| Hosting | GitHub Pages · custom domain `dakhni.org` |
| Content | JSON files in `content/` — single source of truth |
| Validation | JSON Schema in `schemas/page.schema.json` |
| Styles / JS | `assets/site.css` · `assets/site.js` — vanilla, no build step |
| CI | GitHub Actions — search index rebuild + image localization |

## Commands

```bash
# Build — validate all JSON, generate HTML for every page
python3 scripts/build_site.py

# Rebuild search index (run after build when content changes)
python3 scripts/build-search-index.py

# Quick schema check on a single file
python3 -c "
import jsonschema, json
s = json.load(open('schemas/page.schema.json'))
d = json.load(open('content/cities/hyderabad.json'))
jsonschema.validate(d, s)
print('OK')
"
```

The build prints `Rendered N pages` on success. Any JSON or schema error exits non-zero with a message.

## Folder layout

```
content/                JSON source — one file per page
  cities/               10 city leaf pages
  dynasties/            5 dynasty leaf pages
  sufism/               7 Sufi saint leaf pages
  heritage/             7 heritage topic leaf pages
  language/             4 language leaf pages
  sacred-sites/         4 sacred-site leaf pages
  landmarks/            monuments.json + institutions.json
  *.json                Hub/index pages + home, about, navigation

scripts/                Python build tools (do not edit unless task says to)
schemas/                JSON Schema validation files
assets/                 Global CSS, JS, shared images
{section}/              Generated HTML output (committed, served by GH Pages)

.claude/
  commands/             Slash commands — one .md per routine
  settings.json         Hooks + pre-approved permissions
PLAN.md                 Checklist of pending tasks — the loop's memory
loop.sh                 Shell script to run next-task in a loop
```

## Content conventions

### Page types and expected blocks

| `page_type` | Expected blocks | Status |
|---|---|---|
| `city_leaf` | `facts` + `html` + `timeline` | All 10 done |
| `language_leaf` | `facts` + `html` + `timeline` | All 4 done |
| `saint_leaf` | `facts` + `html` + `timeline` | Timeline missing on 7 |
| `dynasty_leaf` | `facts` + `html` + `timeline` | Timeline missing on 5 |
| `heritage_leaf` | `facts` + `html` + `timeline` | All 7 use raw `body_html` |
| `sacred_site_leaf` | `facts` + `html` + `timeline` | All 4 use raw `body_html` |
| `section_hub` | `cards` (optional) | Mix |

### Block schemas

```jsonc
// Key-value facts panel
{ "type": "facts", "items": [{ "key": "Founded", "value": "1591 CE" }] }

// Raw HTML block (preserve existing prose)
{ "type": "html", "html": "<div class=\"h-wrap\">...</div>" }

// Dated chronology
{
  "type": "timeline",
  "eyebrow": "A Dynastic Chronology",
  "title": "The Bahmani Sultanate in dates",
  "items": [{ "year": "1347", "text": "Alauddin Bahman Shah declares independence from Delhi." }]
}

// Section with heading + prose
{ "type": "section", "heading": "The Chishti Lineage", "body": "..." }

// Card grid (hub pages)
{ "type": "cards", "items": [{ "title": "Hyderabad", "url": "/cities/hyderabad/", "description": "..." }] }
```

### Required JSON fields (every page)

`title`, `description`, `url`, `section`, `eyebrow`, `title_html`, `subtitle`, `dedication`

Plus either `blocks` (preferred) or `body_html` (legacy, being migrated).

### File naming

- Filename = last URL segment: `content/cities/hyderabad.json` → `/cities/hyderabad/`
- Lowercase, hyphenated. Adding a new page: create the JSON, register it in the hub's `blocks.cards`, re-run build.

## Definition of done (per PLAN.md task)

A task is complete when ALL of the following are true:

1. The target JSON file has the correct block structure
2. `python3 scripts/build_site.py` exits with `Rendered N pages` (zero errors)
3. The generated HTML under the page's output directory exists and contains the new content
4. Changes are committed on the working branch with message format `content: <brief description>`
5. The commit has been pushed to `origin`
6. The checkbox in `PLAN.md` is checked (`- [x]`)

## Git workflow

- **Working branch:** `claude/agent-automation-checklists-lGrNX`
- **Never push to `main` directly**
- One commit per PLAN.md task — commit message: `content: <what was added>`
- Push immediately after each commit (so the remote is always up to date)

## Guardrails for unattended runs

- Only edit files in `content/` and update checkboxes in `PLAN.md`
- Do not touch `scripts/`, `assets/`, `.github/`, or `schemas/` unless the task explicitly says so
- Do not create new pages unless a Phase 6 task says to — enrich existing pages first
- If `build_site.py` fails, fix the JSON before committing (never commit a broken state)
- Complete **one task per run** — check the box, commit, push, then stop
- When writing new historical content (timeline entries, facts), use only information consistent with what already appears in the file; do not invent dates or names not supported by the existing content
