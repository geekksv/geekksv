#!/usr/bin/env python3
"""Draw the terminal header for the profile README.

    python scripts/terminal.py

Writes assets/terminal-dark.svg and assets/terminal-light.svg.

Two files rather than one because the README pairs them with <picture>, the same way
the radar and language charts already work here. A single file could switch on
prefers-color-scheme inside the SVG, but the pattern already used in this repo is the
one known to behave through GitHub's image proxy.

The portrait and the signature are embedded as base64 data URIs, not referenced. An SVG
that GitHub renders through <img> is isolated: it cannot fetch an external image, so a
plain href would render as nothing at all. That is also why the portrait is rasterised
here rather than reusing assets/portrait.svg -- a nested SVG reference has the same
problem, and inlining 674KB of <circle> elements would be worse.

The cursor blinks with a CSS animation. CSS inside an SVG does run when the SVG is
rendered through <img>; SMIL would also work but is deprecated.
"""

import base64
import io
import pathlib
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit('need: pip install pillow')

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'

# ---- content ---------------------------------------------------------------
TITLE = 'keshav@github'
USER = 'ksv@macbook'
PROMPT = ' : ~ $ '
COMMAND = 'id -un'          # the POSIX way to ask the same question as whoami
FOCUS = 'linux  /  devops  /  telephony  /  automation'
STATUS = 'online'

W, H = 880, 262

# Portrait: rendered at 3x the size it is shown at, so it stays sharp on a high-DPI
# screen. 110 columns at 3px a cell keeps the dots legible; at the 150 columns the
# standalone portrait uses, a cell here would be about a pixel and the whole thing
# would mush into a blur.
PORTRAIT_COLS = 110
PORTRAIT_CELL = 3
PORTRAIT_DETAIL = 0.82
SUPERSAMPLE = 4

PORTRAIT_BOX = (40, 100, 110, 110)      # x, y, w, h  (displayed size)
SIG_H = 56

THEMES = {
    'dark': {
        'bg': '#0d1117', 'border': '#21262d', 'bar': '#161b22',
        'title': '#8b949e', 'user': '#3fb950', 'punct': '#6e7681',
        'cmd': '#c9d1d9', 'focus': '#8b949e',
        'cursor': '#58a6ff', 'status': '#8b949e', 'dot': '#3fb950',
    },
    'light': {
        'bg': '#ffffff', 'border': '#d0d7de', 'bar': '#f6f8fa',
        'title': '#57606a', 'user': '#1a7f37', 'punct': '#6e7781',
        'cmd': '#24292f', 'focus': '#57606a',
        'cursor': '#0969da', 'status': '#57606a', 'dot': '#1a7f37',
    },
}

MONO = ('ui-monospace,SFMono-Regular,&#x27;SF Mono&#x27;,Menlo,Consolas,'
        '&#x27;Liberation Mono&#x27;,monospace')


def dot_portrait(src_path):
    """Rasterise the dot-matrix portrait, matching scripts/dotify.py --color --flat.

    Flat sizing: every dot is the same radius and only its colour varies. Sizing by
    darkness is right for a photograph and wrong for flat art, which this source is --
    it would eat the light areas of the face.
    """
    img = Image.open(src_path).convert('RGBA')
    rows = max(1, round(PORTRAIT_COLS * img.height / img.width))
    small = img.resize((PORTRAIT_COLS, rows), Image.BOX)

    s = SUPERSAMPLE
    w, h = PORTRAIT_COLS * PORTRAIT_CELL, rows * PORTRAIT_CELL
    canvas = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    radius = (PORTRAIT_CELL / 2) * PORTRAIT_DETAIL * s

    px = small.load()
    for y in range(rows):
        for x in range(PORTRAIT_COLS):
            r, g, b, a = px[x, y]
            if a < 24:                      # transparent source stays transparent
                continue
            cx = (x + 0.5) * PORTRAIT_CELL * s
            cy = (y + 0.5) * PORTRAIT_CELL * s
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                         fill=(r, g, b, a))

    # Downsample for the antialiasing; drawing circles this small directly gives
    # hard, crawling edges.
    out = canvas.resize((w, h), Image.LANCZOS)

    # Every byte here is paid for twice: once as PNG, again inflated by a third as
    # base64 inside the SVG. The source is flat art, so a 256-colour palette costs
    # nothing visible and takes about a third off. FASTOCTREE is the one quantizer
    # that keeps the alpha channel -- the default would flatten the transparent
    # background to a solid block.
    quantized = out.quantize(colors=256, method=Image.FASTOCTREE).convert('RGBA')
    if quantized.split()[-1].getextrema()[0] != 0:
        return out          # alpha did not survive; keep the unquantized version
    return quantized


def data_uri(img, fmt='PNG', **save_kw):
    buf = io.BytesIO()
    img.save(buf, fmt, optimize=True, **save_kw)
    return f'data:image/{fmt.lower()};base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def svg(c, portrait_uri, sig_uri, sig_w):
    px, py, pw, ph = PORTRAIT_BOX
    sig_x = px + pw + 26
    sig_y = round(py + (ph - SIG_H) / 2)    # centred against the portrait
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="keshav kumar — {FOCUS}">
  <title>keshav kumar — {FOCUS}</title>
  <style>
    .mono {{ font-family: {MONO}; }}
    .cursor {{ animation: blink 1.1s steps(1, end) infinite; }}
    @keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .cursor {{ animation: none; }} }}
  </style>

  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="#2ea043" stop-opacity="0"/>
      <stop offset="0.18" stop-color="#2ea043" stop-opacity="1"/>
      <stop offset="0.82" stop-color="#3fb950" stop-opacity="1"/>
      <stop offset="1"    stop-color="#3fb950" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card">
      <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="12"/>
    </clipPath>
  </defs>

  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="12" fill="{c['bg']}" stroke="{c['border']}" stroke-width="1"/>

  <g clip-path="url(#card)">
    <rect x="8" y="8" width="{W - 16}" height="40" fill="{c['bar']}"/>
    <rect x="8" y="8" width="{W - 16}" height="2" fill="url(#edge)"/>
  </g>
  <line x1="8" y1="48" x2="{W - 8}" y2="48" stroke="{c['border']}" stroke-width="1"/>

  <circle cx="34" cy="28" r="6" fill="#ff5f56"/>
  <circle cx="54" cy="28" r="6" fill="#ffbd2e"/>
  <circle cx="74" cy="28" r="6" fill="#27c93f"/>

  <text class="mono" x="{W / 2}" y="33" text-anchor="middle" font-size="13" fill="{c['title']}">{TITLE}</text>

  <text class="mono" x="40" y="86" font-size="14.5">
    <tspan fill="{c['user']}" font-weight="600">{USER}</tspan><tspan fill="{c['punct']}">{PROMPT}</tspan><tspan fill="{c['cmd']}">{COMMAND}</tspan>
  </text>

  <circle cx="{W - 108}" cy="81" r="4.5" fill="{c['dot']}"/>
  <text class="mono" x="{W - 40}" y="86" text-anchor="end" font-size="13" fill="{c['status']}">{STATUS}</text>

  <!-- The answer to id -un: the face and the signature, where the typed name used to be. -->
  <image x="{px}" y="{py}" width="{pw}" height="{ph}" href="{portrait_uri}" preserveAspectRatio="xMidYMid meet"/>
  <image x="{sig_x}" y="{sig_y}" width="{sig_w}" height="{SIG_H}" href="{sig_uri}" preserveAspectRatio="xMidYMid meet"/>

  <text class="mono" x="40" y="236" font-size="13" fill="{c['focus']}">{FOCUS}<tspan class="cursor" fill="{c['cursor']}" font-weight="700" dx="14">&#x2588;</tspan></text>
</svg>
'''


def main():
    source = ASSETS / 'source.png'
    if not source.exists():
        sys.exit(f'portrait source not found: {source}')

    portrait = dot_portrait(source)
    portrait_uri = data_uri(portrait)
    print(f'portrait rasterised {portrait.size[0]}x{portrait.size[1]} '
          f'({len(portrait_uri) // 1024} KB as a data URI)')

    for name, colours in THEMES.items():
        sig_path = ASSETS / f'signature-{name}.png'
        if not sig_path.exists():
            sys.exit(f'missing {sig_path} — run scripts/signature.py first')
        sig = Image.open(sig_path).convert('RGBA')
        sig_w = round(SIG_H * sig.width / sig.height)
        # Resize to roughly 2x the display size; the source is larger than needed and
        # every spare pixel is paid for twice over once it is base64.
        sig = sig.resize((sig_w * 2, SIG_H * 2), Image.LANCZOS)

        out = ASSETS / f'terminal-{name}.svg'
        out.write_text(svg(colours, portrait_uri, data_uri(sig), sig_w), encoding='utf-8')
        print(f'wrote {out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
