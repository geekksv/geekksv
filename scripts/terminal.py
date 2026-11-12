#!/usr/bin/env python3
"""Draw the terminal header for the profile README.

    python scripts/terminal.py

Writes assets/terminal-dark.svg and assets/terminal-light.svg.

Two files rather than one because the README pairs them with <picture>, the same way
the radar and language charts already work here. A single file could switch on
prefers-color-scheme inside the SVG, but GitHub serves README images through its own
camo proxy and the media query then follows whatever the proxy decides rather than the
reader's theme -- the pattern already used in this repo is the one that behaves.

The cursor blinks with a CSS animation. CSS inside an SVG does run when the SVG is
rendered through <img>, which is how GitHub embeds it; SMIL would also work but is
deprecated.

Text is left as text rather than converted to outlines. The font stack falls back
through the usual monospace faces, so it renders on any machine without fetching a
webfont -- GitHub will not load one from inside an SVG anyway.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'

# ---- content ---------------------------------------------------------------
TITLE = 'keshav@github'
USER = 'ksv@macbook'
PROMPT = ' : ~ $ '
COMMAND = 'id -un'          # the POSIX way to ask the same question as whoami
NAME = 'keshav kumar'
FOCUS = 'linux  /  devops  /  telephony  /  automation'
STATUS = 'online'

W, H = 880, 190

THEMES = {
    'dark': {
        'bg': '#0d1117', 'border': '#21262d', 'bar': '#161b22',
        'title': '#8b949e', 'user': '#3fb950', 'punct': '#6e7681',
        'cmd': '#c9d1d9', 'name': '#58a6ff', 'focus': '#8b949e',
        'cursor': '#58a6ff', 'status': '#8b949e', 'dot': '#3fb950',
    },
    'light': {
        'bg': '#ffffff', 'border': '#d0d7de', 'bar': '#f6f8fa',
        'title': '#57606a', 'user': '#1a7f37', 'punct': '#6e7781',
        'cmd': '#24292f', 'name': '#0969da', 'focus': '#57606a',
        'cursor': '#0969da', 'status': '#57606a', 'dot': '#1a7f37',
    },
}

MONO = ('ui-monospace,SFMono-Regular,&#x27;SF Mono&#x27;,Menlo,Consolas,'
        '&#x27;Liberation Mono&#x27;,monospace')


def svg(c):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME}, {FOCUS}">
  <title>{NAME} — {FOCUS}</title>
  <style>
    .mono {{ font-family: {MONO}; }}
    .cursor {{ animation: blink 1.1s steps(1, end) infinite; }}
    @keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .cursor {{ animation: none; }}
    }}
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

  <!-- card -->
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="12" fill="{c['bg']}" stroke="{c['border']}" stroke-width="1"/>

  <g clip-path="url(#card)">
    <!-- title bar -->
    <rect x="8" y="8" width="{W - 16}" height="40" fill="{c['bar']}"/>
    <!-- the lit top edge -->
    <rect x="8" y="8" width="{W - 16}" height="2" fill="url(#edge)"/>
  </g>
  <line x1="8" y1="48" x2="{W - 8}" y2="48" stroke="{c['border']}" stroke-width="1"/>

  <!-- window buttons -->
  <circle cx="34" cy="28" r="6" fill="#ff5f56"/>
  <circle cx="54" cy="28" r="6" fill="#ffbd2e"/>
  <circle cx="74" cy="28" r="6" fill="#27c93f"/>

  <text class="mono" x="{W / 2}" y="33" text-anchor="middle" font-size="13" fill="{c['title']}">{TITLE}</text>

  <!-- prompt -->
  <text class="mono" x="40" y="88" font-size="14.5">
    <tspan fill="{c['user']}" font-weight="600">{USER}</tspan><tspan fill="{c['punct']}">{PROMPT}</tspan><tspan fill="{c['cmd']}">{COMMAND}</tspan>
  </text>

  <!-- status -->
  <circle cx="{W - 108}" cy="83" r="4.5" fill="{c['dot']}"/>
  <text class="mono" x="{W - 40}" y="88" text-anchor="end" font-size="13" fill="{c['status']}">{STATUS}</text>

  <!-- the answer -->
  <text class="mono" x="40" y="132" font-size="31" font-weight="700" fill="{c['name']}" letter-spacing="0.5">{NAME}</text>

  <!-- what that means -->
  <text class="mono" x="40" y="162" font-size="13" fill="{c['focus']}">{FOCUS}<tspan class="cursor" fill="{c['cursor']}" font-weight="700" dx="14">&#x2588;</tspan></text>
</svg>
'''


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, colours in THEMES.items():
        out = ASSETS / f'terminal-{name}.svg'
        out.write_text(svg(colours), encoding='utf-8')
        print(f'wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
