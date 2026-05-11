#!/usr/bin/env python3
"""
analyze_peg_labels.py — PEG contraindication-level label analysis.

Scope: products flagged contains_peg under the tight-scope validation
table AND in the oral-solids slice (shared filter from allergen_filters).

Output: data/fullcatalog/peg_label_analysis.csv
"""

import csv
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from spl_label_parser import (build_setid_index, get_warning_sections,
                              classify_warning_level, ALLERGY_CONTEXT)
from allergen_filters import is_oral_solid, is_oral

BASE = Path(__file__).parent.parent
FLAGGED = BASE / "data" / "fullcatalog" / "allergens_fullcatalog_flagged.csv"
OUT = BASE / "data" / "fullcatalog" / "peg_label_analysis.csv"

# Allergen-name regex. ALLERGY_CONTEXT is shared from spl_label_parser
# (see methodology.md §5 for honest framing of the vocabulary choice).
#
# Asymmetry disclosure (Task #23 resolution 2026-04-23): `\bPEG\b` is
# included here in the warning detector to catch label-text vocabulary
# like "PEG-allergic" / "PEG hypersensitivity" — but is NOT in
# peg_validation.csv. Adding `\bPEG\b` to the validation table would
# broaden the flag classification (it matches 264 PEG-N derivative
# excipient strings — polysorbates, polyoxyl, BIS-PEG, etc.) past the
# tight-scope decision (methodology §3.5 / §3.6). Warning detection
# runs against SPL warning-section TEXT; flag classification runs
# against excipient STRINGS. Different domains. Documented in
# methodology.md §5 + limitations.md §PEG.
PEG_NAME = (r"(?:\bpolyethylene\s+glycol|\bpolyethylene\s+oxide"
            r"|\bmacrogol|\bcarbowax|\bPEG\b)")

PEG_PATTERNS = [
    rf"{PEG_NAME}.{{0,80}}{ALLERGY_CONTEXT}",
    rf"{ALLERGY_CONTEXT}.{{0,80}}{PEG_NAME}",
]


def main():
    print("Loading flagged catalog for PEG oral-solids rows...")
    rows_by_setid = {}
    with open(FLAGGED, "r", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("peg_flag") != "contains_peg":
                continue
            if not is_oral(row.get("route")):
                continue
            if not is_oral_solid(row.get("dosage_form")):
                continue
            sid = row.get("set_id")
            if sid and sid not in rows_by_setid:
                rows_by_setid[sid] = row
    print(f"  {len(rows_by_setid):,} unique set_ids.\n")

    index = build_setid_index()

    print("Parsing SPL XML (this may take a few minutes)...")
    results = []
    empty = 0
    total = len(rows_by_setid)
    for i, (sid, row) in enumerate(rows_by_setid.items(), 1):
        sections = get_warning_sections(sid, index)
        if not sections:
            empty += 1
            level, code, snippet = "set_id_not_found_or_empty", "", ""
        else:
            level, code, snippet = classify_warning_level(sections, PEG_PATTERNS)
        results.append({
            "set_id": sid,
            "drug_name": row.get("drug_name", ""),
            "ndc_code": row.get("ndc_code", ""),
            "manufacturer": row.get("manufacturer", ""),
            "dosage_form": row.get("dosage_form", ""),
            "approval_type": row.get("approval_type", ""),
            "warning_level": level,
            "loinc_code": code,
            "triggering_text": snippet[:300],
        })
        if i % 500 == 0:
            print(f"    {i:,}/{total:,} parsed")
    print(f"  Done. {empty} set_ids had no warning-relevant sections.\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()) if results else
                           ["set_id", "drug_name", "ndc_code", "manufacturer",
                            "dosage_form", "approval_type", "warning_level",
                            "loinc_code", "triggering_text"])
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {OUT.relative_to(BASE)} — {len(results):,} rows.\n")

    counts = Counter(r["warning_level"] for r in results)
    print("Warning-level distribution:")
    for level, n in counts.most_common():
        print(f"  {level:>35}: {n:,}")


if __name__ == "__main__":
    main()
