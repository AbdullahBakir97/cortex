# graph-art

> Original concept and design: **Abdullah Bakir** ([@AbdullahBakir97](https://github.com/AbdullahBakir97)), 2026.
> Reading a contribution graph as a story, finding drawings hidden in real commit days,
> and keeping every drawing true to the graph.

Read your contribution graph two ways: as a story (which months were quiet,
steady or busy) and as a drawing (the shapes your real commit days happen to
make). Everything works on real days only.

## Quick start

```bash
export GH_TOKEN=...                       # any token that can read your profile
cortex graph-art fetch   -u <you>         # -> calendar.json
cortex graph-art analyze --calendar calendar.json
cortex graph-art detect  --calendar calendar.json      # -> figures.draft.json
# review the draft: keep what you see, rename it, recolour cells, add a note
cortex graph-art check   --calendar calendar.json -f figures.json
cortex graph-art render  --calendar calendar.json -f figures.json -o assets
```

`--heatmaps "assets/heatmap-*.svg"` works instead of `--calendar` if you already
keep SVGs whose cells carry `<title>N on YYYY-MM-DD</title>`.

## figures.json

```json
{
  "version": 1,
  "figures": [
    {
      "year": 2023,
      "name": "A sad ghost",
      "weeks": [44, 51],
      "when": "NOV – DEC",
      "cells": {"45,0": "#c9d1d9", "46,0": "#58a6ff"},
      "holes": ["46,0"],
      "note": "the two empty days at the top are its eyes",
      "legend": [["#c9d1d9", "ghost"], ["#58a6ff", "eyes"]]
    }
  ]
}
```

- `weeks` is the column range in that year's grid (0 = the week of Jan 1).
- `cells` keys are `"week,row"`, row 0 = Sunday.
- A coloured cell must be a day with contributions. An empty day may be used
  only when it is listed in `holes`. `check` and `render` enforce this, so a
  figure can never draw in days that did not happen.

## How detection works

- **Faces** — small empty pockets (1–3 days) mostly surrounded by active days
  read as eyes. Two of them on about the same row, 2–5 weeks apart, inside a
  dense patch become a face candidate.
- **Templates** — small masks (`#` active, `.` empty, `?` any) slid across the
  grid; a match needs 86% of the defined cells to agree.

Detection only suggests. Seeing a dog or a lighthouse in a graph is a human
reading, so the draft is meant to be reviewed and edited before rendering.

## name-art

```bash
cortex graph-art name-art --calendar calendar.json -n "Your Name" -f figures.json --handle github.com/you
```

Writes `assets/name-art.svg`: your name in pixel letters made of your real
commit days (oldest to newest, one colour per year), your confirmed drawings
placed in the free space around it, an octopus made of the rest of your
timeline, the longest streak and biggest day marked on the letters, and a worm
that sleeps, then eats every square in date order before it all grows back.
