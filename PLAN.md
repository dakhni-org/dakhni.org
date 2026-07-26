# PLAN.md — dakhni.org content roadmap

The automated agent picks the **first unchecked item**, completes it, and marks it done.
One task per run. See `CLAUDE.md` for definition of done and guardrails.

---

## Phase 1 — Add `timeline` blocks to Sufi saint pages

Each saint page has `facts` + `html` blocks but no `timeline`.
**Add** a `{"type": "timeline", "eyebrow": "...", "title": "...", "items": [...]}` block with 6–10
dated entries covering birth/arrival in Deccan, key works, death, legacy, and urs tradition.
Write accurate dates and events consistent with what already appears in the file.

- [x] Add timeline block to `content/sufism/bandanawaz.json` — Khwaja Gesudaraz (1321–1422), Gulbarga
- [x] Add timeline block to `content/sufism/sharfuddin.json` — Hazrat Sharfuddin Yayha Maneri, Bidar
- [x] Add timeline block to `content/sufism/burhanuddin.json` — Hazrat Burhanuddin Gharib, Khuldabad
- [x] Add timeline block to `content/sufism/hussain-shah-wali.json` — Shah Hussain Wali, Nanded
- [x] Add timeline block to `content/sufism/shah-khamosh.json` — Shah Khamosh, Aurangabad
- [x] Add timeline block to `content/sufism/shah-raju.json` — Shah Raju Qattal, Gulbarga
- [x] Add timeline block to `content/sufism/yousufain.json` — Maula Ali & Yousuf, Hyderabad

---

## Phase 2 — Add `timeline` blocks to dynasty pages

Each dynasty page has `facts` + `html` blocks but no `timeline`.
**Add** a `timeline` block with 8–12 dated entries: dynasty founding, major rulers,
key battles, cultural milestones, and end of dynasty.

- [x] Add timeline block to `content/dynasties/bahmani.json` — Bahmani Sultanate 1347–1527
- [x] Add timeline block to `content/dynasties/qutb-shahi.json` — Qutb Shahi 1518–1687
- [x] Add timeline block to `content/dynasties/adil-shahi.json` — Adil Shahi 1489–1686
- [x] Add timeline block to `content/dynasties/bidar-barid.json` — Barid Shahi 1487–1619
- [x] Add timeline block to `content/dynasties/asaf-jahi.json` — Asaf Jahi / Nizams 1724–1948

---

## Phase 3 — Migrate heritage leaf pages from `body_html` to `blocks`

Each file in `content/heritage/*.json` stores content in the legacy `body_html` string.
**Migrate** by: (1) wrapping the existing `body_html` value inside a `{"type":"html","html":"<existing>"}` block,
(2) adding a `facts` block if one is missing, (3) adding a `timeline` block.
Set `body_html` to `""` after migration. Do NOT discard existing prose.

- [x] Migrate `content/heritage/cuisine.json` — Hyderabadi biryani, Dum Pukht, Haleem, Irani chai
- [x] Migrate `content/heritage/music.json` — Qawwali, Dhrupad, Hindustani music in the Deccan
- [x] Migrate `content/heritage/architecture.json` — Qutb Shahi arch, Deccani stucco, pointed arch
- [x] Migrate `content/heritage/crafts.json` — Bidriware, Himroo, Paithani, Kalamkari
- [x] Migrate `content/heritage/language-poetry.json` — Dakhni dialect, Wali Deccani, Divan-e-Wali
- [x] Migrate `content/heritage/festivals.json` — Eid Milad, Muharram processions, Bonalu, Bathukamma
- [x] Migrate `content/heritage/sufi-tradition.json` — Silsilas, urs gatherings, Chishti lineage in Deccan

---

## Phase 4 — Migrate landmarks pages from `body_html` to `blocks`

Same migration pattern as Phase 3.

- [x] Migrate `content/landmarks/monuments.json` — Charminar, Golconda, Bidar Fort, Gol Gumbaz
- [x] Migrate `content/landmarks/institutions.json` — Osmania University, Salar Jung, Chowmahalla

---

## Phase 5 — Migrate sacred-sites pages from `body_html` to `blocks`

Same migration pattern as Phase 3.

- [x] Migrate `content/sacred-sites/dargahs.json` — dargahs of the Deccan
- [x] Migrate `content/sacred-sites/masjids.json` — Mecca Masjid, Jama Masjid Bijapur, etc.
- [x] Migrate `content/sacred-sites/temples.json` — Birla Mandir, Yadagirigutta, Thousand Pillar Temple
- [x] Migrate `content/sacred-sites/religious-structures.json` — ashurkhanas, khanqahs, takias

---

## Phase 6 — Hub pages and new content

**Do not start Phase 6 until phases 1–5 are all checked.**

- [x] Add `cards` block to `content/sufism.json` hub — link all 7 saints with one-line descriptions
- [x] Add `cards` block to `content/dynasties.json` hub — link all 5 dynasties with one-line descriptions
- [x] Add `cards` block to `content/heritage.json` hub — link all 7 heritage topics
- [x] Add `cards` block to `content/landmarks.json` hub — link monuments and institutions sub-pages
- [x] Create `content/glossary.json` — a glossary page of Dakhni/Urdu/Persian terms used across the site; wire it into `content/navigation.json` under a new "Reference" section

---

## Phase 7 — Dedicated leaf pages for named crafts, dishes, festivals & music

The `cuisine`, `crafts`, `festivals`, and `music` heritage hub pages each mention several
specific named things in passing — a craft, a dish, a festival, a musical form — that have
no page of their own to link to from elsewhere on the site (unlike cities, dynasties, saints
and monuments, which all already are cross-link targets). This phase gives the highest-value
ones a dedicated leaf page.

**Do not start Phase 7 until phases 1–6 are all checked.**

**URL structure:** create these as flat siblings directly under `/heritage/` —
e.g. `content/heritage/bidriware.json` → `/heritage/bidriware/` — **not** nested under
`crafts/`, `cuisine/`, `festivals/` or `music/` (e.g. NOT `content/heritage/crafts/bidriware.json`).
`build_page_maps` in `scripts/build_site.py` (~line 544) classifies any URL that is another
page's parent as a hub, and hub pages are excluded from their own parent's Prev/Next sibling
group. Nesting a leaf under `crafts.json`'s URL would turn `/heritage/crafts/` into a hub and
silently drop it out of the `/heritage/` topic navigator — flat URLs avoid that specific bug.

**But flat URLs alone are not enough:** `build_page_maps` groups *every* non-hub child of a
parent into one shared Prev/Next sibling group by `parent_url`, with no notion of tier. Left
alone, these 6 sub-topic pages (default `sort_order` 999, same tier as pillars in the sort key)
would join the 7 pillars' `/heritage/` Prev/Next sequence directly — e.g. `festivals.json`
(`sort_order` 70, currently last) would gain "Bidriware" as its Next, mixing sub-topics into
the pillar tour. Before creating the first leaf page, add an explicit opt-out so sub-topic
pages join neither their own subnav nor their parent's group:
  1. In `schemas/page.schema.json`, add an optional `"no_subnav": {"type": "boolean"}` property.
  2. In `build_page_maps` (`scripts/build_site.py`), change the skip condition from
     `if url in hub_urls: continue` to `if url in hub_urls or page.get("no_subnav"): continue`.
  3. Set `"no_subnav": true` on each of the 6 new leaf pages below.
Verify afterward that none of the 7 pillar pages' rendered Prev/Next links point at a sub-topic.

**Discovery:** do not add a `cards` block anywhere for these — `render_blocks` emits
`content-cards`/`cards-grid`/`content-card` markup that `assets/site.css` does not style (this
exact mistake was already made and reverted once, commit `355598c`). The existing hand-styled
card-grid pattern (`<a class="card">…</a>` inside `<div class="card-grid">`, see
`content/heritage.json`'s own `html` block) is for the 7 top-level heritage pillars only —
don't extend it either; these are sub-topics, not new pillars. Instead, rely on the
cross-linking engine: each parent topic page's prose already names these things verbatim
("Bidriware — the signature craft of Bidar…" in `crafts.json`, etc.), so once the new leaf
page declares its own name in `link_terms`, `render_crosslinks` will automatically hyperlink
that existing mention — no manual wiring, and no `content/navigation.json` dropdown entry
needed either (that dropdown lists the 7 pillars, not their sub-topics).

For each item below: create the leaf page with `facts` + `html` blocks (timeline optional —
only if there are enough genuinely dated milestones), citing sources the way other leaf pages
do; declare the page's own name in its `link_terms`; set `"no_subnav": true`; then rebuild and
confirm (a) zero `link_terms` collisions, (b) the parent topic page's existing mention now
renders as an `xref-link` to the new page, (c) the new URL appears in `sitemap.xml`, and
(d) none of the 7 pillar pages' Prev/Next now points at a sub-topic page.

- [ ] Create `content/heritage/bidriware.json` — the silver-inlaid blackened-alloy metalwork of Bidar, c. 1500–present
- [ ] Create `content/heritage/paithani.json` — the tapestry-bordered silk sari woven at Paithan, near Aurangabad
- [ ] Create `content/heritage/biryani.json` — Hyderabadi dum biryani; the kachchi vs. pakki distinction
- [ ] Create `content/heritage/haleem.json` — the pounded wheat-lentil-meat dish and its Ramazan/Hyderabadi status
- [ ] Create `content/heritage/bonalu.json` — the Hindu festival of Bonalu in Hyderabad's old city
- [ ] Create `content/heritage/qawwali.json` — Sufi devotional ensemble singing at Deccan shrines

---

_Last updated by agent: check git log for latest commit._
