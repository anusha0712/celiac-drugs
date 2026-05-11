#!/usr/bin/env python3
"""
analyze_dpi_labels.py — DPI contraindication-level label analysis.

For each unique DPI set_id, parse the SPL XML and classify milk-protein
warning level per label.

DPI identification uses the shared allergen_filters.is_dpi() — pMDIs
(AEROSOL, METERED) are excluded because they are propellant-based and
do not use lactose carriers (not part of the CMPA harm anchor).

Output: data/fullcatalog/dpi_label_analysis.csv
"""

import csv
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from spl_label_parser import (build_setid_index, get_warning_sections,
                              classify_warning_level, ALLERGY_CONTEXT)
from allergen_filters import is_dpi

BASE = Path(__file__).parent.parent
FLAGGED = BASE / "data" / "fullcatalog" / "allergens_fullcatalog_flagged.csv"
OUT = BASE / "data" / "fullcatalog" / "dpi_label_analysis.csv"

# Allergen-name regex. ALLERGY_CONTEXT is shared from spl_label_parser
# (see methodology.md §5 for honest framing of the vocabulary choice).
#
# Asymmetry disclosure: `\bdairy` appears here but is NOT on the FARE
# milk-allergen list (and therefore NOT in milk_validation.csv). Real-
# world labels use "dairy allergy" as warning vocabulary, so the
# warning detector includes it intentionally. The contains_milk flag
# classification stays anchored to the FARE list (no dairy).
# Documented in methodology.md §5 + limitations.md §Milk.
MILK_NAME = (r"(?:milk[- ]?protein|cow'?s?\s+milk|\bmilk\s+allerg"
             r"|\bdairy|\bcasein|\bwhey|\blactalbumin"
             r"|\blactoglobulin|\blactoferrin)")

MILK_PATTERNS = [
    rf"{MILK_NAME}.{{0,80}}{ALLERGY_CONTEXT}",
    rf"{ALLERGY_CONTEXT}.{{0,80}}{MILK_NAME}",
]


def main():
    print("Loading flagged catalog...")
    rows_by_setid = {}
    with open(FLAGGED, "r", newline="") as f:
        for row in csv.DictReader(f):
            if is_dpi(row.get("dosage_form"), row.get("route")):
                sid = row.get("set_id")
                if sid and sid not in rows_by_setid:
                    rows_by_setid[sid] = row
    print(f"  Identified {len(rows_by_setid)} unique DPI set_ids.\n")

    print("Loading set_id → ZIP index...")
    index = build_setid_index()

    print("Parsing SPL XML for each DPI set_id...")
    results = []
    empty = 0
    for i, (sid, row) in enumerate(rows_by_setid.items(), 1):
        sections = get_warning_sections(sid, index)
        if not sections:
            empty += 1
            level, code, snippet = "set_id_not_found_or_empty", "", ""
        else:
            level, code, snippet = classify_warning_level(sections, MILK_PATTERNS)
        results.append({
            "set_id": sid,
            "drug_name": row.get("drug_name", ""),
            "ndc_code": row.get("ndc_code", ""),
            "manufacturer": row.get("manufacturer", ""),
            "dosage_form": row.get("dosage_form", ""),
            "warning_level": level,
            "loinc_code": code,
            "triggering_text": snippet[:300],
        })
        if i % 20 == 0:
            print(f"    {i}/{len(rows_by_setid)} parsed")
    print(f"  Done. {empty} set_ids had no warning-relevant sections.\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()) if results else
                           ["set_id", "drug_name", "ndc_code", "manufacturer",
                            "dosage_form", "warning_level", "loinc_code",
                            "triggering_text"])
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {OUT.relative_to(BASE)} — {len(results)} rows.\n")

    counts = Counter(r["warning_level"] for r in results)
    print("Warning-level distribution:")
    for level, n in counts.most_common():
        print(f"  {level:>35}: {n}")


if __name__ == "__main__":
    main()
