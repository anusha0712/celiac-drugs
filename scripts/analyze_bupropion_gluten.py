#!/usr/bin/env python3
"""
analyze_bupropion_gluten.py — Slice the gluten-flagged catalog to the
bupropion family (Wellbutrin and its brand/generic siblings) and report
flag distribution, brand/generic split, and the no_data rows.

Reads data/fullcatalog/gluten_fullcatalog_flagged.csv. Prints to stdout.
Re-running produces byte-identical output. No AI inference.

Run:
  python3 scripts/analyze_bupropion_gluten.py
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
INPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "gluten_fullcatalog_flagged.csv"


def fmt_int(n):
    return f"{int(n):,}"


def fmt_pct(num, denom, decimals=2):
    if denom == 0:
        return "—"
    return f"{num / denom * 100:.{decimals}f}%"


def slice_counts(subset):
    n = len(subset)
    counts = subset["gluten_flag"].value_counts()
    cg = int(counts.get("contains_gluten", 0))
    un = int(counts.get("unknown", 0))
    nd = int(counts.get("no_data", 0))
    gf = int(counts.get("gluten_free", 0))
    cc = cg + un + nd
    return n, gf, un, cg, nd, cc


def report_cohort(label, sub):
    n, gf, un, cg, nd, cc = slice_counts(sub)
    print(f"\n{label}")
    print("-" * len(label))
    print(f"  Total rows:         {fmt_int(n)}")
    print(f"  gluten_free:        {fmt_int(gf)}  ({fmt_pct(gf, n)})")
    print(f"  unknown:            {fmt_int(un)}  ({fmt_pct(un, n)})")
    print(f"  contains_gluten:    {fmt_int(cg)}  ({fmt_pct(cg, n)})")
    print(f"  no_data:            {fmt_int(nd)}  ({fmt_pct(nd, n)})")
    print(f"  cannot_confirm:     {fmt_int(cc)}  ({fmt_pct(cc, n)})")

    print("\n  Brand/generic split:")
    bg_counts = sub["brand_generic"].value_counts()
    for bg, cnt in bg_counts.items():
        print(f"    {bg:<25} {fmt_int(cnt)}")

    print("\n  Approval type:")
    at_counts = sub["approval_type"].value_counts()
    for at, cnt in at_counts.items():
        print(f"    {at:<35} {fmt_int(cnt)}")


def main():
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)

    family_mask = df["active_ingredients"].str.upper().str.contains(
        "BUPROPION", na=False
    )
    family = df[family_mask].copy()

    # Combos = active_ingredients string contains a semicolon
    combo_mask = family["active_ingredients"].str.contains(";", na=False)
    combos = family[combo_mask]
    only = family[~combo_mask]

    print("=" * 80)
    print("Bupropion family — gluten-flag analysis")
    print(f"Source: {INPUT_CSV.relative_to(BASE_DIR)}")
    print(f"Family-mask: active_ingredients contains 'BUPROPION' (uppercased)")
    print("=" * 80)

    print(f"\nFamily total:  {fmt_int(len(family))} rows")
    print(f"  Bupropion-only:    {fmt_int(len(only))} rows "
          f"(Wellbutrin / Aplenzin / Zyban / Forfivo / generic bupropion)")
    print(f"  Bupropion combos:  {fmt_int(len(combos))} rows "
          f"(Contrave, Auvelity)")

    print("\nUnique active_ingredients strings in the family:")
    for s, c in family["active_ingredients"].value_counts().items():
        print(f"  {fmt_int(c):>4}  {s}")

    report_cohort("COHORT 1 — Bupropion-only (Wellbutrin-class)", only)
    report_cohort("COHORT 2 — Bupropion-containing combos (Contrave / Auvelity)", combos)

    # No_data drill-down across the whole family
    nd_rows = family[family["gluten_flag"] == "no_data"]
    print("\n" + "=" * 80)
    print(f"NO_DATA ROWS IN BUPROPION FAMILY — {len(nd_rows)} total")
    print("=" * 80)
    if len(nd_rows) > 0:
        cols = ["drug_name", "manufacturer", "dosage_form", "ndc_code",
                "brand_generic", "approval_type", "marketing_status"]
        for _, row in nd_rows.iterrows():
            print()
            for col in cols:
                if col in row.index:
                    print(f"  {col:<22} {row[col]}")

    # Top brand-named products (sanity)
    print("\n" + "=" * 80)
    print("BRAND-NAMED PRODUCTS IN THE FAMILY")
    print("=" * 80)
    brands = family[family["brand_generic"] == "brand"][
        ["drug_name", "manufacturer", "dosage_form", "ndc_code", "approval_type",
         "gluten_flag"]
    ]
    name_counts = brands["drug_name"].value_counts()
    for name, cnt in name_counts.items():
        print(f"  {fmt_int(cnt):>3}  {name}")

    # Verification
    print("\n" + "=" * 80)
    print("SANITY CHECKS")
    print("=" * 80)
    print(f"  family total:         {len(family)}  (expected 511)")
    print(f"  bupropion-only total: {len(only)}    (expected 502)")
    print(f"  combos total:         {len(combos)}      (expected 9)")
    print(f"  no_data in family:    {len(nd_rows)}      (expected 5)")


if __name__ == "__main__":
    main()
