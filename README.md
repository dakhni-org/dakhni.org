# Dakhni.org — Heritage of the Deccan

> Preserving the soul of the Deccan, one story at a time.

[**dakhni.org**](https://dakhni.org) is a digital archive and cultural gateway dedicated to the **Dakhni civilisation** — six centuries (1347 – 1948) of language, poetry, food, music, architecture and royal lineage that flourished across the Deccan plateau of southern India.

From the **Bahmani Sultanate** of Gulbarga to the **Asaf Jahi Nizams** of Hyderabad, the site celebrates the kingdoms, the saints, the poets, the cities and the everyday heritage of the region that gave the world its first form of Urdu.

## Sections

The site is organised into seven sections, each with an overview page and detail pages beneath it:

| Section | What's inside |
| --- | --- |
| **Heritage** | Language & poetry, cuisine, music, architecture, crafts, the Sufi tradition and festivals |
| **Dynasties** | The royal houses of the Deccan — Bahmani, Qutb Shahi, Bidar Barid, Adil Shahi and the Asaf Jahi Nizams |
| **Language** | Dakhni and the tongues of the plateau — Dakhni, Urdu, Faarsi (Persian) and Telugu |
| **Sufism** | The saints of the Deccan — Burhanuddin Gharib, Bandanawaz Gisudaraz, Baba Sharfuddin and others |
| **Cities** | The ten cities of the Dakhni heartland |
| **Landmarks** | Monuments (forts, palaces, tombs) and Institutions (universities, colleges, hospitals, the Salar Jung Museum…) |
| **Sacred Sites** | Masjids, dargahs, temples and the houses of other faiths |

A homepage quiz, **"Are You Dakhni?"**, maps a visitor's roots back to the Deccan heartland.

## The Dakhni heartland

Hyderabad · Bidar · Gulbarga · Bijapur · Aurangabad · Golconda · Warangal · Nanded · Raichur · Nizamabad

## The dynasties

1. **Bahmani Sultanate** — 1347 – 1527 — Gulbarga, then Bidar
2. **Qutb Shahi Dynasty** — 1518 – 1687 — Golconda, then Hyderabad
3. **Barid Shahi (Bidar Sultanate)** — 1489 – 1619 — Bidar
4. **Adil Shahi Dynasty** — 1490 – 1686 — Bijapur
5. **Asaf Jahi Nizams** — 1724 – 1948 — Hyderabad

The full set lives under [`/dynasties/`](https://dakhni.org/dynasties/).

## Project structure

A static site generated from JSON content files in `content/` using `scripts/build_site.py`.
Generated pages are written as `index.html` files so URLs stay clean (`/cities/hyderabad/`).

```
.
├── index.html              # Landing page — heritage, pillars, quiz, poetry
├── heritage/               # 7 subpages + overview
├── dynasties/              # 5 dynasties + overview
├── language/               # Dakhni, Urdu, Faarsi, Telugu + overview
├── sufism/                 # 7 saints + overview
├── cities/                 # 10 cities + overview
├── landmarks/              # overview
│   ├── monuments/
│   └── institutions/       # + 15 institution detail pages
├── sacred-sites/           # overview
│   ├── masjids/
│   ├── dargahs/
│   ├── temples/
│   └── religious-structures/
├── assets/                 # Shared images (logo, pattern, flag) — see assets/README.md
│   └── README.md           # Asset conventions
├── scripts/                # Maintenance tooling
│   └── localize-images.py  # Download hot-linked Wikimedia images into local assets/
├── robots.txt
├── sitemap.xml             # Lists all 62 pages
├── CNAME                   # Custom domain (dakhni.org)
└── README.md
```

The shared navigation, head/meta shell, hero/footer, disclosure modal and search overlay
are generated from one template in `scripts/build_site.py`. Navigation data is maintained
in `content/navigation.json`.

### Assets

Global images live in [`/assets/`](assets/README.md); page-specific images live in a
colocated `assets/` folder inside each page directory. Conventions (naming, formats,
referencing) are documented in [`assets/README.md`](assets/README.md).

## Local development

Build and serve locally:

```bash
git clone https://github.com/dakhni-org/dakhni.org.git
cd dakhni.org
python3 scripts/build_site.py
python3 -m http.server 8000
# then open http://localhost:8000
```

`build_site.py` now performs validation before rendering. It verifies required
fields and basic shape checks for every `content/**/*.json` page file and validates
`content/navigation.json` structure. Any validation error fails the build with a
clear message so inconsistent content is caught early.

The site is hosted directly via **GitHub Pages** at [dakhni.org](https://dakhni.org).

## Contributing

Contributions of historical accuracy fixes, additional poetry, recipes, photographs and
translations are welcome. Open an issue or pull request — please cite sources for any
historical claim. When adding images, follow the conventions in
[`assets/README.md`](assets/README.md).

## Licence

Content © 2025 Dakhni.org. The site is published in memory of the Asaf Jahi dynasty and built with love for the Deccan.
