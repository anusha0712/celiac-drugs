#!/usr/bin/env python3
"""
flag_allergens_fullcatalog.py — Apply milk, PEG, and carmine flags to the RAW bulk
DailyMed catalog (199,961 rows, pre-filtering).

Reads:
    data/fullcatalog/dailymed_fullcatalog_raw.csv               (raw catalog)
    data/fullcatalog/milk_validation.csv            (exact-match + exclusion entries)
    data/fullcatalog/peg_validation.csv             (regex-only entries)
    data/fullcatalog/carmine_validation.csv         (exact + regex entries)

Writes:
    data/fullcatalog/allergens_fullcatalog_flagged.csv (raw + 6 new columns)

Added columns:
    milk_flag, milk_flagged_excipients
    peg_flag, peg_flagged_excipients
    carmine_flag, carmine_flagged_excipients

Flag tiers per allergen:
    contains_<allergen>     at least one excipient is a source
    <allergen>_free         no sources found, excipients_raw non-empty
    no_data                 excipients_raw is empty / missing

Worst-excipient rule:
    any contains_<allergen> → contains_<allergen>
    else if excipients_raw empty → no_data
    else → <allergen>_free

The pipeline is fully deterministic. No AI / LLM / inference at any step.
The starting dataset is the RAW catalog (unfiltered) — route and dosage_form
columns are preserved so downstream analysis can slice by harm category
(e.g. DPIs for milk, bowel preps for PEG, tablet coatings for carmine).

Run:
    python3 scripts/flag_allergens_fullcatalog.py
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from allergen_filters import EXCIPIENT_DELIMITER, passes_baseline

BASE_DIR = Path(__file__).parent.parent
RAW_CSV = BASE_DIR / "data" / "fullcatalog" / "dailymed_fullcatalog_raw.csv"
MILK_CSV = BASE_DIR / "data" / "fullcatalog" / "milk_validation.csv"
PEG_CSV = BASE_DIR / "data" / "fullcatalog" / "peg_validation.csv"
CARMINE_CSV = BASE_DIR / "data" / "fullcatalog" / "carmine_validation.csv"
OUT_CSV = BASE_DIR / "data" / "fullcatalog" / "allergens_fullcatalog_flagged.csv"

ALLERGENS = ("milk", "peg", "carmine")


def load_validation(csv_path):
    """Load a validation CSV into (exact_lookup, regex_patterns).

    exact_lookup: dict {uppercased_token: flag_decision}
    regex_patterns: list of (compiled_pattern, flag_decision) tuples

    Malformed regex patterns produce a clear row-context error and
    exit, rather than a cryptic re.error mid-pipeline.
    """
    exact = {}
    regex = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row_no, row in enumerate(reader, start=2):  # +1 for header
            term = row["fda_term"].strip()
            match_type = row["match_type"].strip()
            decision = row["flag_decision"].strip()
            if match_type == "exact":
                exact[term.upper()] = decision
            elif match_type == "regex":
                try:
                    regex.append((re.compile(term, re.IGNORECASE), decision))
                except re.error as e:
                    sys.exit(
                        f"ERROR: malformed regex in {csv_path} at row {row_no}.\n"
                        f"  fda_term: {term!r}\n"
                        f"  re.error: {e}"
                    )
            else:
                raise ValueError(
                    f"Unknown match_type {match_type!r} in {csv_path} "
                    f"at row {row_no} (term={term!r})"
                )
    return exact, regex


def classify(excipients_raw, exact, regex, allergen):
    """Apply the worst-excipient rule for one allergen to one row."""
    raw = (excipients_raw or "").strip()
    if not raw:
        return ("no_data", "")

    tokens = [t.strip() for t in raw.split(EXCIPIENT_DELIMITER) if t.strip()]
    if not tokens:
        return ("no_data", "")

    contains_key = f"contains_{allergen}"
    contains_hits = []
    for tok in tokens:
        tok_up = tok.upper()
        flag = exact.get(tok_up)
        if flag is None:
            for pat, dec in regex:
                if pat.search(tok_up):
                    flag = dec
                    break
        if flag == contains_key:
            contains_hits.append(tok)

    if contains_hits:
        return (contains_key, EXCIPIENT_DELIMITER.join(contains_hits))
    return (f"{allergen}_free", "")


def main():
    if not RAW_CSV.exists():
        print(f"ERROR: raw catalog not found: {RAW_CSV}", file=sys.stderr)
        sys.exit(1)
    for p in (MILK_CSV, PEG_CSV, CARMINE_CSV):
        if not p.exists():
            print(f"ERROR: validation table not found: {p}", file=sys.stderr)
            print("Run scripts/build_allergens_validation.py first.", file=sys.stderr)
            sys.exit(1)

    print("Loading validation tables...")
    tables = {
        "milk": load_validation(MILK_CSV),
        "peg": load_validation(PEG_CSV),
        "carmine": load_validation(CARMINE_CSV),
    }
    for allergen, (exact, regex) in tables.items():
        print(f"  {allergen}: {len(exact)} exact, {len(regex)} regex")
    print()

    print(f"Reading raw catalog from {RAW_CSV.relative_to(BASE_DIR)}...")
    with open(RAW_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        input_fieldnames = reader.fieldnames
        all_rows = list(reader)
    print(f"  Loaded {len(all_rows):,} raw rows × {len(input_fieldnames)} columns.")

    # Task #28 baseline filter: drop homeopathic / unapproved /
    # non-drug rows BEFORE allergen flagging. Without this filter,
    # milk counts in particular were polluted by ~25% (4,436
    # homeopathic + 4,905 unapproved). See methodology.md §1.x and
    # limitations.md per-allergen sections.
    print("Applying baseline filter (homeopathic + unapproved + non-drug exclusion)...")
    rows = [r for r in all_rows if passes_baseline(r)]
    dropped = len(all_rows) - len(rows)
    print(f"  Dropped {dropped:,} rows; kept {len(rows):,} rows for allergen flagging.\n")

    new_cols = []
    for allergen in ALLERGENS:
        new_cols.append(f"{allergen}_flag")
        new_cols.append(f"{allergen}_flagged_excipients")
    output_fieldnames = list(input_fieldnames) + new_cols

    print("Applying flags...")
    counts = {a: {} for a in ALLERGENS}
    for row in rows:
        raw_exc = row.get("excipients_raw", "")
        for allergen in ALLERGENS:
            exact, regex = tables[allergen]
            flag, hits = classify(raw_exc, exact, regex, allergen)
            row[f"{allergen}_flag"] = flag
            row[f"{allergen}_flagged_excipients"] = hits
            counts[allergen][flag] = counts[allergen].get(flag, 0) + 1
    print("  Done.\n")

    total = len(rows)
    for allergen in ALLERGENS:
        print(f"{allergen}_flag distribution:")
        for tier in (f"contains_{allergen}", f"{allergen}_free", "no_data"):
            n = counts[allergen].get(tier, 0)
            pct = n / total * 100
            print(f"  {tier:>22}: {n:>7,}  ({pct:5.2f}%)")
        print(f"  {'TOTAL':>22}: {total:>7,}\n")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing {OUT_CSV.relative_to(BASE_DIR)}...")
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows):,} rows × {len(output_fieldnames)} columns.")


if __name__ == "__main__":
    main()
