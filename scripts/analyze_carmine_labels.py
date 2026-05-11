#!/usr/bin/env python3
"""
analyze_carmine_labels.py — carmine contraindication-level label analysis.

Scope: all products flagged contains_carmine under the hardened
validation table. Parse SPL XML, classify carmine-allergy warning level.

Output: data/fullcatalog/carmine_label_analysis.csv
"""

import csv
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from spl_label_parser import (build_setid_index, get_warning_sections,
                              classify_warning_level, ALLERGY_CONTEXT)

BASE = Path(__file__).parent.parent
FLAGGED = BASE / "data" / "fullcatalog" / "allergens_fullcatalog_flagged.csv"
OUT = BASE / "data" / "fullcatalog" / "carmine_label_analysis.csv"

# Allergen-name regex. ALLERGY_CONTEXT is shared from spl_label_parser
# (see methodology.md §5 for honest framing of the vocabulary choice).
# Carmine name terms match the carmine_validation.csv exact + regex
# entries (21 CFR 73.100 + GSRS UNII synonym record).
CARMINE_NAME = (r"(?:\bcarmine|\bcochineal|\bcarminic\s+acid"
                r"|\bCI\s*75470|\bnatural\s+red\s+4"
                r"|\bE[- ]?120\b|\bINS[- ]?120\b)")

CARMINE_PATTERNS = [
    rf"{CARMINE_NAME}.{{0,80}}{ALLERGY_CONTEXT}",
    rf"{ALLERGY_CONTEXT}.{{0,80}}{CARMINE_NAME}",
]


def main():
    print("Loading flagged catalog...")
    rows_by_setid = {}
    with open(FLAGGED, "r", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("carmine_flag") != "contains_carmine":
                continue
            sid = row.get("set_id")
            if sid and sid not in rows_by_setid:
                rows_by_setid[sid] = row
    print(f"  {len(rows_by_setid)} unique set_ids flagged contains_carmine.\n")

    index = build_setid_index()

    print("Parsing SPL XML...")
    results = []
    empty = 0
    for i, (sid, row) in enumerate(rows_by_setid.items(), 1):
        sections = get_warning_sections(sid, index)
        if not sections:
            empty += 1
            level, code, snippet = "set_id_not_found_or_empty", "", ""
        else:
            level, code, snippet = classify_warning_level(sections, CARMINE_PATTERNS)
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
        if i % 50 == 0:
            print(f"    {i}/{len(rows_by_setid)} parsed")
    print(f"  Done. {empty} set_ids had no warning-relevant sections.\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()) if results else
                           ["set_id", "drug_name", "ndc_code", "manufacturer",
                            "dosage_form", "approval_type", "warning_level",
                            "loinc_code", "triggering_text"])
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {OUT.relative_to(BASE)} — {len(results)} rows.\n")

    counts = Counter(r["warning_level"] for r in results)
    print("Warning-level distribution:")
    for level, n in counts.most_common():
        print(f"  {level:>35}: {n}")


if __name__ == "__main__":
    main()
