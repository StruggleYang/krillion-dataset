#!/bin/sh
# regenerate data/krillion_answers.csv from the JSON (no network needed)
cd "$(dirname "$0")/.." || exit 1
python3 - <<'EOF'
import json, csv
POINTS = {"One in a Krillion": 100, "Deep cut": 85, "Rare": 60,
          "Schooler": 30, "Too Clever": 15, "Plankton": 10}
dives = json.load(open("data/krillion_dives.json"))
with open("data/krillion_answers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dive_number","date","prompt_number","prompt","accepted_answers","tier","points","answer"])
    for d in dives:
        for i, p in enumerate(d["prompts"], 1):
            for t in p["tiers"]:
                for a in t["picks"]:
                    w.writerow([d["n"], d["date"], i, p["q"], p["accepted"], t["name"], POINTS.get(t["name"], ""), a])
print("csv regenerated:", sum(1 for _ in open("data/krillion_answers.csv")) - 1, "answer rows")
EOF
