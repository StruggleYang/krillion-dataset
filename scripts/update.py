#!/usr/bin/env python3
"""Update the Krillion Daily Dive dataset.

Fetches any missing daily dives from the public reveal-sheet mirror,
appends them to data/krillion_dives.json, and regenerates the flattened
data/krillion_answers.csv. Designed to run unattended (GitHub Actions
cron) and locally.

Usage:
    python3 scripts/update.py            # incremental
    python3 scripts/update.py --force    # refetch everything
"""
import csv
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
JSON_PATH = DATA / "krillion_dives.json"
CSV_PATH = DATA / "krillion_answers.csv"
FIRST_DATE = date(2026, 7, 16)  # dive #1
UA = {"User-Agent": "Mozilla/5.0 (krillion-dataset updater)"}
POINTS = {"One in a Krillion": 100, "Deep cut": 85, "Rare": 60,
          "Schooler": 30, "Too Clever": 15, "Plankton": 10}
MAX_PICKS = 10  # sample size kept per tier; the official sheet is complete


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode()


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_page(html: str, iso: str) -> dict:
    blocks = re.split(r'<h2><span class="answer-num">', html)[1:]
    if not blocks:
        raise ValueError("no prompt blocks found")
    prompts = []
    for block in blocks:
        head, _, rest = block.partition("</h2>")
        q = re.sub(r"^\s*\d+\.\s*", "", strip_tags(head))
        cut = re.split(r"About this data|Challenge a friend", rest)[0]
        text = strip_tags(cut)
        am = re.search(r"(\d+)\s+valid answers", text)
        accepted = int(am.group(1)) if am else None
        tiers = []
        matches = list(re.finditer(
            r"(One in a Krillion|Deep cut|Rare|Schooler|Too Clever|Plankton)\s*\((\d+)\)", text))
        for i, m in enumerate(matches):
            name, count = m.group(1), int(m.group(2))
            seg = text[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            parts = re.split(r"\s+(100|85|60|30|15|10)\s+", seg.strip())
            picks = []
            for j in range(0, len(parts) - 1, 2):
                if parts[j].strip():
                    picks.append(parts[j].strip())
                if len(picks) >= MAX_PICKS:
                    break
            tiers.append({"name": name, "count": count, "picks": picks})
        prompts.append({"q": q, "accepted": accepted, "tiers": tiers})
    if len(prompts) != 7:
        print(f"  ! {iso}: {len(prompts)} prompts (expected 7)", file=sys.stderr)
    n = (date.fromisoformat(iso) - FIRST_DATE).days + 1
    return {"n": n, "date": iso, "prompts": prompts}


def write_csv(dives: list) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dive_number", "date", "prompt_number", "prompt",
                    "accepted_answers", "tier", "points", "answer"])
        for d in dives:
            for i, p in enumerate(d["prompts"], 1):
                for t in p["tiers"]:
                    for ans in t["picks"]:
                        w.writerow([d["n"], d["date"], i, p["q"],
                                    p["accepted"], t["name"],
                                    POINTS.get(t["name"], ""), ans])


def main() -> None:
    force = "--force" in sys.argv
    DATA.mkdir(exist_ok=True)
    existing = json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() and not force else []
    have = {d["date"] for d in existing}

    all_dates = sorted(set(re.findall(
        r"/krillion-answers/(\d{4}-\d{2}-\d{2})/",
        fetch("https://krilliongame.com/krillion-answers/"))))
    todo = [d for d in all_dates if d not in have]
    print(f"archive has {len(all_dates)} dates; {len(have)} cached; fetching {len(todo)}")

    scraped = []
    for iso in todo:
        try:
            dive = parse_page(fetch(f"https://krilliongame.com/krillion-answers/{iso}/"), iso)
            scraped.append(dive)
            print(f"  + {iso} dive #{dive['n']}")
        except Exception as e:  # noqa: BLE001
            print(f"  x {iso}: {e}", file=sys.stderr)
        time.sleep(1)

    if not scraped:
        print("no new dives")
    merged = sorted(existing + scraped, key=lambda d: d["date"], reverse=True)
    JSON_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
    write_csv(merged)
    total = sum(p["accepted"] or 0 for d in merged for p in d["prompts"])
    print(f"wrote {len(merged)} dives ({total:,} accepted answers) -> {JSON_PATH.name}, {CSV_PATH.name}")


if __name__ == "__main__":
    main()
