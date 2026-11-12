#!/usr/bin/env python3
"""Recolour the portfolio signature for both GitHub themes.

    python scripts/signature.py

Reads the signature from the portfolio repo (white ink on transparency) and writes
assets/signature-dark.png and assets/signature-light.png.

The source is white, which is invisible against GitHub's light theme -- the usual way
this goes wrong is shipping the one file and only ever checking it in dark mode. Only
the alpha channel carries the handwriting, so each output is that same mask filled with
an ink colour that reads against its own background.
"""

import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('need: pip install pillow')

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
SOURCE = ROOT.parent / 'keshav-portfolio' / 'public' / 'signature.png'

# Ink per theme. Not pure black on light: the signature sits beside a dot-matrix
# portrait, and full black next to that reads as a different weight of mark.
INKS = {
    'dark': (233, 237, 243),    # near-white, GitHub dark foreground
    'light': (36, 41, 47),      # GitHub light foreground
}

TRIM_PAD = 6


def main():
    if not SOURCE.exists():
        sys.exit(f'signature not found: {SOURCE}')

    src = Image.open(SOURCE).convert('RGBA')
    alpha = src.split()[-1]

    # Trim the transparent margin so the README can size it by width without a slab
    # of empty space throwing the alignment off against the portrait.
    box = alpha.getbbox()
    if box:
        left, top, right, bottom = box
        left = max(0, left - TRIM_PAD)
        top = max(0, top - TRIM_PAD)
        right = min(src.width, right + TRIM_PAD)
        bottom = min(src.height, bottom + TRIM_PAD)
        alpha = alpha.crop((left, top, right, bottom))

    ASSETS.mkdir(exist_ok=True)
    for theme, ink in INKS.items():
        out_img = Image.new('RGBA', alpha.size, ink + (0,))
        out_img.putalpha(alpha)
        out = ASSETS / f'signature-{theme}.png'
        out_img.save(out, 'PNG', optimize=True)
        print(f'wrote {out.relative_to(ROOT)}  {alpha.size[0]}x{alpha.size[1]}  ({out.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
