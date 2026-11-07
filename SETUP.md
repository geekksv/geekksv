# Setup

This repo must be named **exactly `geekksv`** — the same as the GitHub username. That
repo's README is what GitHub shows on the profile. Any other name and it is just a repo.

It must also be **public**. The SVGs load by URL, so a private repo shows a column of
broken images to everyone except you.

---

## 1 · Push it

```bash
cd D:\portfolio\gh-profile
git init && git branch -M main
git add -A && git commit -m "profile readme"
git remote add origin https://github.com/geekksv/geekksv.git
git push -u origin main
```

## 2 · Let Actions write back

Repo → **Settings** → **Actions** → **General** → **Workflow permissions** →
**Read and write permissions** → Save.

The charts and metrics jobs commit their output. Without this they fail on the push step,
after doing all the work.

## 3 · Add the metrics token

`lowlighter/metrics` draws the contribution calendar and needs a token of its own — the
built-in `GITHUB_TOKEN` cannot read profile-level data. This is the usual reason that job
finishes green with an empty image.

1. <https://github.com/settings/tokens> → **Generate new token (classic)**
2. Scope: **`read:user`**
3. Copy it → repo → **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret** → name **`METRICS_TOKEN`**

## 4 · Run each workflow once

**Actions** tab → enable if prompted → **Run workflow** on each:

| workflow | draws | lands in |
|---|---|---|
| **Charts and cards** | radar, language bars, stat card, project cards | `assets/` on `main` |
| **Metrics** | 3D isometric contribution calendar | `assets/metrics.isocalendar.svg` |
| **Snake** | snake eating the contribution graph | the `output` branch |

After that they are on a schedule: charts daily, metrics every 6h, snake every 12h.

> The snake images are referenced from the `output` branch by raw URL, so they **404 until
> the Snake workflow has run once**. That is expected on a fresh profile. Do not go looking
> for a broken path.

## 5 · Fill in the profile fields

These are free, take a minute, and matter more than any of the artwork — all four are
currently empty:

- **Bio**: `Linux, DevOps & telephony engineer. I run the SIP layer and the Linux estate under a production platform.`
- **Website**: `https://geekksv.vercel.app/`
- **Location**: `Patna, India` · **Company**: `Prishal Technolabs`
- **Pinned repos**: Qode, artyom-robo, MeetOn, mirror-dashboard, Reely, faceproof

---

## Changing things later

### The skills

`assets/skills.json`. Edit the scores, push, and the Charts workflow redraws both charts.

The numbers are a judgement, not a measurement — change them when they stop being true.

They are **deliberately hand-written rather than computed from repo byte counts**. A
byte-count chart on this account puts JavaScript on top, because the public repos are side
projects and the work that pays — the SBC layer, the Linux estate — is not open source and
contributes nothing here. That chart would be accurate about GitHub and wrong about you,
and it would contradict both the CV and geekksv.vercel.app.

### The project cards

`assets/projects.json`. A bare name uses whatever GitHub reports; `{"name": …, "lang": …}`
overrides the language.

The override exists because GitHub names the language with the most **bytes**, which is not
always what a project is about — Qode's card said *JavaScript* next to a description saying
the encoder is written from scratch in Go, because the thin web wrapper outweighs it. Use it
only to correct that kind of thing, never to claim a language the repo does not contain.

### The portrait

```bash
python scripts/dotify.py assets/source.webp -o assets/portrait \
  --cols 120 --color --flat --detail 0.72
```

- `--cols` density. Higher is finer and heavier; **check it at the width the README uses
  (420px), not full size** — a grid that looks crisp at 1:1 turns to mush when scaled down.
- `--flat` even dots, colour carries the image. Right for flat illustration. Drop it for a
  photograph, where dot size should follow tone.
- `--detail` dot size relative to its cell.
- Transparency is preserved, so one file serves both GitHub themes.

To swap the picture, drop a new file in `assets/` and point the command at it. It samples
whatever it is given — nothing is generated, so the output is always the input.

### Preview before pushing

Open `preview.html` in a browser. It renders every local asset on both backgrounds, which
catches the two failures that are invisible in a diff: an SVG that is broken XML, and a
chart that is unreadable on one of the two themes.
