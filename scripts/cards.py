"""Draw the stat card and the project cards, live from the GitHub API.

Self-drawn rather than github-readme-stats / streak-stats / profile-trophy. Those are
single shared public instances serving millions of READMEs: when one is rate-limited or
down, this profile shows broken images, and the owner has no way to fix it and usually
no way to notice.

    python scripts/cards.py                 # unauthenticated, 60 req/hr
    GITHUB_TOKEN=... python scripts/cards.py
"""

import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER = os.environ.get("PROFILE_USER", "geekksv")

THEMES = {
    "dark":  {"ink": "#e8ecf2", "muted": "#7d8798", "line": "#1c212b", "panel": "#0d0f14", "accent": "#e57255"},
    "light": {"ink": "#14171d", "muted": "#666f7d", "line": "#e4e6ec", "panel": "#ffffff", "accent": "#c15f3c"},
}

LANG_COLOUR = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Go": "#00ADD8", "Shell": "#89e051", "C++": "#f34b7d", "HTML": "#e34c26",
    "CSS": "#563d7c", "Dockerfile": "#384d54",
}


def esc(t):
    """XML-escape. Repo descriptions are user text and will contain & sooner or later."""
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-cards"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def repo_card(t, repo):
    w, h = 420, 150
    desc = repo.get("description") or "No description"
    lines = wrap(desc, 46)[:2]
    lang = repo.get("language")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="JetBrains Mono, ui-monospace, monospace">',
           f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>',
           f'<text x="22" y="38" fill="{t["accent"]}" font-size="16" font-weight="600">{esc(repo["name"])}</text>']
    for i, line in enumerate(lines):
        out.append(f'<text x="22" y="{66 + i*20}" fill="{t["muted"]}" font-size="12">{esc(line)}</text>')
    y = h - 26
    if lang:
        out.append(f'<circle cx="28" cy="{y-4}" r="5" fill="{LANG_COLOUR.get(lang, t["muted"])}"/>')
        out.append(f'<text x="42" y="{y}" fill="{t["ink"]}" font-size="12">{esc(lang)}</text>')
    out.append(f'<text x="{w-22}" y="{y}" fill="{t["muted"]}" font-size="12" text-anchor="end">'
               f'&#9733; {repo["stargazers_count"]}  &#9282; {repo["forks_count"]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    entries = json.loads((assets / "projects.json").read_text(encoding="utf-8"))["repos"]
    # Entries are either a bare name or {name, lang} where lang overrides what GitHub
    # reports. GitHub names the language with the most bytes, which on Qode is the
    # JavaScript wrapper around a QR encoder written from scratch in Go — so the card
    # said "JavaScript" directly beside a description saying Go. The override exists for
    # exactly that case and should not be used to claim anything the repo does not contain.
    wanted = [e if isinstance(e, str) else e["name"] for e in entries]
    overrides = {e["name"]: e["lang"] for e in entries if isinstance(e, dict) and e.get("lang")}

    try:
        user = api(f"users/{USER}")
        repos = api(f"users/{USER}/repos?per_page=100")
    except urllib.error.HTTPError as e:
        # Fail loudly. A card silently left at yesterday's numbers is worse than a
        # workflow that goes red, because nobody goes looking for it.
        raise SystemExit(f"GitHub API {e.code}: {e.reason}. Set GITHUB_TOKEN if rate-limited.")

    by_name = {r["name"]: r for r in repos}

    for theme, t in THEMES.items():
        for name in wanted:
            repo = by_name.get(name)
            if not repo:
                print(f"  ! {name} not found on {USER}, skipped")
                continue
            shown = dict(repo)
            if name in overrides:
                shown["language"] = overrides[name]
            (assets / f"card-{name}-{theme}.svg").write_text(repo_card(t, shown), encoding="utf-8")

    print(f"drew {len(wanted)} project cards x {len(THEMES)} themes")


if __name__ == "__main__":
    main()
