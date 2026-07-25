#!/usr/bin/env python3
"""Apply the July 2026 site-wide historical fact-check corrections.

The public HTML is generated from content/**/*.json.  This script edits only the
canonical content layer (plus README.md); scripts/build_site.py then regenerates
all pages.  Replacements are deliberately conservative: demonstrably incorrect
claims are corrected, and disputed superlatives are qualified rather than
replaced with a different unsupported certainty.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Phrases that recur across multiple canonical content files.
GLOBAL_REPLACEMENTS: list[tuple[str, str]] = [
    ("The earliest form of Urdu", "An early literary form of Urdu/Hindustani"),
    ("the earliest form of Urdu", "an early literary form of Urdu/Hindustani"),
    ("two centuries older than the Urdu of Delhi", "established as a literary medium before Urdu flourished at Delhi"),
    ("literary two hundred years before the Urdu of Delhi", "literary before Urdu flourished at Delhi"),
    ("Father of Urdu Poetry", "Influential early Urdu poet"),
    ("the first sovereign-poet in a South Asian vernacular", "an early sovereign-poet in a South Asian vernacular"),
    ("first sovereign-poet in a South Asian vernacular", "early sovereign-poet in a South Asian vernacular"),
    ("the first reigning sovereign in South Asia to leave a literary divan in a vernacular tongue", "one of the earliest South Asian sovereigns to leave a substantial literary divan in a vernacular"),
    ("the first sustained sovereign-poet's diwan in any South Asian vernacular, anywhere on the subcontinent", "one of the earliest substantial royal divans in a South Asian vernacular"),
    ("the first sustained prose work in any north-Indian-derived vernacular, anywhere on the subcontinent", "a landmark early work of extended prose in Dakhni"),
    ("the language's first major work of extended prose fiction", "a landmark work of extended allegorical prose"),
    ("The first novel in a north-Indian tongue", "An early allegorical prose romance in Dakhni"),
    ("50,000-verse divan", "substantial Dakhni divan"),
    ("a personal divan of more than 50,000 verses in Dakhni", "a substantial surviving divan in Dakhni"),
    ("left a 50,000-verse divan in Dakhni", "left a substantial divan in Dakhni"),
    ("left a 50,000-verse divan in it", "left a substantial divan in it"),
    ("the most-visited dargah of modern Hyderabad", "a major dargah of modern Hyderabad"),
    ("the city's most-beloved Sufi shrine", "one of the city's best-known Sufi shrines"),
    ("their seventh-century repertoire", "their centuries-old repertoire"),
]

# Exact, source-file-specific corrections.  All old phrases are required so the
# script fails loudly if upstream content changes before this pass runs.
PATH_REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "content/home.json": [
        ("Mughal Capital · 1610–1707", "Founded 1610 · Mughal Deccan capital 1681–1707"),
        ("personally wrote a divan of poetry in Dakhni, Telugu and Persian — the first sovereign in South Asia to do so.", "wrote a substantial divan in Dakhni and became one of the Deccan's best-known sovereign-poets."),
        ("Their treasury produced the Koh-i-Noor and Hope diamonds.", "Golconda-region mines and markets supplied diamonds later associated with famous stones including the Koh-i-Noor and Hope; the earliest ownership histories of individual gems remain uncertain.<cite data-ref=\"smithsonian-hope\"></cite>"),
        ("whose whisper gallery still echoes a fifth time.", "whose whispering gallery carries sound repeatedly around the dome.<cite data-ref=\"incredible-india-gol-gumbaz\"></cite>"),
        ("V · The Last and Greatest", "V · The Last Deccan Dynasty"),
        ("1724 – 1948 &nbsp;·&nbsp; Seven generations, as prophesied by Hazrat Nizamuddin", "1724 – 1948 &nbsp;·&nbsp; Hyderabad State"),
        ("<span class=\"chrono-year\">1424</span><span class=\"chrono-text\">Capital shifts from Gulbarga to Bidar under Ahmad Shah I; the city becomes a Sufi and scholarly hub.</span>", "<span class=\"chrono-year\">c. 1425–1429</span><span class=\"chrono-text\">The Bahmani capital shifts from Gulbarga to Bidar under Ahmad Shah I; sources differ on the precise year.</span>"),
        ("The four Deccan sultanates unite at the Battle of Talikota and end the Vijayanagara Empire's hold on the south.", "The allied Deccan sultanates defeat Vijayanagara at Talikota and devastate its capital; the empire nevertheless continues from successor capitals into the seventeenth century."),
        ("<span class=\"chrono-year\">1656</span><span class=\"chrono-text\">Ibrahim Adil Shah II's reign closes Bijapur's poetic golden age; the <em>Kitab-i-Nauras</em> survives as Dakhni literature's masterwork.</span>", "<span class=\"chrono-year\">1627</span><span class=\"chrono-text\">Ibrahim Adil Shah II dies after a reign renowned for music and poetry; the <em>Kitab-i-Nauras</em> remains a major work of Dakhni literature.</span>"),
        ("The Asaf Jahi prophecy of seven generations holds.", "Asaf Jahi rule ends after seven ruling Nizams."),
        ("Brought south by Bahmani armies in the 14th century, the Khari Boli of Delhi mingled with local Dravidian and Marathi speech and was written in the Persian-Arabic script.", "Dakhni developed in the medieval Deccan through contact among Indo-Aryan vernaculars, Persian and Arabic literary culture, and Telugu, Marathi and Kannada speech; scholars differ over any single linear origin."),
        ("Bandanawaz Gisudaraz of Gulbarga (d. 1422) wrote devotional prose in early Dakhni.", "Bandanawaz Gisudaraz of Gulbarga (d. 1422) is traditionally credited with early Dakhni devotional prose, although the attribution of individual texts is debated."),
    ],
    "content/dynasties.json": [
        ("Six dynasties. Six hundred years.", "Five dynasties. Six hundred years."),
        ("the greatest patrons of Dakhni literature", "major patrons of Dakhni literature"),
        ("Nine sultans of Bijapur, the most cosmopolitan capital of the Deccan. Under the poet-king Ibrahim Adil Shah II it became a city of half a million, leaving behind the Gol Gumbaz and the Ibrahim Rauza.", "Nine sultans ruled Bijapur, a major cosmopolitan capital of the Deccan. Ibrahim Adil Shah II commissioned the Ibrahim Rauza; the later ruler Muhammad Adil Shah commissioned the Gol Gumbaz."),
        ("V · The Last and Greatest", "V · The Last Deccan Dynasty"),
        ("Under the seventh Nizam, named the richest man on earth by TIME magazine, Hyderabad ran its own railway, currency and university.", "Under the seventh Nizam, widely described in the 1930s as one of the world's wealthiest men, Hyderabad maintained its own railway, currency and university."),
    ],
    "content/dynasties/bahmani.json": [
        ("\"value\": \"Four tarafs\"", "\"value\": \"Initially four; eight after Gawan's reforms\""),
        ("<a href=\"#tarafs\">Four Tarafs</a>", "<a href=\"#tarafs\">Provincial Reforms</a>"),
        ("The four <em>tarafs</em>", "The provincial <em>tarafs</em>"),
        ("How the provinces meant to hold the realm together became the seeds of its five successor kingdoms", "How provincial administration evolved before governors and nobles established five successor sultanates"),
        ("To govern their vast territories, the Bahmanis divided the realm into four <em>tarafs</em> — great provinces administered by powerful regional nobles. These four were the seeds of every Deccan kingdom that followed.", "The Bahmani realm was initially divided into four <em>tarafs</em>. Mahmud Gawan later expanded the system to eight smaller provinces to limit the power of individual governors. Provincial elites and court factions subsequently helped form the five successor sultanates.<cite data-ref=\"eaton-2005\"></cite>"),
        ("the Deccan plateau becomes a sovereign political space for the first time since the Delhi Sultanate.", "the Bahmani state consolidates an independent sultanate across much of the northern Deccan."),
        ("Firuz Shah Bahmani invites the Chishti saint Bandanawaz Gisudaraz to Gulbarga; the dargah built after the saint's death in 1422 becomes the largest Sufi shrine of the southern Deccan.", "Bandanawaz Gisudaraz reaches Gulbarga around 1400 after leaving Delhi; the dargah built after his death in 1422 becomes one of the Deccan's major Sufi shrines."),
        ("Gawan reforms the provincial system, codifies the four tarafs,", "Gawan reforms the provincial system, expanding four tarafs into eight smaller provinces,"),
        ("The four taraf governors assert independence one by one:", "Provincial governors and powerful nobles establish successor states:"),
    ],
    "content/dynasties/qutb-shahi.json": [
        ("one of South Asia's most complete royal necropolises", "one of South Asia's best-preserved royal necropolises"),
        ("writes the first sovereign divan in a vernacular tongue", "becomes an early sovereign-poet of Dakhni"),
        ("He was the first reigning sovereign in South Asia to leave a literary divan in a vernacular tongue, writing poetry in Dakhni, Telugu and Persian alike.", "He left a substantial divan in Dakhni and became one of the Deccan's most important sovereign-poets."),
        ("The treasury through which the Koh-i-Noor, the Hope and the Regent passed into the world", "Mines and markets associated with some of the world's most famous diamonds"),
        ("The Koh-i-Noor, the Hope, the Regent and the Daria-i-Noor all passed through the Qutb Shahi treasury before scattering across the courts of Europe and Persia. For nearly two centuries the kingdom set the world price of the gemstone.", "Mines and trade networks in the wider Golconda region supplied celebrated diamonds to Asian and European markets. Stones later identified as the Hope and several other famous gems are associated with this region, but their earliest ownership histories are incomplete and cannot all be traced through the Qutb Shahi treasury.<cite data-ref=\"smithsonian-hope\"></cite>"),
        ("A year-long siege ended by treachery", "An eight-month siege ended by a breach from within"),
        ("After a year-long siege,", "After an eight-month siege,"),
        ("remain South Asia's most complete royal necropolis", "remain one of South Asia's best-preserved royal necropolises"),
        ("the first sovereign patronage of Dakhni", "early sovereign patronage of Dakhni"),
        ("the Koh-i-Noor, the Hope, the Regent, and the Daria-i-Noor all pass through the Qutb Shahi treasury.", "diamonds from the wider Golconda region enter global trade; the earliest ownership histories of individual famous stones remain uncertain.<cite data-ref=\"smithsonian-hope\"></cite>"),
        ("composing poetry in Dakhni, Telugu, and Persian alike.", "leaving a substantial literary divan in Dakhni."),
    ],
    "content/dynasties/asaf-jahi.json": [
        ("the largest and wealthiest princely state in India", "India's largest princely state by area and one of its wealthiest"),
        ("the largest and richest of the princely states", "the largest princely state by area and one of the wealthiest"),
        ("After the catastrophic Musi flood of 1908 he remade Hyderabad as a modern capital — founding Osmania University, the first in India to teach in Urdu, together with Osmania General Hospital, the State Central Library, the High Court, and the great dams of Osman Sagar and Himayat Sagar.", "The catastrophic Musi flood of 1908 occurred under the sixth Nizam, Mir Mahbub Ali Khan. Reconstruction and flood-control planning began before Mir Osman Ali Khan acceded in 1911; his government then implemented and expanded the programme, including Osmania University — the first Indian university to adopt an Indian language, Urdu, as its medium of instruction — major civic buildings, and the Osman Sagar and Himayat Sagar reservoirs.<cite data-ref=\"osmania-official\"></cite>"),
        ("the incomparable Salar Jung collection assembled by their prime ministers", "the Salar Jung collection, assembled principally by Mir Yousuf Ali Khan (Salar Jung III), a former prime minister, and his family"),
        ("the seventh Nizam Mir Osman Ali Khan, who accedes in 1911, uses the reconstruction as the occasion to remake the city as a modern capital.", "relief begins under the sixth Nizam, Mir Mahbub Ali Khan; after acceding in 1911, Mir Osman Ali Khan's government implements and expands the reconstruction and flood-control programme."),
        ("founds Osmania University — the first in India to teach in Urdu — together with Osmania General Hospital, the State Central Library, and the High Court.", "establishes Osmania University — the first Indian university to adopt an Indian language, Urdu, as its medium of instruction — and develops major institutions including Osmania General Hospital, the State Central Library and the High Court.<cite data-ref=\"osmania-official\"></cite>"),
    ],
    "content/cities/aurangabad.json": [
        ("A City of the Deccan · Mughal Imperial Capital · 1610–1707", "A City of the Deccan · Founded 1610 · Mughal Deccan capital 1681–1707"),
        ("an Ethiopian boy sold into slavery and risen to a throne", "an Ethiopian-born enslaved youth who rose to become regent and de facto ruler of the Nizam Shahi state"),
        ("in the same compound, the founder of Aurangabad and the emperor who renamed it lie within a stone's throw of each other.", "the founder of Aurangabad and the emperor who renamed it are both buried in the wider sacred landscape of Khuldabad, but not in the same compound."),
        ("The grain markets of the city fed an army of half a million;", "The grain markets of the city supplied a vast Mughal field army;"),
    ],
    "content/sacred-sites/religious-structures.json": [
        ("Medak Cathedral · 1924 · largest in India", "Medak Cathedral · 1924 · major Telangana landmark"),
        ("Asia's largest non-Catholic cathedral", "Major Church of South India cathedral"),
        ("the largest cathedral in India after the Mar Thoma cathedral at Calcutta", "one of Telangana's largest churches, with seating for about 5,000 people"),
        ("Parsi Anjuman &amp; Atash Behram, Secunderabad", "Parsi Zoroastrian Anjuman &amp; Fire Temple, Secunderabad"),
        ("Zoroastrian · Continuous since the 1820s", "Zoroastrian · Trust documented since 1887"),
        ("The Parsi Anjuman maintains an Atash Behram (fire-temple), a dharamshala and a dakhma at Secunderabad — the principal Zoroastrian sites of the Deccan plateau.", "The Parsi Zoroastrian Anjuman of Secunderabad and Hyderabad, documented by a trust deed from 1887, maintains a fire temple and community facilities in Secunderabad. The available official source does not classify the temple as an Atash Behram.<cite data-ref=\"pzash-official\"></cite>"),
        ("Shvetambar · 2,000-year-old Adishwara Tirth", "Shvetambar · Historic Adishwara Tirth"),
        ("holds a 5-foot jade idol of Rishabhanatha said to have been worshipped by the Pandavas.", "holds a 5-foot jade idol of Rishabhanatha traditionally said to have been worshipped by the Pandavas."),
        ("a kind of inter-faith necropolis, the most condensed sacred landscape in the Mughal Deccan", "a concentrated Islamic sacred and funerary landscape of the Mughal Deccan"),
        ("the only Sikh Takht outside Punjab and Bihar", "one of two Sikh Takhts outside Punjab (the other is Patna Sahib in Bihar)"),
        ("the Parsi Anjuman establishes an Atash Behram (fire-temple), dharamshala, and dakhma", "the Parsi community establishes an Anjuman, fire temple and community facilities; the trust is documented from 1887"),
        ("completed in 1924, its 175-foot Gothic spire makes it the largest cathedral in India after Calcutta", "completed in 1924, its 175-foot Gothic spire makes it a major landmark of the Church of South India"),
        ("the Bahá'í Centre at Banjara Hills opens (1968), serving a Hyderabad community continuous since the early twentieth century.", "a Bahá'í community develops in Hyderabad; the site does not assign a precise opening year without a verifiable institutional source."),
    ],
    "content/sufism.json": [
        ("The saints arrived <em style=\"color:var(--gold-deep);font-style:italic;\">with</em> the sultans", "Saints, courts and <em style=\"color:var(--gold-deep);font-style:italic;\">migration</em>"),
        ("Islam first reached the Deccan in 711 with the Arab traders of the Konkan coast, but the established institutional Islam — with its mosques, madrasas, qadis and Sufi <em>khanqahs</em> — came south only with the Khalji and Tughluq invasions in the fourteenth century.", "Muslim maritime communities were present on India's western coast from the early medieval period, while the Khalji and Tughluq expansions of the fourteenth century brought a new wave of courts, soldiers, scholars, jurists and Sufi institutions into the interior Deccan."),
        ("the most consequential single Sufi migration in South Asian history", "an important migration in the history of Deccan Sufism"),
        ("The Sufis who came south were not popular preachers or itinerant healers; they were trained scholars,", "Many Sufis who came south were trained scholars,"),
        ("but no settled Sunni Sufi establishment. Within three generations there was one", "and limited evidence of an established Sunni Sufi network in the interior. Within three generations a substantial network had emerged"),
    ],
    "content/language/dakhni.json": [
        ("\"key\": \"First text\",\n          \"value\": \"c. 1410 · Bandanawaz\"", "\"key\": \"Early texts\",\n          \"value\": \"15th c. · some traditionally attributed to Bandanawaz\""),
        ("\"key\": \"Speakers\",\n          \"value\": \"~12 million\",\n          \"ref\": \"rahman-2011\"", "\"key\": \"Speakers\",\n          \"value\": \"No separate official census count\""),
        ("Linguistically, it is not a separate language but a distinct dialect:", "It is variously classified as a southern variety or register of Hindustani/Urdu rather than through a universally agreed language–dialect boundary:"),
        ("The first writer of literary Dakhni was not a king but a Sufi.", "Bandanawaz is traditionally identified as an early figure in literary Dakhni, although the attribution of particular vernacular works remains debated."),
        ("<em>Mi'raj-ul-Ashiqin</em> — a tract on the path of the seeker — and his <em>Hidayat-nama</em> are the earliest surviving prose texts in any north-Indian-derived vernacular, beating Hindavi prose of the north by nearly a century. They are also the documentary beginning of Dakhni's life as a written language.", "<em>Mi'raj-ul-Ashiqin</em> and <em>Hidayat-nama</em> are traditionally associated with early Dakhni prose, but modern scholarship debates the authorship and dating of some works attributed to Bandanawaz. They remain important to discussions of Dakhni's emergence as a written literary medium."),
        ("the first sustained sovereign-poet's diwan in any South Asian vernacular, anywhere on the subcontinent", "one of the earliest substantial royal divans in a South Asian vernacular"),
        ("The first <em>novel</em> in a north-Indian tongue", "An early Dakhni <em>allegorical prose romance</em>"),
        ("They are the only sixteenth-century compositions in any South Asian vernacular that survive intact, words and ragas together.", "The work is an important surviving witness to the interaction of Dakhni poetry and court music."),
    ],
}

REFERENCE_ADDITIONS: dict[str, list[dict[str, str]]] = {
    "content/home.json": [
        {"id": "smithsonian-hope", "text": "Smithsonian National Museum of Natural History, 'History of the Hope Diamond'.", "url": "https://naturalhistory.si.edu/explore/collections/hope-diamond-history"},
        {"id": "incredible-india-gol-gumbaz", "text": "Ministry of Tourism, Government of India, 'Gol Gumbaz — The Whispering Dome'.", "url": "https://www.incredibleindia.gov.in/en/karnataka/vijayapura/gol-gumbaz"},
    ],
    "content/dynasties/qutb-shahi.json": [
        {"id": "smithsonian-hope", "text": "Smithsonian National Museum of Natural History, 'History of the Hope Diamond'.", "url": "https://naturalhistory.si.edu/explore/collections/hope-diamond-history"},
    ],
    "content/dynasties/asaf-jahi.json": [
        {"id": "osmania-official", "text": "Osmania University, 'Origin and History' and official milestones.", "url": "https://www.osmania.ac.in/aboutus-originandhistory.php"},
    ],
    "content/sacred-sites/religious-structures.json": [
        {"id": "pzash-official", "text": "Parsi Zoroastrian Anjuman of Secunderabad and Hyderabad, 'The Organisation'.", "url": "https://www.pzash.org/the-organisation"},
    ],
}


def replace_strings(value: Any, replacements: list[tuple[str, str]], counts: dict[str, int]) -> Any:
    if isinstance(value, str):
        for old, new in replacements:
            n = value.count(old)
            if n:
                value = value.replace(old, new)
                counts[old] = counts.get(old, 0) + n
        return value
    if isinstance(value, list):
        return [replace_strings(item, replacements, counts) for item in value]
    if isinstance(value, dict):
        return {key: replace_strings(item, replacements, counts) for key, item in value.items()}
    return value


def remove_unverified_synagogue_card(data: Any) -> Any:
    """Remove the unsupported Banjara Hills Magen David entry from decoded HTML."""
    if isinstance(data, str) and "Magen David Synagogue (historic)" in data:
        marker = '<h3 class="card-title">Magen David Synagogue (historic) &amp; the Bene Israel of Hyderabad</h3>'
        pos = data.index(marker)
        start = data.rfind('    <article class="card">', 0, pos)
        end = data.index('    </article>', pos) + len('    </article>')
        return data[:start] + data[end:]
    if isinstance(data, list):
        return [remove_unverified_synagogue_card(item) for item in data]
    if isinstance(data, dict):
        return {key: remove_unverified_synagogue_card(item) for key, item in data.items()}
    return data


def add_references(doc: dict[str, Any], additions: list[dict[str, str]]) -> None:
    refs = doc.setdefault("references", [])
    existing = {ref.get("id") for ref in refs if isinstance(ref, dict)}
    for ref in additions:
        if ref["id"] not in existing:
            refs.append(ref)
            existing.add(ref["id"])


def update_json(path: Path) -> tuple[int, list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    doc = json.loads(path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    doc = replace_strings(doc, GLOBAL_REPLACEMENTS, counts)
    required = PATH_REPLACEMENTS.get(rel, [])
    doc = replace_strings(doc, required, counts)

    missing = [old for old, _ in required if counts.get(old, 0) == 0]
    if missing:
        return 0, [f"{rel}: required phrase not found: {old!r}" for old in missing]

    if rel == "content/sacred-sites/religious-structures.json":
        doc = remove_unverified_synagogue_card(doc)

    add_references(doc, REFERENCE_ADDITIONS.get(rel, []))
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sum(counts.values()), []


def update_readme() -> int:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    replacements = [
        ("the region that gave the world its first form of Urdu", "the region that helped shape one of the earliest literary forms of Urdu/Hindustani"),
        ("sitemap.xml             # Lists all 62 pages", "sitemap.xml             # Lists all generated pages"),
    ]
    changed = 0
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"README.md: required phrase not found: {old!r}")
        changed += text.count(old)
        text = text.replace(old, new)
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
