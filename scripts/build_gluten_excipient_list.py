#!/usr/bin/env python3
"""
build_gluten_excipient_list.py — Extract gluten-adjacent excipients from the full DailyMed catalog.

Reads data/fullcatalog/dailymed_fullcatalog_raw.csv, identifies excipient strings that match
gluten-related keywords, subtracts terms already classified in the pilot
validation table, and outputs a research worklist of new terms to classify.

Keywords come from three sources:
  1. Portuguese study (Figueiredo et al. 2025) Table 1 excipient list:
     wheat, rye, barley, semolina, bran, malt, oats, starch, glucose syrup,
     pregelatinized starch, modified starch, gelatinized starch,
     sodium carboxymethyl starch, xanthan gum
  2. Latin botanical names for gluten grains:
     avena (oat), triticum (wheat), hordeum (barley), secale (rye)
  3. Starch chemistry terms:
     glycolate (catches SSG variants), pregelatinized, dextrin

Output:
  data/fullcatalog/gluten_excipient_research_worklist.csv
"""

import csv
import re
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from allergen_filters import EXCIPIENT_DELIMITER

BASE_DIR = Path(__file__).parent.parent
BULK_CSV = BASE_DIR / "data" / "fullcatalog" / "dailymed_fullcatalog_raw.csv"
PILOT_VALIDATION = BASE_DIR / "data" / "pilot" / "gluten_pilot_validation.csv"
OUTPUT_DIR = BASE_DIR / "data" / "fullcatalog"
WORKLIST_CSV = OUTPUT_DIR / "excipient_research_worklist.csv"

# --- Keyword patterns ---
# Word-boundary regex to avoid false matches (e.g., "oat" in "coated")
# Each tuple: (keyword_label, compiled regex)
KEYWORDS = [
    # From Portuguese study Table 1
    ("wheat", re.compile(r"\bWHEAT\b")),
    ("rye", re.compile(r"\bRYE\b")),
    ("barley", re.compile(r"\bBARLEY\b")),
    ("semolina", re.compile(r"\bSEMOLINA\b")),
    ("bran", re.compile(r"\bBRAN\b")),
    ("malt", re.compile(r"\bMALT\b")),
    ("oat", re.compile(r"\bOAT\b")),
    ("oats", re.compile(r"\bOATS\b")),
    ("starch", re.compile(r"\bSTARCH\b")),
    ("gluten", re.compile(r"\bGLUTEN\b")),
    ("glucose", re.compile(r"\bGLUCOSE\b")),
    ("pregelatinized", re.compile(r"\bPREGELATINIZED\b")),
    ("flour", re.compile(r"\bFLOUR\b")),
    ("grain", re.compile(r"\bGRAIN\b")),
    # Latin botanical names for gluten grains
    ("avena", re.compile(r"\bAVENA\b")),
    ("triticum", re.compile(r"\bTRITICUM\b")),
    ("hordeum", re.compile(r"\bHORDEUM\b")),
    ("secale", re.compile(r"\bSECALE\b")),
    # Starch chemistry terms
    ("glycolate", re.compile(r"\bGLYCOLATE\b")),
    ("dextrin", re.compile(r"\bDEXTRIN\b")),
    # Catch-all for gum (some gums use grain-based fermentation substrates)
    ("gum", re.compile(r"\bGUM\b")),
]


def load_pilot_terms():
    """Load already-classified terms from the pilot validation table."""
    terms = set()
    with open(PILOT_VALIDATION, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            terms.add(row["fda_term"].strip().upper())
    return terms


def extract_unique_excipients():
    """Extract all unique excipient strings from the bulk CSV."""
    counts = Counter()
    total_rows = 0
    empty_rows = 0

    with open(BULK_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            raw = row.get("excipients_raw", "").strip()
            if not raw:
                empty_rows += 1
                continue
            for exc in raw.split(EXCIPIENT_DELIMITER):
                exc = exc.strip()
                if exc:
                    counts[exc.upper()] += 1

    print(f"Total rows: {total_rows:,}")
    print(f"Empty excipient rows: {empty_rows:,}")
    print(f"Unique excipient strings (case-normalized): {len(counts):,}")
    return counts


def find_keyword_matches(excipient_counts):
    """Find excipients matching gluten-adjacent keywords."""
    matches = {}  # {term: [keywords_matched]}
    for term in excipient_counts:
        matched_keywords = []
        for label, pattern in KEYWORDS:
            if pattern.search(term):
                matched_keywords.append(label)
        if matched_keywords:
            matches[term] = matched_keywords
    return matches


def main():
    print("=" * 60)
    print("Building excipient research worklist for full catalog")
    print("=" * 60)
    print()

    # Step 1: Extract unique excipients
    print("--- Extracting unique excipients ---")
    excipient_counts = extract_unique_excipients()
    print()

    # Step 2: Load pilot validation table
    print("--- Loading pilot validation table ---")
    pilot_terms = load_pilot_terms()
    print(f"Pilot entries: {len(pilot_terms)}")
    print()

    # Step 3: Find keyword matches
    print("--- Keyword search ---")
    all_matches = find_keyword_matches(excipient_counts)
    print(f"Total keyword matches: {len(all_matches)}")

    already_classified = {t for t in all_matches if t in pilot_terms}
    new_matches = {t: kw for t, kw in all_matches.items() if t not in pilot_terms}
    print(f"Already in pilot table: {len(already_classified)}")
    print(f"NEW terms to classify: {len(new_matches)}")
    print()

    # Step 4: Write worklist
    print("--- Writing worklist ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sorted_terms = sorted(new_matches.keys(),
                          key=lambda t: excipient_counts[t],
                          reverse=True)

    with open(WORKLIST_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fda_term", "product_count", "keywords_matched"])
        for term in sorted_terms:
            writer.writerow([
                term,
                excipient_counts[term],
                EXCIPIENT_DELIMITER.join(new_matches[term]),
            ])

    print(f"Wrote {len(sorted_terms)} terms to {WORKLIST_CSV}")
    print()

    # Summary
    print("--- Summary by keyword ---")
    keyword_counts = Counter()
    for term, kws in new_matches.items():
        for kw in kws:
            keyword_counts[kw] += 1
    for kw, count in keyword_counts.most_common():
        print(f"  {kw}: {count} new terms")

    print()
    print("--- Top 20 new terms by product count ---")
    for term in sorted_terms[:20]:
        print(f"  {excipient_counts[term]:>6,}  {term}")
        print(f"         keywords: {', '.join(new_matches[term])}")


if __name__ == "__main__":
    main()
