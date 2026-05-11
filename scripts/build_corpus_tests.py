#!/usr/bin/env python3
"""
build_corpus_tests.py — Deterministic corpus-test generator for allergen
validation tables.

For each of the three allergen validation tables, runs every exact and
regex rule against the full set of unique uppercased excipient strings
in the DailyMed bulk catalog and emits a corpus test CSV listing every
hit.

Output schema:
    fda_term         rule from the validation table
    match_type       exact | regex
    matched_string   DailyMed excipient string that hit the rule
    flag_decision    classification from the validation table
    notes            flags empty-match rules or potential review items

Reads:
    data/fullcatalog/dailymed_fullcatalog_raw.csv
    data/fullcatalog/{milk,peg,carmine}_validation.csv
Writes (overwrites):
    data/fullcatalog/corpus_test_{milk,peg,carmine}.csv

Re-running produces byte-identical output. Reuses match semantics from
flag_allergens_fullcatalog.load_validation() — validation tables are the single
source of truth for the match rules.

Run:
    python3 scripts/build_corpus_tests.py
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from flag_allergens_fullcatalog import load_validation
from allergen_filters import EXCIPIENT_DELIMITER

BASE = Path(__file__).parent.parent
RAW = BASE / "data" / "fullcatalog" / "dailymed_fullcatalog_raw.csv"
VALIDATIONS = {
    "milk":    BASE / "data" / "fullcatalog" / "milk_validation.csv",
    "peg":     BASE / "data" / "fullcatalog" / "peg_validation.csv",
    "carmine": BASE / "data" / "fullcatalog" / "carmine_validation.csv",
}
OUT_DIR = BASE / "data" / "fullcatalog"


FIELDS = ["fda_term", "match_type", "matched_string", "flag_decision", "notes"]


def unique_excipient_strings(raw_csv: Path) -> set:
    """Extract every unique uppercased excipient token from the raw catalog."""
    tokens = set()
    with open(raw_csv, "r", newline="") as f:
        for row in csv.DictReader(f):
            raw = (row.get("excipients_raw") or "").strip()
            if not raw:
                continue
            for t in raw.split(EXCIPIENT_DELIMITER):
                t = t.strip().upper()
                if t:
                    tokens.add(t)
    return tokens


def build_for_allergen(allergen: str, val_csv: Path, strings: set) -> list:
    """Apply validation rules to corpus strings; return hit rows."""
    exact, regex = load_validation(val_csv)

    rows = []

    # Invert exact dict for iteration in val-table order. Re-read to get
    # the original fda_term spelling and row ordering.
    val_table = []
    with open(val_csv, "r", newline="") as f:
        for r in csv.DictReader(f):
            val_table.append({
                "fda_term": r["fda_term"].strip(),
                "match_type": r["match_type"].strip(),
                "flag_decision": r["flag_decision"].strip(),
            })

    for vrow in val_table:
        term = vrow["fda_term"]
        match_type = vrow["match_type"]
        decision = vrow["flag_decision"]

        matched_strings = []
        if match_type == "exact":
            if term.upper() in strings:
                matched_strings.append(term.upper())
        elif match_type == "regex":
            pat = re.compile(term, re.IGNORECASE)
            matched_strings = sorted(s for s in strings if pat.search(s))
        else:
            raise ValueError(f"Unknown match_type {match_type!r} for {term}")

        if not matched_strings:
            rows.append({
                "fda_term": term,
                "match_type": match_type,
                "matched_string": "",
                "flag_decision": decision,
                "notes": "NO MATCH in corpus — rule currently inactive",
            })
            continue

        for ms in matched_strings:
            note = ""
            # Milk-specific heuristic flag: MILK THISTLE is a plant (not
            # dairy). Exact-match table does not include it, so it should
            # not actually hit. If a regex rule ever matches it, the
            # note surfaces it for review.
            if allergen == "milk" and "MILK THISTLE" in ms:
                note = "REVIEW — plant (not dairy); not in FARE milk list"
            rows.append({
                "fda_term": term,
                "match_type": match_type,
                "matched_string": ms,
                "flag_decision": decision,
                "notes": note,
            })

    return rows


def main():
    if not RAW.exists():
        print(f"ERROR: raw catalog not found: {RAW}", file=sys.stderr)
        sys.exit(1)
    for p in VALIDATIONS.values():
        if not p.exists():
            print(f"ERROR: validation table not found: {p}", file=sys.stderr)
            sys.exit(1)

    print(f"Loading unique excipient strings from {RAW.relative_to(BASE)}...")
    strings = unique_excipient_strings(RAW)
    print(f"  {len(strings):,} unique uppercased strings.\n")

    for allergen, val_csv in VALIDATIONS.items():
        print(f"--- {allergen} ---")
        rows = build_for_allergen(allergen, val_csv, strings)
        out = OUT_DIR / f"corpus_test_{allergen}.csv"
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        n_hits = sum(1 for r in rows if r["matched_string"])
        n_dead = sum(1 for r in rows if not r["matched_string"])
        n_review = sum(1 for r in rows if r["notes"].startswith("REVIEW"))
        print(f"  {len(rows)} rows → {out.relative_to(BASE)}")
        print(f"    {n_hits} matched, {n_dead} inactive, {n_review} flagged for review\n")


if __name__ == "__main__":
    main()
