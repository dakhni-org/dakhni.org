#!/usr/bin/env python3
"""Raster sharing and app icons derived from the canonical D monogram SVG.

Requires Pillow and Inkscape. Run when assets/dakhni-org-logo.svg changes.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, tempfile

root = Path(__file__).resolve().parents[1]
assets = root / 'assets'
logo = assets / 'dakhni-org-logo.svg'
svg = logo.read_text()
assert 'viewBox="0 0 1254 1254"' in svg
(assets / 'favicon.svg').write_text(svg.replace('  <g shape-rendering=', '  <rect width="1254" height="1254" fill="#FAF7EF"/>\n  <g shape-rendering=', 1))
with tempfile.TemporaryDirectory() as temporary:
    output = Path(temporary) / 'monogram.png'
    subprocess.run(['inkscape', str(logo), '--export-filename='+str(output), '--export-width=700'], check=True, capture_output=True)
    mark = Image.open(output).convert('RGBA')
    for size,name in [(32,'favicon-32.png'),(180,'apple-touch-icon.png'),(192,'icon-192.png'),(512,'icon-512.png')]:
        tile=Image.new('RGBA',(size,size),'#FAF7EF')
        inset=max(1,size//20)
        glyph=mark.resize((size-2*inset,size-2*inset),Image.Resampling.LANCZOS)
        tile.alpha_composite(glyph,(inset,inset))
        tile.convert('RGB').save(assets/name,optimize=True)

    canvas=Image.new('RGB',(1200,630),'#1A1814')
    draw=ImageDraw.Draw(canvas)
    gold='#AF8E59';cream='#FAF7EF'
    draw.rounded_rectangle((46,45,1154,585),radius=8,outline=gold,width=2)
    draw.rounded_rectangle((94,153,354,413),radius=14,fill=cream)
    glyph=mark.resize((250,250),Image.Resampling.LANCZOS)
    canvas.paste(glyph,(99,158),glyph)
    serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    draw.text((405,201),'DAKHNI.ORG',font=ImageFont.truetype(serif,57),fill=cream)
    draw.text((409,298),'The living heritage of the Deccan',font=ImageFont.truetype(sans,25),fill='#D9BD8E')
    draw.line((409,355,1088,355),fill=gold,width=2)
    draw.text((409,380),'LANGUAGE  ·  HISTORY  ·  CULTURE',font=ImageFont.truetype(sans,18),fill=cream)
    canvas.save(assets/'social-preview.png',optimize=True)
