#!/usr/bin/env python3
"""
filter_gluten_fullcatalog.py — Apply the 6-step filter pipeline to the bulk DailyMed catalog.

Reads the raw bulk extraction (199,961 rows) and produces a filtered dataset
containing only FDA-recognized human medications that are directly delivered
to the GI tract by swallowing.

Filter pipeline (locked order):
  1. document_type    — keep only HUMAN OTC / HUMAN PRESCRIPTION / HUMAN COMPOUNDED labels
  2. bulk_category    — drop homeopathic
  3. route            — keep only ORAL
  4. dosage_form      — drop mouth-only forms, wrong-route data errors, and other not-swallowed forms
  5. approval_type    — keep only ANDA / NDA / NDA AG / BLA / OTC monograph
  6. mouthwash slip   — drop products named "Mouthwash"/"Mouth Wash"/"Mouth Rinse"/"Gargle"
                        whose dosage_form is something other than MOUTHWASH

Filter order does NOT change the final result (set intersection is commutative).
The pipeline is fully deterministic. No AI / LLM / inference at any step.

Input:  data/fullcatalog/dailymed_fullcatalog_raw.csv          (199,961 rows × 43 columns)
Output: data/fullcatalog/gluten_fullcatalog_filtered.csv (~72,358 rows × 43 columns)

Run:
  python3 scripts/filter_gluten_fullcatalog.py
"""

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
INPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "dailymed_fullcatalog_raw.csv"
OUTPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "gluten_fullcatalog_filtered.csv"


# ============================================================
# Filter rule sets (locked per plan 2026-04-10)
# ============================================================

KEEP_DOCUMENT_TYPES = {
    "HUMAN OTC DRUG LABEL",
    "HUMAN PRESCRIPTION DRUG LABEL",
    "HUMAN PRESCRIPTION DRUG LABEL WITH HIGHLIGHTS",
    "HUMAN COMPOUNDED DRUG LABEL",
}

DROP_BULK_CATEGORIES = {
    "homeopathic",
}

KEEP_ROUTES = {
    "ORAL",
}

DROP_DOSAGE_FORMS = {
    # Group A — mouth-only delivery (not swallowed)
    "LOZENGE",
    "MOUTHWASH",
    "GUM, CHEWING",
    "PASTE, DENTIFRICE",
    "POWDER, DENTIFRICE",
    "GEL, DENTIFRICE",
    "RINSE",
    "PASTE",
    "PASTILLE",
    "TROCHE",
    # Group B — wrong-route data errors (route says ORAL but form is for a different route)
    "INJECTION",
    "INJECTION, POWDER, FOR SOLUTION",
    "INJECTION, POWDER, LYOPHILIZED, FOR SOLUTION",
    "INJECTION, SOLUTION",
    "INJECTION, SUSPENSION",
    "AEROSOL, METERED",
    "AEROSOL, SPRAY",
    "AEROSOL, POWDER",
    "INHALANT",
    "SPRAY, METERED",
    "SPRAY, SUSPENSION",
    "CREAM",
    "LOTION",
    "OINTMENT",
    "SWAB",
    "SPONGE",
    "DRESSING",
    "PATCH",
    # Group C — other not-swallowed forms
    "SPRAY",
    "GEL",
    "FILM",
    "FILM, SOLUBLE",
    "STRIP",
    "TABLET, ORALLY DISINTEGRATING",
    "TABLET, ORALLY DISINTEGRATING, DELAYED RELEASE",
}

KEEP_APPROVAL_TYPES = {
    "ANDA",
    "NDA",
    "NDA AUTHORIZED GENERIC",
    "BLA",
    "OTC MONOGRAPH DRUG",
    "OTC MONOGRAPH FINAL",
    "OTC MONOGRAPH NOT FINAL",
}

# Mouthwash-by-name slip — products named like mouthwash but tagged with a
# non-MOUTHWASH dosage_form. Caught with a regex on drug_name.
MOUTHWASH_NAME_PATTERN = r"(?:MOUTHWASH|MOUTH WASH|MOUTH RINSE|MOUTH GARGLE|GARGLE)"


def log(step_num, name, before, after):
    dropped = before - after
    pct = (dropped / before * 100) if before else 0
    print(f"  Step {step_num} ({name}): {before:>7,} → {after:>7,}  "
          f"(dropped {dropped:>6,}, {pct:5.2f}%)")


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: input file not found: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading {INPUT_CSV.relative_to(BASE_DIR)}...")
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    initial = len(df)
    print(f"Loaded {initial:,} rows.\n")

    print("Applying filter pipeline:")

    # Pre-compute normalized columns once for efficiency
    df["_doctype_n"] = df["document_type"].str.upper().str.strip()
    df["_route_n"] = df["route"].str.upper().str.strip()
    df["_dosage_n"] = df["dosage_form"].str.upper().str.strip()
    df["_approval_n"] = df["approval_type"].str.upper().str.strip()
    df["_drugname_n"] = df["drug_name"].str.upper().str.strip()

    # Step 1 — document_type
    before = len(df)
    df = df[df["_doctype_n"].isin(KEEP_DOCUMENT_TYPES)]
    log(1, "document_type     ", before, len(df))

    # Step 2 — bulk_category
    before = len(df)
    df = df[~df["bulk_category"].isin(DROP_BULK_CATEGORIES)]
    log(2, "bulk_category     ", before, len(df))

    # Step 3 — route
    before = len(df)
    df = df[df["_route_n"].isin(KEEP_ROUTES)]
    log(3, "route             ", before, len(df))

    # Step 4 — dosage_form
    before = len(df)
    df = df[~df["_dosage_n"].isin(DROP_DOSAGE_FORMS)]
    log(4, "dosage_form       ", before, len(df))

    # Step 5 — approval_type
    before = len(df)
    df = df[df["_approval_n"].isin(KEEP_APPROVAL_TYPES)]
    log(5, "approval_type     ", before, len(df))

    # Step 6 — mouthwash-by-name slip
    before = len(df)
    mw_mask = df["_drugname_n"].str.contains(MOUTHWASH_NAME_PATTERN, regex=True, na=False)
    df = df[~mw_mask]
    log(6, "mouthwash slip    ", before, len(df))

    # Drop helper columns and write
    df = df.drop(columns=["_doctype_n", "_route_n", "_dosage_n", "_approval_n", "_drugname_n"])

    final = len(df)
    print(f"\nFinal: {initial:,} → {final:,} rows "
          f"(dropped {initial - final:,}, {(initial - final) / initial * 100:.2f}%)")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV.relative_to(BASE_DIR)} ({final:,} rows × {len(df.columns)} columns)")


if __name__ == "__main__":
    main()
