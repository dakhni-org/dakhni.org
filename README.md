# Dakhni.org — Heritage of the Deccan

> Preserving the soul of the Deccan, one story at a time.

[**dakhni.org**](https://dakhni.org) is a digital archive and cultural gateway dedicated to the **Dakhni civilisation** — six centuries (1347 – 1948) of language, poetry, food, music and royal lineage that flourished across the Deccan plateau of southern India.

From the **Bahmani Sultanate** of Gulbarga to the **Asaf Jahi Nizams** of Hyderabad, the site celebrates the kingdoms, the saints, the poets and the everyday heritage of the region that gave the world its first form of Urdu.

## What you'll find

| Pillar | Theme |
| --- | --- |
| **Tarikh** | History and the six royal dynasties of the Deccan |
| **Zubaan** | Dakhni language and poetry — Wali Deccani, Ibrahim Adil Shah II and beyond |
| **Khana** | Hyderabadi cuisine: dum biryani, haleem, lukhmi, qubani ka meetha |
| **Mauseeqi** | Music, Bidri metalwork, Paithan silk, Dakhni miniature painting |
| **Khel** | Quizzes and trivia — coins, dishes, proverbs |
| **Pehchaan** | An AI companion that maps your roots to the Deccan heartland |

## The Dakhni heartland

Hyderabad · Bidar · Gulbarga · Bijapur · Aurangabad · Golconda · Warangal · Nanded · Raichur · Nizamabad

## The dynasties

1. **Bahmani Sultanate** — 1347 – 1527 — Gulbarga, then Bidar
2. **Qutb Shahi Dynasty** — 1518 – 1687 — Golconda, then Hyderabad
3. **Barid Shahi (Bidar Sultanate)** — 1489 – 1619 — Bidar
4. **Adil Shahi Dynasty** — 1490 – 1686 — Bijapur
5. **Asaf Jahi Nizams** — 1724 – 1948 — Hyderabad

A full visual timeline lives at [`/dynasties.html`](https://dakhni.org/dynasties.html).

## Project structure

```
.
├── index.html        # Landing page — heritage, pillars, quiz, poetry
├── dynasties.html    # Full timeline of the six Deccan dynasties
├── robots.txt        # Search-engine directives
├── sitemap.xml       # Sitemap for crawlers
├── CNAME             # Custom domain (dakhni.org)
└── README.md
```

The site is a static, dependency-free pair of HTML files designed to be hosted directly via **GitHub Pages** at [dakhni.org](https://dakhni.org).

## Local development

No build step. Clone the repository and open the HTML files in a browser, or run a tiny static server:

```bash
git clone https://github.com/dakhni-org/dakhni.org.git
cd dakhni.org
python3 -m http.server 8000
# then open http://localhost:8000
```

## Contributing

Contributions of historical accuracy fixes, additional poetry, recipes, photographs and translations are welcome. Open an issue or pull request — please cite sources for any historical claim.

## Licence

Content © 2025 Dakhni.org. The site is published in memory of the Asaf Jahi dynasty and built with love for the Deccan.
