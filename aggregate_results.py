#!/usr/bin/env python3
"""
Aggregate semantic-validation JSON files into a CSV table suitable for the JWS paper.
"""
import argparse
import csv
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--input-dir", required=True)
ap.add_argument("--output", required=True)
args = ap.parse_args()

rows = []
for p in sorted(Path(args.input_dir).glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    rows.append({
        "approach": d.get("approach"),
        "pair": d.get("pair"),
        "Cons": d.get("Cons"),
        "Coh": d.get("Coh"),
        "n_named_classes": d.get("n_named_classes"),
        "n_unsatisfiable_classes": d.get("n_unsatisfiable_classes"),
        "Comp_tau": d.get("Comp_tau"),
        "n_requirements": d.get("n_requirements"),
        "n_entailed": d.get("n_entailed"),
        "n_alignment_axioms_added": d.get("n_alignment_axioms_added"),
        "n_alignment_cells_skipped": d.get("n_alignment_cells_skipped"),
    })

out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    if rows:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

print(f"Wrote {len(rows)} rows to {out}")
