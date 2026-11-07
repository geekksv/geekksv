"""Draw the skill radar and the language bars from assets/skills.json.

Two SVGs per chart, one per GitHub theme, because GitHub serves the README to both and
a single file tuned for one is unreadable on the other.

No third-party chart service. The usual ones are shared public instances; when they are
down the top of the profile is a row of broken images, and the owner is the last to know.

    python scripts/radar.py
"""

import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "assets" / "skills.json").read_text(encoding="utf-8"))

def esc(text):
    """XML-escape label text.

    Three axis names contain "&" — "Linux & systems" and friends. A bare ampersand is
    not well-formed XML, so the browser refuses the whole file and the chart renders as
    a broken image while every other asset on the page looks fine. Easy to misread as a
    path problem.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


THEMES = {
    "dark":  {"ink": "#e8ecf2", "muted": "#7d8798", "line": "#1c212b", "accent": "#e57255", "bg": "none"},
    "light": {"ink": "#14171d", "muted": "#666f7d", "line": "#e4e6ec", "accent": "#c15f3c", "bg": "none"},
}


def radar(theme, t):
    axes = DATA["radar"]
    n = len(axes)
    # Canvas is wider than tall and the web is small inside it: the labels sit outside
    # the outer ring, and the longest of them ("SIP & telephony") ran off a square
    # 420 box and was clipped. Sizing to the ring and not to the text is the usual way
    # to lose the ends of labels.
    size_w, size_h, cx, cy, r = 520, 420, 260, 205, 112

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" '
           f'viewBox="0 0 {size_w} {size_h}" font-family="JetBrains Mono, ui-monospace, monospace">']

    def point(i, frac):
        # Start at twelve o'clock and go clockwise, which is how people read a dial.
        a = -math.pi / 2 + (2 * math.pi * i / n)
        return cx + math.cos(a) * r * frac, cy + math.sin(a) * r * frac

    # Web rings
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, ring) for i in range(n)))
        out.append(f'<polygon points="{pts}" fill="none" stroke="{t["line"]}" stroke-width="1"/>')

    # Spokes
    for i in range(n):
        x, y = point(i, 1.0)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["line"]}" stroke-width="1"/>')

    # The shape itself
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, a["score"] / 10) for i, a in enumerate(axes)))
    out.append(f'<polygon points="{pts}" fill="{t["accent"]}" fill-opacity="0.18" '
               f'stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round"/>')
    for i, a in enumerate(axes):
        x, y = point(i, a["score"] / 10)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{t["accent"]}"/>')

    # Labels, nudged outward and aligned so they never sit on the web
    for i, a in enumerate(axes):
        x, y = point(i, 1.28)
        anchor = "middle" if abs(x - cx) < 20 else ("start" if x > cx else "end")
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{t["ink"]}" font-size="12" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{esc(a["axis"])}</text>')
        out.append(f'<text x="{x:.1f}" y="{y + 15:.1f}" fill="{t["muted"]}" font-size="10" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{a["score"]}/10</text>')

    out.append("</svg>")
    return "\n".join(out)


def languages(theme, t):
    langs = DATA["languages"]
    w, row = 460, 42
    h = row * len(langs) + 20

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" font-family="JetBrains Mono, ui-monospace, monospace">']

    for i, l in enumerate(langs):
        y = 20 + i * row
        bar_w = (w - 150) * l["score"] / 100
        out.append(f'<text x="0" y="{y}" fill="{t["ink"]}" font-size="13" dominant-baseline="middle">{esc(l["name"])}</text>')
        out.append(f'<rect x="110" y="{y - 7}" width="{w - 150}" height="14" rx="7" fill="{t["line"]}"/>')
        out.append(f'<rect x="110" y="{y - 7}" width="{bar_w:.1f}" height="14" rx="7" fill="{t["accent"]}"/>')
        out.append(f'<text x="110" y="{y + 20}" fill="{t["muted"]}" font-size="10" '
                   f'dominant-baseline="middle">{esc(l["note"])}</text>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme, t in THEMES.items():
        (assets / f"radar-{theme}.svg").write_text(radar(theme, t), encoding="utf-8")
        (assets / f"langs-{theme}.svg").write_text(languages(theme, t), encoding="utf-8")
    print(f"drew radar-*.svg and langs-*.svg for {', '.join(THEMES)}")


if __name__ == "__main__":
    main()
