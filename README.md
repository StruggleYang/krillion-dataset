# Krillion Daily Dive Dataset

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](LICENSE)
![Dives](https://img.shields.io/badge/dives-70%2B-blue)
![Accepted answers](https://img.shields.io/badge/accepted_answers-100k%2B-green)
![Updated](https://img.shields.io/badge/updated-daily-orange)

Every **Krillion** daily trivia dive — prompts and rarity-tiered answers — as clean,
structured open data. **Updated daily by an automated pipeline.**

**Krillion** is a free daily trivia game, the "daily trivia dive": 7 open prompts
a day, where the **rarest valid answer scores the most** — from Plankton (10 points)
up to One in a Krillion (100 points) ([how it works](https://krillionhq.com/how-to-play/)).
This repository redistributes the publicly released answer sheets as machine-readable
data: every dive since day one (#1 on 2026-07-16), every prompt, and a sample of
every accepted answer grouped by its official rarity tier.

> 🎮 **New to the game?** The companion guide — daily answers, scoring explainers
> and the full searchable archive — lives at **[krillionhq.com](https://krillionhq.com/)**:
> today's [answers](https://krillionhq.com/answers/), the
> [full dive archive](https://krillionhq.com/archive/), and
> [how to play](https://krillionhq.com/how-to-play/).

## Files

| File | Description |
|---|---|
| `data/krillion_dives.json` | Canonical dataset. One object per dive, newest first. |
| `data/krillion_answers.csv` | Flattened view: one row per sampled answer. |

## Data dictionary

**`krillion_dives.json`** — `Dive[]` (newest first):

```jsonc
{
  "n": 70,                    // official dive number (#1 = 2026-07-16)
  "date": "2026-09-23",       // US Eastern day the dive went live
  "prompts": [                // exactly 7 per dive
    {
      "q": "Name a way to prepare eggs",   // prompt text, qualifiers included
      "accepted": 259,                     // accepted answers on the official sheet
      "tiers": [                           // ordered rarest first
        {
          "name": "One in a Krillion",     // tier name (see scoring table below)
          "count": 2,                      // answers in this tier on the official sheet
          "picks": ["Haminados", "Khai luk khoei"]  // up to 10 sample picks
        }
      ]
    }
  ]
}
```

**`krillion_answers.csv`** — columns: `dive_number, date, prompt_number, prompt,
accepted_answers, tier, points, answer`.

**Scoring tiers:** Plankton 10 · Too Clever 15 · Schooler 30 · Rare 60 ·
Deep cut 85 · One in a Krillion 100. Every point sinks the dive 10 metres.

## Quickstart

```bash
# all "One in a Krillion" answers from the latest dive (jq)
jq '.[0].prompts[] | {q, gem: [.tiers[] | select(.name == "One in a Krillion") | .picks][]}' \
  data/krillion_dives.json

# average accepted answers per prompt, by month (python)
python3 - <<'PY'
import json, collections
dives = json.load(open("data/krillion_dives.json"))
by_month = collections.defaultdict(list)
for d in dives:
    for p in d["prompts"]:
        if p["accepted"]:
            by_month[d["date"][:7]].append(p["accepted"])
for m, v in sorted(by_month.items()):
    print(m, round(sum(v) / len(v), 1))
PY
```

## Daily updates

A scheduled GitHub Action runs `scripts/update.py` once a day, appends any new
dives, and commits the refreshed JSON + CSV — so this repository grows one dive
per day, automatically. Run it locally with:

```bash
python3 scripts/update.py          # incremental
python3 scripts/update.py --force  # full refetch
```

## Coverage & scope

- Dives **#1 (2026-07-16) → present**, one row set per day.
- Each tier keeps **up to 10 sample answers** plus the exact tier count; the
  complete per-dive answer sheets are published by the game itself.
- Acceptance and tier placement reflect the official sheet as published.
- English-language dataset (the game's prompts are English).

## Source & methodology

Answer sheets are published publicly after each daily dive ends. This dataset is
collected from a public mirror of those sheets, parsed with a validated extractor
(7 prompts per dive enforced, per-tier counts cross-checked against sheet totals),
and refreshed daily. HTML entities are unescaped; prompts keep their in-game
qualifiers (e.g. "accessories don't count").

## License & citation

Released under [CC BY 4.0](LICENSE). Krillion the game is made by its solo
developer (play at the official site) — this is an independent, non-affiliated
dataset built for players and researchers, maintained by
[KrillionHQ](https://krillionhq.com/).

**Cite as:**

> KrillionHQ (2026). *Krillion Daily Dive Dataset* — prompts and rarity-tiered
> answers for every Krillion daily dive. https://github.com/StruggleYang/krillion-dataset
