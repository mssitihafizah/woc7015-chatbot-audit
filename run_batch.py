"""Run a prompt file against your configured chatbot and log every call.

Prompt file (CSV) columns:  prompt_id, category, prompt            (red_team, ai_generated)
                            prompt_id, category, pair_id, role, prompt   (metamorphic)
A multi-turn prompt separates turns with ' ||| ' (the label then applies to the last turn).
Each repeat starts a fresh session. Repeat k uses seed = card seed + k - 1.

Examples
  python run_batch.py --card cards/C07.json --prompts examples/red_team_example.csv --type red_team --repeats 5
  python run_batch.py --card cards/C07.json --prompts my_pairs.csv --type metamorphic --repeats 1
  python run_batch.py --card cards/C07.json --prompts examples/red_team_example.csv --type red_team --dry-run
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import Chatbot, DryRunClient, load_card


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--type", required=True, choices=["red_team", "metamorphic", "ai_generated", "manual"])
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--out", default=None, help="log CSV (default logs/<candidate>_log.csv)")
    ap.add_argument("--dry-run", action="store_true", help="no API calls; tests your files and log format")
    a = ap.parse_args()

    card = load_card(a.card)
    out = a.out or os.path.join("logs", f"{card['candidate_id']}_log.csv")
    if a.dry_run:
        out = out.replace(".csv", "_DRYRUN.csv")
    bot = Chatbot(card, out, client=DryRunClient() if a.dry_run else None)

    with open(a.prompts, encoding="utf8", newline="") as f:
        rows = list(csv.DictReader(f))
    total = len(rows) * a.repeats
    done = 0
    for row in rows:
        turns = [t.strip() for t in row["prompt"].split("|||")]
        for k in range(1, a.repeats + 1):
            bot.new_session()
            for t in turns:
                bot.ask(t, test_type=a.type, category=row.get("category", ""),
                        prompt_id=row.get("prompt_id", ""), pair_id=row.get("pair_id", ""),
                        role=row.get("role", ""), run_number=k, seed=card["seed"] + k - 1)
            done += 1
            if done % 10 == 0 or done == total:
                print(f"{done}/{total} runs logged -> {out}")
    print("Done. Now open the log and fill in label, label_reason (and audit_verdict for Part C).")


if __name__ == "__main__":
    main()
