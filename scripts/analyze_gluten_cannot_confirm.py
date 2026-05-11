#!/usr/bin/env python3
"""
analyze_gluten_cannot_confirm.py — Compute the combined "cannot confirm
gluten-free from the label alone" rate per slice, for use as journalism
citations.

The combined rate counts a product as "cannot confirm" if its gluten_flag is
contains_gluten OR unknown OR no_data. Existing findings docs report each
of these separately and exclude no_data from the denominator. The article
needs the bundled rate against the full denominator. This script is the
deterministic source for those bundled numbers.

Slices reported:
  1. All products
  2. By document_type (OTC vs Rx)
  3. By brand_generic (brand / generic / OTC monograph)
  4. Top 15 active ingredients by row count
  5. Confirmed-gluten product enumeration (sanity check)

Reads data/fullcatalog/gluten_fullcatalog_flagged.csv (72,358 rows). Prints to
stdout. Re-running produces byte-identical output. No AI inference.

Run:
  python3 scripts/analyze_gluten_cannot_confirm.py
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
INPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "gluten_fullcatalog_flagged.csv"

CANNOT_CONFIRM_FLAGS = {"contains_gluten", "unknown", "no_data"}


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
    cc = cg + un + nd
    return n, cg, un, nd, cc


def print_row(label, n, cg, un, nd, cc):
    print(
        f"  {label:<40} "
        f"n={fmt_int(n):>8}  "
        f"contains={fmt_int(cg):>4}  "
        f"unknown={fmt_int(un):>5}  "
        f"no_data={fmt_int(nd):>5}  "
        f"cannot_confirm={fmt_int(cc):>5}  "
        f"({fmt_pct(cc, n)})"
    )


def brand_generic_bucket(value):
    """Map raw brand_generic field to journalism-facing bucket."""
    if value in ("brand",):
        return "brand (NDA)"
    if value in ("generic",):
        return "generic (ANDA + NDA AG)"
    if value in ("otc_monograph",):
        return "OTC monograph"
    return f"other ({value})"


def main():
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)

    print("=" * 100)
    print("Gluten 'cannot confirm from label alone' rate")
    print(f"Source: {INPUT_CSV.relative_to(BASE_DIR)}")
    print("Definition: gluten_flag in {contains_gluten, unknown, no_data}")
    print("=" * 100)

    # Sanity: all flag values present
    flag_counts = df["gluten_flag"].value_counts().to_dict()
    print("\nFlag distribution (raw):")
    for k in ("gluten_free", "unknown", "contains_gluten", "no_data"):
        print(f"  {k:<20} {fmt_int(flag_counts.get(k, 0))}")
    print(f"  {'TOTAL':<20} {fmt_int(len(df))}")

    # 1. Headline
    print("\n" + "-" * 100)
    print("1. ALL PRODUCTS")
    print("-" * 100)
    n, cg, un, nd, cc = slice_counts(df)
    print_row("All products", n, cg, un, nd, cc)

    # 2. By document_type (OTC vs Rx)
    print("\n" + "-" * 100)
    print("2. BY DOCUMENT TYPE (OTC vs Rx)")
    print("-" * 100)
    # Group prescription label variants together
    def doc_bucket(dt):
        dt = dt or ""
        if dt.upper().startswith("HUMAN OTC"):
            return "OTC"
        if dt.upper().startswith("HUMAN PRESCRIPTION"):
            return "Rx"
        if dt.upper().startswith("HUMAN COMPOUNDED"):
            return "compounded"
        return f"other ({dt})"

    df["_doc_bucket"] = df["document_type"].apply(doc_bucket)
    for label in ("OTC", "Rx", "compounded"):
        sub = df[df["_doc_bucket"] == label]
        if len(sub) == 0:
            continue
        n, cg, un, nd, cc = slice_counts(sub)
        print_row(label, n, cg, un, nd, cc)
    other_mask = ~df["_doc_bucket"].isin(["OTC", "Rx", "compounded"])
    if other_mask.any():
        sub = df[other_mask]
        n, cg, un, nd, cc = slice_counts(sub)
        print_row("other", n, cg, un, nd, cc)

    # 3. By brand_generic
    print("\n" + "-" * 100)
    print("3. BY BRAND / GENERIC / OTC MONOGRAPH (brand_generic field)")
    print("-" * 100)
    df["_bg_bucket"] = df["brand_generic"].apply(brand_generic_bucket)
    for bucket in ("brand (NDA)", "generic (ANDA + NDA AG)", "OTC monograph"):
        sub = df[df["_bg_bucket"] == bucket]
        if len(sub) == 0:
            continue
        n, cg, un, nd, cc = slice_counts(sub)
        print_row(bucket, n, cg, un, nd, cc)
    other_bg = df[~df["_bg_bucket"].isin(
        ["brand (NDA)", "generic (ANDA + NDA AG)", "OTC monograph"]
    )]
    if len(other_bg) > 0:
        # Break out the "other" categories so the user can see them
        for bucket, sub in other_bg.groupby("_bg_bucket"):
            n, cg, un, nd, cc = slice_counts(sub)
            print_row(bucket, n, cg, un, nd, cc)

    # 4. Top 15 active ingredients
    print("\n" + "-" * 100)
    print("4. TOP 25 ACTIVE INGREDIENTS BY ROW COUNT")
    print("-" * 100)
    print("  (active_ingredients string as written on label; combos appear as")
    print("   semicolon-joined strings; empty string = KIT or no active listed)")
    print()
    counts_by_active = df["active_ingredients"].value_counts().head(25)
    for active, count in counts_by_active.items():
        sub = df[df["active_ingredients"] == active]
        n, cg, un, nd, cc = slice_counts(sub)
        label = (active or "(empty)")[:38]
        print_row(label, n, cg, un, nd, cc)

    # 5. Confirmed-gluten products (sanity check)
    print("\n" + "-" * 100)
    print("5. CONFIRMED-GLUTEN PRODUCTS (gluten_flag == contains_gluten)")
    print("-" * 100)
    cg_df = df[df["gluten_flag"] == "contains_gluten"][
        ["drug_name", "ndc_code", "dosage_form", "active_ingredients",
         "flagged_excipients"]
    ]
    print(f"  Total: {len(cg_df)} products\n")
    for _, row in cg_df.iterrows():
        print(f"  {row['drug_name']:<55} "
              f"{row['ndc_code']:<14} "
              f"{row['dosage_form']:<24} "
              f"flagged={row['flagged_excipients']}")

    # 6. Cross-check: confirm sums
    print("\n" + "-" * 100)
    print("SANITY CHECKS")
    print("-" * 100)
    n_total, cg_total, un_total, nd_total, cc_total = slice_counts(df)
    expected_cc = 12 + 1028 + 3041
    print(f"  cannot_confirm count: {cc_total} (expected {expected_cc} from "
          f"findings § 2)")
    otc_n = (df["_doc_bucket"] == "OTC").sum()
    rx_n = (df["_doc_bucket"] == "Rx").sum()
    print(f"  OTC + Rx + other = {otc_n + rx_n + (n_total - otc_n - rx_n)} "
          f"(expected {n_total})")


if __name__ == "__main__":
    main()
