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
- [ ] Add timeline block to `content/sufism/shah-khamosh.json` — Shah Khamosh, Aurangabad
- [ ] Add timeline block to `content/sufism/shah-raju.json` — Shah Raju Qattal, Gulbarga
- [ ] Add timeline block to `content/sufism/yousufain.json` — Maula Ali & Yousuf, Hyderabad

---

## Phase 2 — Add `timeline` blocks to dynasty pages

Each dynasty page has `facts` + `html` blocks but no `timeline`.
**Add** a `timeline` block with 8–12 dated entries: dynasty founding, major rulers,
key battles, cultural milestones, and end of dynasty.

- [ ] Add timeline block to `content/dynasties/bahmani.json` — Bahmani Sultanate 1347–1527
- [ ] Add timeline block to `content/dynasties/qutb-shahi.json` — Qutb Shahi 1518–1687
- [ ] Add timeline block to `content/dynasties/adil-shahi.json` — Adil Shahi 1489–1686
- [ ] Add timeline block to `content/dynasties/bidar-barid.json` — Barid Shahi 1487–1619
- [ ] Add timeline block to `content/dynasties/asaf-jahi.json` — Asaf Jahi / Nizams 1724–1948

---

## Phase 3 — Migrate heritage leaf pages from `body_html` to `blocks`

Each file in `content/heritage/*.json` stores content in the legacy `body_html` string.
**Migrate** by: (1) wrapping the existing `body_html` value inside a `{"type":"html","html":"<existing>"}` block,
(2) adding a `facts` block if one is missing, (3) adding a `timeline` block.
Set `body_html` to `""` after migration. Do NOT discard existing prose.

- [ ] Migrate `content/heritage/cuisine.json` — Hyderabadi biryani, Dum Pukht, Haleem, Irani chai
- [ ] Migrate `content/heritage/music.json` — Qawwali, Dhrupad, Hindustani music in the Deccan
- [ ] Migrate `content/heritage/architecture.json` — Qutb Shahi arch, Deccani stucco, pointed arch
- [ ] Migrate `content/heritage/crafts.json` — Bidriware, Himroo, Paithani, Kalamkari
- [ ] Migrate `content/heritage/language-poetry.json` — Dakhni dialect, Wali Deccani, Divan-e-Wali
- [ ] Migrate `content/heritage/festivals.json` — Eid Milad, Muharram processions, Bonalu, Bathukamma
- [ ] Migrate `content/heritage/sufi-tradition.json` — Silsilas, urs gatherings, Chishti lineage in Deccan

---

## Phase 4 — Migrate landmarks pages from `body_html` to `blocks`

Same migration pattern as Phase 3.

- [ ] Migrate `content/landmarks/monuments.json` — Charminar, Golconda, Bidar Fort, Gol Gumbaz
- [ ] Migrate `content/landmarks/institutions.json` — Osmania University, Salar Jung, Chowmahalla

---

## Phase 5 — Migrate sacred-sites pages from `body_html` to `blocks`

Same migration pattern as Phase 3.

- [ ] Migrate `content/sacred-sites/dargahs.json` — dargahs of the Deccan
- [ ] Migrate `content/sacred-sites/masjids.json` — Mecca Masjid, Jama Masjid Bijapur, etc.
- [ ] Migrate `content/sacred-sites/temples.json` — Birla Mandir, Yadagirigutta, Thousand Pillar Temple
- [ ] Migrate `content/sacred-sites/religious-structures.json` — ashurkhanas, khanqahs, takias

---

## Phase 6 — Hub pages and new content

**Do not start Phase 6 until phases 1–5 are all checked.**

- [ ] Add `cards` block to `content/sufism.json` hub — link all 7 saints with one-line descriptions
- [ ] Add `cards` block to `content/dynasties.json` hub — link all 5 dynasties with one-line descriptions
- [ ] Add `cards` block to `content/heritage.json` hub — link all 7 heritage topics
- [ ] Add `cards` block to `content/landmarks.json` hub — link monuments and institutions sub-pages
- [ ] Create `content/glossary.json` — a glossary page of Dakhni/Urdu/Persian terms used across the site; wire it into `content/navigation.json` under a new "Reference" section

---

_Last updated by agent: check git log for latest commit._
