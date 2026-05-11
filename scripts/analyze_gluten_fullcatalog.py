#!/usr/bin/env python3
"""
analyze_gluten_fullcatalog.py — Generate analysis/allergens/gluten/findings_fullcatalog_gluten.md
from the flagged full-catalog dataset.

Reads data/fullcatalog/gluten_fullcatalog_flagged.csv (72,358 rows) and writes
analysis/allergens/gluten/findings_fullcatalog_gluten.md in one deterministic
pass. Every table in the findings document is computed from the same
in-memory dataframe. No hand transcription. Rerunning this script produces
a byte-identical file.

The document contains only objective data sections (no interpretation).
Per the methodology statement locked 2026-04-10, all findings are reported
without editorializing. Interpretation is deferred to the journalist.

Run:
  python3 scripts/analyze_gluten_fullcatalog.py
"""

import sys
from pathlib import Path
from datetime import date

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from allergen_filters import EXCIPIENT_DELIMITER

BASE_DIR = Path(__file__).parent.parent
INPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "gluten_fullcatalog_flagged.csv"
OUTPUT_MD = (BASE_DIR / "analysis" / "allergens" / "gluten"
             / "findings_fullcatalog_gluten.md")

FLAG_ORDER = ["contains_gluten", "unknown", "gluten_free", "no_data"]


# ============================================================
# Formatting helpers
# ============================================================

def fmt_int(n):
    return f"{int(n):,}"


def fmt_pct(num, denom, decimals=2):
    if denom == 0:
        return "—"
    return f"{num / denom * 100:.{decimals}f}%"


def md_table(headers, rows, align=None):
    """Render a markdown table. `align` is a list of 'l', 'c', or 'r' per column."""
    if align is None:
        align = ["l"] * len(headers)
    sep_map = {"l": ":---", "c": ":---:", "r": "---:"}
    sep = [sep_map[a] for a in align]
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join(sep) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def flag_distribution_row(subset, total_label=""):
    """Return (n, gluten_free, unknown, contains_gluten, no_data) counts for a subset."""
    n = len(subset)
    counts = subset["gluten_flag"].value_counts()
    gf = int(counts.get("gluten_free", 0))
    un = int(counts.get("unknown", 0))
    cg = int(counts.get("contains_gluten", 0))
    nd = int(counts.get("no_data", 0))
    return n, gf, un, cg, nd


def flag_percentages_no_data_excluded(n, gf, un, cg, nd):
    """Compute percentages with no_data excluded from the denominator."""
    denom = n - nd
    return (
        fmt_pct(gf, denom),
        fmt_pct(un, denom),
        fmt_pct(cg, denom),
        fmt_pct(nd, n),  # no_data % is of total, not of with-data
    )


# ============================================================
# Data loading
# ============================================================

def load_data():
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    # Normalized helper columns for grouping (not for display)
    df["_dosage_n"] = df["dosage_form"].str.upper().str.strip()
    df["_approval_n"] = df["approval_type"].str.upper().str.strip()
    df["_ai_n"] = df["active_ingredients"].str.upper().str.strip()
    df["_mfr_n"] = df["manufacturer"].str.strip()
    df["_dt_n"] = df["document_type"].str.upper().str.strip()
    return df


# ============================================================
# Section generators
# ============================================================

def section_header():
    today = date.today().isoformat()
    return f"""# Bulk Catalog Findings: Gluten Labeling Transparency in FDA-Recognized Oral Medications

*Analysis date: {today}*
*Data source: DailyMed bulk download (April 6, 2026), filtered per CLAUDE.md "Bulk Filtering Decisions (2026-04-10)"*
*Scope: FDA-recognized human medications directly delivered to the GI tract by swallowing*
*Input file: `data/fullcatalog/gluten_fullcatalog_flagged.csv` (72,358 rows)*

This document reports objective data cuts on the bulk dataset. It contains no
interpretation. Methodology is documented in CLAUDE.md; limitations are
documented in `analysis/allergens/limitations.md` §Gluten.

**Denominator convention:** All percentages reported in the breakdown sections
exclude `no_data` products from the denominator unless a column header
explicitly says otherwise. The `no_data %` column, where shown, is computed
against the full subset total.
"""


def section_executive_summary(df):
    n, gf, un, cg, nd = flag_distribution_row(df)

    # Top excipient driving unknown
    unk_df = df[df["gluten_flag"] == "unknown"]
    top_unk_excip = (
        unk_df["flagged_excipients"]
        .value_counts()
        .head(1)
    )
    top_unk_excip_str = top_unk_excip.index[0] if len(top_unk_excip) > 0 else "—"
    top_unk_count = int(top_unk_excip.iloc[0]) if len(top_unk_excip) > 0 else 0

    # KIT share of no_data
    nd_df = df[df["gluten_flag"] == "no_data"]
    kit_nd = (nd_df["_dosage_n"] == "KIT").sum()
    kit_share = fmt_pct(kit_nd, nd) if nd > 0 else "—"

    # OTC vs Rx uncertainty (no_data excluded)
    otc = df[df["_dt_n"] == "HUMAN OTC DRUG LABEL"]
    rx = df[df["_dt_n"] == "HUMAN PRESCRIPTION DRUG LABEL"]
    otc_n, _, otc_un, otc_cg, otc_nd = flag_distribution_row(otc)
    rx_n, _, rx_un, rx_cg, rx_nd = flag_distribution_row(rx)
    otc_uncertain = fmt_pct(otc_un + otc_cg, otc_n - otc_nd)
    rx_uncertain = fmt_pct(rx_un + rx_cg, rx_n - rx_nd)

    return f"""## Executive Summary

- **Dataset:** {fmt_int(n)} FDA-recognized swallowed human medications
- **Confirmed gluten grain on label:** {fmt_int(cg)} products ({fmt_pct(cg, n - nd)} of products with data)
- **Cannot be determined safe from label alone (`unknown`):** {fmt_int(un)} products ({fmt_pct(un, n - nd)} of products with data)
- **Confirmed gluten-free from label:** {fmt_int(gf)} products ({fmt_pct(gf, n - nd)} of products with data)
- **No excipient data on label (`no_data`):** {fmt_int(nd)} products ({fmt_pct(nd, n)} of total)
- **Share of `no_data` that is KIT packages:** {kit_share} ({fmt_int(kit_nd)} of {fmt_int(nd)})
- **Top excipient driving `unknown`:** `{top_unk_excip_str}` — {fmt_int(top_unk_count)} products
- **Uncertainty rate (no_data excluded):** OTC {otc_uncertain} vs Rx {rx_uncertain}
"""


def section_scope(df):
    n = len(df)
    otc = (df["_dt_n"] == "HUMAN OTC DRUG LABEL").sum()
    rx = (df["_dt_n"] == "HUMAN PRESCRIPTION DRUG LABEL").sum()
    rx_hl = (df["_dt_n"] == "HUMAN PRESCRIPTION DRUG LABEL WITH HIGHLIGHTS").sum()
    compounded = (df["_dt_n"] == "HUMAN COMPOUNDED DRUG LABEL").sum()

    generic = (df["brand_generic"] == "generic").sum()
    brand = (df["brand_generic"] == "brand").sum()
    otc_mono = (df["brand_generic"] == "otc_monograph").sum()

    single = (df["single_or_combo"] == "single").sum()
    combo = (df["single_or_combo"] == "combo").sum()

    dea = (df["dea_schedule"] != "").sum()
    non_dea = (df["dea_schedule"] == "").sum()

    nd = (df["gluten_flag"] == "no_data").sum()
    with_data = n - nd

    rows = [
        ("Total products", fmt_int(n)),
        ("Products with excipient data", f"{fmt_int(with_data)} ({fmt_pct(with_data, n)})"),
        ("Products without excipient data (`no_data`)", f"{fmt_int(nd)} ({fmt_pct(nd, n)})"),
        ("", ""),
        ("OTC drug labels", fmt_int(otc)),
        ("Prescription drug labels", fmt_int(rx)),
        ("Prescription drug labels with highlights", fmt_int(rx_hl)),
        ("Human compounded drug labels", fmt_int(compounded)),
        ("", ""),
        ("Brand (NDA / BLA)", fmt_int(brand)),
        ("Generic (ANDA / NDA authorized generic)", fmt_int(generic)),
        ("OTC monograph", fmt_int(otc_mono)),
        ("", ""),
        ("Single-ingredient products", fmt_int(single)),
        ("Combination products", fmt_int(combo)),
        ("", ""),
        ("DEA controlled substances", fmt_int(dea)),
        ("Non-controlled", fmt_int(non_dea)),
    ]

    body = md_table(["Metric", "Count"], rows, align=["l", "r"])
    return f"""## 1. Scope and Dataset Composition

{body}

Unit of analysis: NDC-level. The bulk extraction produces one row per
`<manufacturedProduct>` block in the SPL XML, so a single SPL label can
contribute multiple rows when different NDCs carry different dosage forms
or excipient profiles.

Full filter pipeline: CLAUDE.md § "Bulk Filtering Decisions (2026-04-10)".
Full limitations: `analysis/allergens/limitations.md` §Gluten.
"""


def section_headline_results(df):
    n, gf, un, cg, nd = flag_distribution_row(df)
    denom_with_data = n - nd

    rows = [
        ("`gluten_free`", fmt_int(gf), fmt_pct(gf, n), fmt_pct(gf, denom_with_data)),
        ("`unknown`", fmt_int(un), fmt_pct(un, n), fmt_pct(un, denom_with_data)),
        ("`contains_gluten`", fmt_int(cg), fmt_pct(cg, n), fmt_pct(cg, denom_with_data)),
        ("`no_data`", fmt_int(nd), fmt_pct(nd, n), "—"),
        ("**Total**", f"**{fmt_int(n)}**", "**100.00%**", f"**n = {fmt_int(denom_with_data)}**"),
    ]

    body = md_table(
        ["Flag", "Count", "% of all products", "% of products with data"],
        rows,
        align=["l", "r", "r", "r"],
    )
    return f"""## 2. Headline Results — All Products

{body}
"""


def section_contains_gluten(df):
    cg = df[df["gluten_flag"] == "contains_gluten"].copy()
    cg_sorted = cg.sort_values(["manufacturer", "drug_name"])
    rows = []
    for _, r in cg_sorted.iterrows():
        rows.append((
            r["drug_name"][:60],
            r["manufacturer"][:50],
            r["dosage_form"][:30],
            r["ndc_code"],
            r["flagged_excipients"][:60],
        ))

    if not rows:
        body = "No products in the dataset were flagged `contains_gluten`."
    else:
        body = md_table(
            ["Drug name", "Manufacturer", "Dosage form", "NDC", "Flagged excipient(s)"],
            rows,
            align=["l", "l", "l", "l", "l"],
        )

    return f"""## 3. Confirmed Gluten Products

The following {len(cg)} products explicitly list a confirmed gluten grain
(wheat, barley, or rye, or an identified derivative thereof) on their DailyMed
label. "Confirmed" here means the label string names the grain; it does not
mean the product has been tested for gluten protein content. See
`analysis/allergens/limitations.md` §Gluten on the label-only methodology.

{body}
"""


def _subgroup_flag_row(label, subset):
    n, gf, un, cg, nd = flag_distribution_row(subset)
    denom = n - nd
    return (
        label,
        fmt_int(n),
        fmt_pct(gf, denom),
        fmt_pct(un, denom),
        fmt_pct(cg, denom),
        fmt_pct(nd, n),
    )


def section_breakdowns(df):
    # 4.1 By regulatory category
    subgroups_41 = [
        ("OTC drug label (document_type)", df[df["_dt_n"] == "HUMAN OTC DRUG LABEL"]),
        ("Prescription drug label (document_type)", df[df["_dt_n"] == "HUMAN PRESCRIPTION DRUG LABEL"]),
        ("ANDA (generic Rx)", df[df["_approval_n"] == "ANDA"]),
        ("NDA (brand Rx)", df[df["_approval_n"] == "NDA"]),
        ("NDA authorized generic", df[df["_approval_n"] == "NDA AUTHORIZED GENERIC"]),
        ("OTC monograph (all variants)", df[df["_approval_n"].str.startswith("OTC MONOGRAPH")]),
        ("BLA (biologic)", df[df["_approval_n"] == "BLA"]),
    ]
    rows_41 = [_subgroup_flag_row(label, sub) for label, sub in subgroups_41 if len(sub) > 0]
    table_41 = md_table(
        ["Category", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_41,
        align=["l", "r", "r", "r", "r", "r"],
    )

    # 4.2 By dosage form (top 20 by row count)
    top_forms = df["_dosage_n"].value_counts().head(20).index.tolist()
    rows_42 = []
    for form in top_forms:
        sub = df[df["_dosage_n"] == form]
        rows_42.append(_subgroup_flag_row(form.title(), sub))
    table_42 = md_table(
        ["Dosage form", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_42,
        align=["l", "r", "r", "r", "r", "r"],
    )

    # 4.3 Single vs combination
    rows_43 = [
        _subgroup_flag_row("Single-ingredient", df[df["single_or_combo"] == "single"]),
        _subgroup_flag_row("Combination", df[df["single_or_combo"] == "combo"]),
    ]
    table_43 = md_table(
        ["Product type", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_43,
        align=["l", "r", "r", "r", "r", "r"],
    )

    # 4.4 DEA schedule
    rows_44 = [
        _subgroup_flag_row("Non-controlled", df[df["dea_schedule"] == ""]),
        _subgroup_flag_row("Schedule II", df[df["dea_schedule"] == "CII"]),
        _subgroup_flag_row("Schedule III", df[df["dea_schedule"] == "CIII"]),
        _subgroup_flag_row("Schedule IV", df[df["dea_schedule"] == "CIV"]),
        _subgroup_flag_row("Schedule V", df[df["dea_schedule"] == "CV"]),
    ]
    rows_44 = [r for r in rows_44 if r[1] != "0"]
    table_44 = md_table(
        ["DEA schedule", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_44,
        align=["l", "r", "r", "r", "r", "r"],
    )

    # 4.5 Top 20 active ingredient strings
    top_ai = df["_ai_n"].value_counts().head(20).index.tolist()
    rows_45 = []
    for ai in top_ai:
        sub = df[df["_ai_n"] == ai]
        # Shorten for display
        display = ai if len(ai) <= 60 else ai[:57] + "..."
        rows_45.append(_subgroup_flag_row(display, sub))
    table_45 = md_table(
        ["Active ingredient(s)", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_45,
        align=["l", "r", "r", "r", "r", "r"],
    )

    # 4.6 Top 20 manufacturers by row count
    top_mfr = df["_mfr_n"].value_counts().head(20).index.tolist()
    rows_46 = []
    for mfr in top_mfr:
        sub = df[df["_mfr_n"] == mfr]
        display = mfr if len(mfr) <= 55 else mfr[:52] + "..."
        rows_46.append(_subgroup_flag_row(display, sub))
    table_46 = md_table(
        ["Manufacturer", "n", "gluten_free %", "unknown %", "contains_gluten %", "no_data %"],
        rows_46,
        align=["l", "r", "r", "r", "r", "r"],
    )

    return f"""## 4. Breakdowns

All percentages in this section exclude `no_data` from the flag denominator.
The `no_data %` column is computed against the subgroup total.

### 4.1 By Regulatory Category

{table_41}

### 4.2 By Dosage Form (Top 20 by Row Count)

{table_42}

Dosage forms outside the top 20 are omitted from the table but are included
in all section-level totals and in Section 2.

### 4.3 Single-Ingredient vs Combination

{table_43}

### 4.4 By DEA Schedule

{table_44}

### 4.5 By Active Ingredient String (Top 20 by Row Count)

{table_45}

Active ingredient strings are grouped as written on the label (semicolon-
separated for combination products). This does not consolidate salt forms
or different orderings of the same components.

### 4.6 By Manufacturer (Top 20 by Row Count)

{table_46}

Manufacturer names are grouped as written in the SPL label. Variant spellings
("Acme, Inc." vs "Acme Inc." vs "ACME INC.") appear as separate rows.
"""


def section_sources_of_uncertainty(df):
    unk = df[df["gluten_flag"] == "unknown"].copy()
    total_unk = len(unk)
    total_products = len(df)

    # Explode flagged_excipients into rows (one row per excipient)
    unk["excipient_list"] = unk["flagged_excipients"].str.split(EXCIPIENT_DELIMITER)
    exploded = unk.explode("excipient_list")
    exploded["excipient_list"] = exploded["excipient_list"].str.strip()
    exploded = exploded[exploded["excipient_list"] != ""]

    # Count unique product-excipient pairs — but since a product only appears
    # in unknown if at least one unknown excipient is present, and the product
    # is flagged once, we count product appearances per flagging excipient.
    excip_counts = exploded.groupby("excipient_list").agg(
        products=("ndc_code", "count"),
    ).sort_values("products", ascending=False)

    rows_51 = []
    for excip, row in excip_counts.iterrows():
        n_products = int(row["products"])
        rows_51.append((
            f"`{excip}`",
            fmt_int(n_products),
            fmt_pct(n_products, total_unk),
            fmt_pct(n_products, total_products),
        ))

    table_51 = md_table(
        ["Excipient string", "Products flagged", "% of unknown products", "% of all products"],
        rows_51,
        align=["l", "r", "r", "r"],
    )

    # 5.2 Source-specified vs unspecified for the top three
    # Count direct excipient strings in the full dataset
    all_excipients = df["excipients_raw"].str.split(EXCIPIENT_DELIMITER).explode()
    all_excipients = all_excipients.str.strip().str.upper()
    all_excipients_counts = all_excipients.value_counts()

    def count_containing(substring):
        mask = all_excipients.str.contains(substring, regex=False, na=False)
        return int(mask.sum())

    def count_exact(s):
        return int(all_excipients_counts.get(s.upper(), 0))

    rows_52 = []
    # SSG Type A
    ssg_a_total = count_containing("SODIUM STARCH GLYCOLATE TYPE A")
    ssg_a_unspec = count_exact("SODIUM STARCH GLYCOLATE TYPE A")
    ssg_a_spec = ssg_a_total - ssg_a_unspec
    if ssg_a_total > 0:
        rows_52.append((
            "`SODIUM STARCH GLYCOLATE TYPE A`",
            fmt_int(ssg_a_total),
            fmt_int(ssg_a_spec),
            fmt_int(ssg_a_unspec),
            fmt_pct(ssg_a_unspec, ssg_a_total),
        ))

    # Pregelatinized starch
    preg_total = count_containing("PREGELATINIZED STARCH") + count_containing("STARCH, PREGELATINIZED")
    preg_unspec = count_exact("PREGELATINIZED STARCH")
    preg_spec = preg_total - preg_unspec
    if preg_total > 0:
        rows_52.append((
            "`PREGELATINIZED STARCH`",
            fmt_int(preg_total),
            fmt_int(preg_spec),
            fmt_int(preg_unspec),
            fmt_pct(preg_unspec, preg_total),
        ))

    # Plain STARCH
    starch_exact = count_exact("STARCH")
    starch_corn = count_exact("STARCH, CORN") + count_exact("CORN STARCH")
    starch_potato = count_exact("STARCH, POTATO") + count_exact("POTATO STARCH")
    starch_tapioca = count_exact("STARCH, TAPIOCA") + count_exact("TAPIOCA STARCH")
    starch_wheat = count_exact("STARCH, WHEAT") + count_exact("WHEAT STARCH")
    starch_rice = count_exact("STARCH, RICE") + count_exact("RICE STARCH")
    starch_total = (
        starch_exact + starch_corn + starch_potato + starch_tapioca
        + starch_wheat + starch_rice
    )
    starch_spec = starch_total - starch_exact
    if starch_total > 0:
        rows_52.append((
            "`STARCH` (any source or unspecified)",
            fmt_int(starch_total),
            fmt_int(starch_spec),
            fmt_int(starch_exact),
            fmt_pct(starch_exact, starch_total),
        ))

    table_52 = md_table(
        ["Excipient family", "Total uses", "Source-specified", "Source-unspecified", "% unspecified"],
        rows_52,
        align=["l", "r", "r", "r", "r"],
    )

    return f"""## 5. Sources of Uncertainty

### 5.1 Excipients Driving the `unknown` Flag

Every product flagged `unknown` has at least one excipient whose gluten
status cannot be determined from the label (typically a starch derivative
with no botanical source specified). The breakdown below counts each
product once per flagging excipient — a product flagged for two different
unknown excipients is counted in both rows.

{table_51}

Denominator for "% of unknown products" is the total number of products
with `unknown` flag ({fmt_int(total_unk)}). Denominator for "% of all
products" is the full dataset ({fmt_int(total_products)}).

### 5.2 Source-Specified vs Source-Unspecified Excipient Use

For the excipient families that drive the `unknown` flag, the table below
counts how often the same excipient family appears with vs without a
specified botanical source across the entire filtered dataset. A high
"% unspecified" value means the excipient is usually declared without a
source grain.

{table_52}
"""


def section_no_data(df):
    nd = df[df["gluten_flag"] == "no_data"]
    total_nd = len(nd)

    # Dosage form composition
    form_counts = nd["_dosage_n"].value_counts()
    rows_61 = []
    cumulative_other = 0
    for i, (form, count) in enumerate(form_counts.items()):
        if i < 15:
            rows_61.append((
                form.title(),
                fmt_int(count),
                fmt_pct(count, total_nd),
            ))
        else:
            cumulative_other += count
    if cumulative_other > 0:
        rows_61.append((
            f"All other forms",
            fmt_int(cumulative_other),
            fmt_pct(cumulative_other, total_nd),
        ))

    table_61 = md_table(
        ["Dosage form", "n", "% of no_data"],
        rows_61,
        align=["l", "r", "r"],
    )

    kit = nd[nd["_dosage_n"] == "KIT"]
    non_kit = nd[nd["_dosage_n"] != "KIT"]

    # Top manufacturers in non-KIT no_data
    mfr_counts = non_kit["_mfr_n"].value_counts().head(10)
    rows_62 = []
    for mfr, count in mfr_counts.items():
        display = mfr if len(mfr) <= 55 else mfr[:52] + "..."
        rows_62.append((display, fmt_int(count)))
    table_62 = md_table(
        ["Manufacturer", "n non-KIT no_data products"],
        rows_62,
        align=["l", "r"],
    )

    return f"""## 6. No-Data Products

{fmt_int(total_nd)} products in the dataset list no inactive ingredients on
their DailyMed label. The composition of this group is shown below.

### 6.1 By Dosage Form

{table_61}

KIT products are multi-component packages. The KIT-level label typically
does not enumerate excipients — the individual product labels inside the
KIT have their own excipient lists. This structural pattern is the reason
KIT appears at {fmt_pct(len(kit), total_nd)} of the no_data bucket. See
`analysis/allergens/limitations.md` §Gluten.

### 6.2 Non-KIT No-Data Manufacturers (Top 10 by Row Count)

{fmt_int(len(non_kit))} non-KIT products have no excipient data on their
label — i.e., the label format does not include an inactive ingredients
section at all.

{table_62}
"""


def section_pilot_comparison(df):
    # Extract rows whose active_ingredients contain ACETAMINOPHEN or IBUPROFEN
    ai_upper = df["active_ingredients"].str.upper()
    has_acet = ai_upper.str.contains("ACETAMINOPHEN", na=False)
    has_ibu = ai_upper.str.contains("IBUPROFEN", na=False)

    acet_sub = df[has_acet]
    ibu_sub = df[has_ibu]

    acet_n, acet_gf, acet_un, acet_cg, acet_nd = flag_distribution_row(acet_sub)
    ibu_n, ibu_gf, ibu_un, ibu_cg, ibu_nd = flag_distribution_row(ibu_sub)

    # Pilot numbers from analysis/allergens/gluten/findings_pilot_gluten.md
    rows = [
        (
            "Acetaminophen-containing",
            "4,986",
            "3.4%",
            fmt_int(acet_n),
            fmt_pct(acet_un + acet_cg, acet_n - acet_nd),
        ),
        (
            "Ibuprofen-containing",
            "1,619",
            "1.0%",
            fmt_int(ibu_n),
            fmt_pct(ibu_un + ibu_cg, ibu_n - ibu_nd),
        ),
    ]

    table = md_table(
        [
            "Subset",
            "Pilot n",
            "Pilot unknown+contains_gluten %",
            "Bulk n",
            "Bulk unknown+contains_gluten %",
        ],
        rows,
        align=["l", "r", "r", "r", "r"],
    )

    return f"""## 7. Pilot Subset Comparison

The pilot dataset (`data/pilot/gluten_pilot_flagged.csv`, 6,605 products) covered
all DailyMed products containing acetaminophen or ibuprofen as an active
ingredient, with only injectables excluded. The bulk dataset applies a
stricter filter pipeline (`scripts/filter_gluten_fullcatalog.py`) that additionally drops
homeopathic, non-FDA-recognized (`unapproved drug other`, `unapproved
homeopathic`, etc.), and non-swallowed dosage forms (lozenges, films,
orally disintegrating tablets, mouthwashes, pastes, etc.).

Row counts differ because of the stricter filters. Percentages differ
because the bulk dataset excludes dosage forms the pilot kept and because
the validation table used for the bulk dataset has 171 entries vs the
pilot's 48.

{table}

Pilot percentages are taken from `analysis/allergens/gluten/findings_pilot_gluten.md` § 4.1 and § 4.2.
All percentages exclude `no_data` from the denominator.
"""


def section_portugal_reference(df):
    # Compute acet and ibu from bulk
    ai_upper = df["active_ingredients"].str.upper()
    acet_sub = df[ai_upper.str.contains("ACETAMINOPHEN", na=False)]
    ibu_sub = df[ai_upper.str.contains("IBUPROFEN", na=False)]

    acet_n, _, acet_un, acet_cg, acet_nd = flag_distribution_row(acet_sub)
    ibu_n, _, ibu_un, ibu_cg, ibu_nd = flag_distribution_row(ibu_sub)

    rows = [
        (
            "Paracetamol/Acetaminophen — % non-gluten-free",
            "44.4%",
            "n=108",
            fmt_pct(acet_un + acet_cg, acet_n - acet_nd),
            f"n={fmt_int(acet_n - acet_nd)}",
        ),
        (
            "Ibuprofen — % non-gluten-free",
            "8.2%",
            "n=85",
            fmt_pct(ibu_un + ibu_cg, ibu_n - ibu_nd),
            f"n={fmt_int(ibu_n - ibu_nd)}",
        ),
        (
            "Products with confirmed gluten grains",
            "0",
            "",
            fmt_int((df["gluten_flag"] == "contains_gluten").sum()),
            f"n={fmt_int(len(df) - (df['gluten_flag'] == 'no_data').sum())}",
        ),
    ]
    table_main = md_table(
        ["Metric", "Portugal", "Portugal n", "US (bulk)", "US n"],
        rows,
        align=["l", "r", "r", "r", "r"],
    )

    diff_rows = [
        ("Sample size", "108 + 85", "See § 7"),
        ("Database", "INFOMED (SmPCs)", "DailyMed (SPL labels)"),
        ("Classification system", "Binary", "Four-tier (gluten_free / unknown / contains_gluten / no_data)"),
        ("Xanthan gum", "Non-gluten-free", "Gluten-free (per NCA)"),
        ("Filter pipeline", "Therapeutic category only", "See CLAUDE.md § Bulk Filtering Decisions"),
        ("Unit of analysis", "Not specified", "NDC"),
    ]
    table_diffs = md_table(
        ["Factor", "Portugal", "US (bulk)"],
        diff_rows,
        align=["l", "l", "l"],
    )

    return f"""## 8. Methodological Reference — Figueiredo et al. (2025)

Figueiredo et al. (2025), "Presence of gluten and soy derived excipients in
medicinal products and their implications on allergen safety and labeling,"
Scientific Reports 15, 10976. https://doi.org/10.1038/s41598-025-95525-6

The Portuguese source study used a binary classification ("gluten-free" vs
"non-gluten-free"). The closest equivalent in this project's four-tier
system is `unknown` + `contains_gluten`. All US percentages below exclude
`no_data` from the denominator.

{table_main}

Methodological differences affecting the comparison:

{table_diffs}
"""


# ============================================================
# Main
# ============================================================

def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: input file not found: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {INPUT_CSV.relative_to(BASE_DIR)}...")
    df = load_data()
    print(f"  Loaded {len(df):,} rows × {len(df.columns)} columns.\n")

    print("Generating sections...")
    parts = [
        section_header(),
        section_executive_summary(df),
        section_scope(df),
        section_headline_results(df),
        section_contains_gluten(df),
        section_breakdowns(df),
        section_sources_of_uncertainty(df),
        section_no_data(df),
        section_pilot_comparison(df),
        section_portugal_reference(df),
    ]

    full_doc = "\n\n".join(parts) + "\n"

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(full_doc)

    print(f"Wrote {OUTPUT_MD.relative_to(BASE_DIR)} ({len(full_doc):,} bytes)")
    print(f"Sections: {len(parts)}")
    print(f"Rows analyzed: {len(df):,}")


if __name__ == "__main__":
    main()
