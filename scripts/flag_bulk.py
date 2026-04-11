#!/usr/bin/env python3
"""
flag_bulk.py — Apply gluten flags to the filtered bulk DailyMed dataset.

Reads the filtered bulk dataset (72,358 rows) and the bulk excipient validation
table (171 entries), then assigns each product a four-tier gluten flag based on
the worst excipient in its inactive ingredient list.

Worst-excipient rule:
  any  contains_gluten → contains_gluten
  else any  unknown    → unknown
  else if all matched as gluten_free OR no matches at all → gluten_free
  else if excipients_raw is empty → no_data

Excipient string normalization is .upper().strip(), matching the case-normalization
decision in CLAUDE.md "Bulk Excipient Validation Decisions".

The pipeline is fully deterministic. No AI / LLM / inference at any step.

Input:
  data/bulk/dailymed_bulk_filtered.csv     (72,358 rows × 43 columns)
  data/bulk/excipient_validation.csv       (171 entries: 105 gluten_free, 35 unknown, 31 contains_gluten)

Output:
  data/bulk/dailymed_bulk_flagged.csv      (72,358 rows × 45 columns; adds gluten_flag, flagged_excipients)

Run:
  python3 scripts/flag_bulk.py
"""

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
INPUT_CSV = BASE_DIR / "data" / "bulk" / "dailymed_bulk_filtered.csv"
VALIDATION_CSV = BASE_DIR / "data" / "bulk" / "excipient_validation.csv"
OUTPUT_CSV = BASE_DIR / "data" / "bulk" / "dailymed_bulk_flagged.csv"

# Excipient string delimiter used in the bulk dataset's excipients_raw column.
# Matches the format produced by extract_bulk.py.
EXCIPIENT_DELIMITER = "; "


def load_validation_table():
    """Load the validation CSV into a {fda_term: flag_decision} dict.

    Keys are normalized via .upper().strip() for case-insensitive lookup.
    """
    df = pd.read_csv(VALIDATION_CSV, dtype=str, keep_default_na=False)
    lookup = {}
    for _, row in df.iterrows():
        key = row["fda_term"].upper().strip()
        lookup[key] = row["flag_decision"]
    return lookup


def classify_row(excipients_raw, lookup):
    """Apply the worst-excipient rule to one product row.

    Returns (gluten_flag, flagged_excipients_string).
    flagged_excipients lists the specific excipients that drove the flag
    (the contains_gluten or unknown ones); empty for gluten_free / no_data.
    """
    raw = excipients_raw.strip()
    if not raw:
        return ("no_data", "")

    excipients = [e.strip() for e in raw.split(EXCIPIENT_DELIMITER) if e.strip()]
    if not excipients:
        return ("no_data", "")

    contains_gluten_hits = []
    unknown_hits = []
    for exc in excipients:
        flag = lookup.get(exc.upper())
        if flag == "contains_gluten":
            contains_gluten_hits.append(exc)
        elif flag == "unknown":
            unknown_hits.append(exc)

    if contains_gluten_hits:
        return ("contains_gluten", EXCIPIENT_DELIMITER.join(contains_gluten_hits))
    if unknown_hits:
        return ("unknown", EXCIPIENT_DELIMITER.join(unknown_hits))
    return ("gluten_free", "")


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: filtered input not found: {INPUT_CSV}", file=sys.stderr)
        print("Run scripts/filter_bulk.py first.", file=sys.stderr)
        sys.exit(1)
    if not VALIDATION_CSV.exists():
        print(f"ERROR: validation table not found: {VALIDATION_CSV}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading validation table from {VALIDATION_CSV.relative_to(BASE_DIR)}...")
    lookup = load_validation_table()
    print(f"  Loaded {len(lookup):,} excipient entries.")
    flag_counts = pd.Series(list(lookup.values())).value_counts()
    for flag, count in flag_counts.items():
        print(f"    {flag}: {count}")
    print()

    print(f"Loading filtered dataset from {INPUT_CSV.relative_to(BASE_DIR)}...")
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    print(f"  Loaded {len(df):,} rows × {len(df.columns)} columns.\n")

    print("Applying gluten flags...")
    flags = []
    flagged_excipients = []
    for raw in df["excipients_raw"]:
        flag, hits = classify_row(raw, lookup)
        flags.append(flag)
        flagged_excipients.append(hits)

    df["gluten_flag"] = flags
    df["flagged_excipients"] = flagged_excipients
    print("  Done.\n")

    print("Final gluten_flag distribution:")
    counts = df["gluten_flag"].value_counts()
    total = len(df)
    for flag in ("gluten_free", "unknown", "contains_gluten", "no_data"):
        n = counts.get(flag, 0)
        pct = n / total * 100
        print(f"  {flag:>16}: {n:>6,}  ({pct:5.2f}%)")
    print(f"  {'TOTAL':>16}: {total:>6,}")
    print()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV.relative_to(BASE_DIR)} ({len(df):,} rows × {len(df.columns)} columns)")


if __name__ == "__main__":
    main()
