#!/usr/bin/env python3
"""Generate deterministic, page-specific 1200x630 social cards from content metadata."""
import glob
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'assets', 'social')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def lines(draw, title, max_width):
    for size in range(72, 41, -2):
        face = font(BOLD, size)
        words, result, current = title.split(), [], ''
        for word in words:
            candidate = (current + ' ' + word).strip()
            if draw.textbbox((0, 0), candidate, font=face)[2] > max_width and current:
                result.append(current)
                current = word
            else:
                current = candidate
        if current:
            result.append(current)
        if len(result) <= 3 and all(draw.textbbox((0, 0), line, font=face)[2] <= max_width for line in result):
            return result, face, size
    return result, face, size


def render(page):
    path = 'home' if page['url'] == '/' else page['url'].strip('/').replace('/', '-')
    canvas = Image.new('RGB', (1200, 630), '#1a1814')
    cover = page.get('cover', '')
    source = os.path.join(ROOT, cover.lstrip('/')) if cover.startswith('/') else ''
    if not source or not os.path.isfile(source):
        source = os.path.join(ROOT, 'assets', 'dakhni-pattern.webp')
    try:
        with Image.open(source) as original:
            photo = ImageOps.fit(original.convert('RGB'), (585, 630), method=Image.Resampling.LANCZOS)
            canvas.paste(photo, (615, 0))
    except (OSError, ValueError):
        pass
    # Darken the photo toward the title and place a quiet gold seam.
    shade = Image.new('RGBA', (585, 630), (0, 0, 0, 0))
    shade.putalpha(Image.new('L', (585, 630)))
    overlay = ImageDraw.Draw(shade)
    for x in range(585):
        overlay.line((x, 0, x, 629), fill=(15, 13, 11, int(165 * (1 - x / 585) + 35)))
    canvas.paste(shade, (615, 0), shade)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 615, 630), fill='#1a1814')
    draw.rectangle((64, 72, 70, 115), fill='#bb9862')
    draw.text((90, 73), 'DAKHNI.ORG', font=font(SANS, 23), fill='#d9c8a9', spacing=2)
    section = page.get('section', 'Heritage of the Deccan').upper()
    draw.text((66, 176), section[:40], font=font(SANS, 20), fill='#bb9862')
    title = page['title']
    title_lines, face, size = lines(draw, title, 515)
    y = 222
    for line in title_lines:
        draw.text((62, y), line, font=face, fill='#f5efe4', stroke_width=0)
        y += size * 1.27
    draw.line((65, 535, 545, 535), fill='#826a48', width=2)
    draw.text((65, 554), 'Heritage of the Deccan', font=font(SANS, 20), fill='#d4c4a6')
    canvas.save(os.path.join(DEST, path + '.jpg'), 'JPEG', quality=86, optimize=True, progressive=True)


def main():
    os.makedirs(DEST, exist_ok=True)
    pages = []
    for filename in glob.glob(os.path.join(ROOT, 'content', '**', '*.json'), recursive=True):
        with open(filename, encoding='utf-8') as stream:
            page = json.load(stream)
        if isinstance(page, dict) and 'url' in page and 'title' in page:
            pages.append(page)
    for page in pages:
        render(page)
    print(f'Generated {len(pages)} social cards')


if __name__ == '__main__':
    main()
