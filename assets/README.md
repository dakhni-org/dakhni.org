# Assets

How images, logos and other static files are organised on dakhni.org.

## Two kinds of assets

**1. Shared / global — this folder (`/assets/`)**
Files used across many pages live here and are referenced by absolute path:

- `dakhni-org-logo.svg` — canonical D monogram. `favicon.svg`, PNG app icons,
  and `social-preview.png` are derived from it with `scripts/generate_brand_assets.py`.
- `dakhni-pattern.webp` — hero background pattern
- `Asafia_flag_of_Hyderabad_State.svg.png` — Asaf Jahi flag
- `image013.jpg`, `image015.jpg` — shared decorative images

**2. Page-local — each page's own `assets/` folder**
Every page directory has its own `assets/` folder for images unique to that
page. A page references its own assets by absolute path, e.g. from
`/sufism/bandanawaz/`:

```html
<img src="/sufism/bandanawaz/assets/bandanawaz-dargah.jpg" alt="…" />
```

Keep the empty `.gitkeep` until the folder has real files.

## Conventions

- **Reference by absolute path** (`/assets/…` or `/section/page/assets/…`), so
  links work the same from any page depth.
- **File names:** lowercase, hyphen-separated, descriptive —
  `golconda-fort-hero.jpg`, not `IMG_2931.JPG`.
- **Formats:** prefer WebP for photographs and compress before committing.
- **In markup:** set `width` and `height`; lazy-load images below the first
  visible section. Keep the first visible image eager so it can paint promptly.

## Localising external images

Some pages still hot-link images from `commons.wikimedia.org`. To download them
into the matching page `assets/` folders and rewrite the markup automatically,
run (from an environment with Wikimedia network access):

```bash
python3 scripts/localize-images.py
```

See `scripts/localize-images.py` for details.
