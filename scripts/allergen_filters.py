#!/usr/bin/env python3
"""
allergen_filters.py — shared filter constants and helpers.

Single source of truth for:
- Excipient-string delimiter (used by every flagger / corpus-test
  generator that splits a product's `excipients_raw` field).
- Dosage-form and route keywords used across
  analyze_allergens_fullcatalog.py, analyze_dpi_labels.py,
  analyze_carmine_labels.py, analyze_peg_labels.py.
"""

# ============================================================
# Excipient-string delimiter
# ============================================================
# DailyMed `excipients_raw` field uses "; " (semicolon-space) as the
# token separator. Verified 2026-04-23 against all 199,961 catalog
# rows: every `;` is followed by exactly one space (zero non-standard
# delimiters). Hardcoded `"; "` was previously duplicated in 5+ files;
# now imported from here.
EXCIPIENT_DELIMITER = "; "

# ============================================================
# DPI identification (milk / CMPA harm anchor)
# ============================================================
# Dry Powder Inhalers only. Excludes pMDIs (AEROSOL, METERED) which are
# propellant-based and do not use lactose carriers — they are not the
# CMPA-related harm category.

DPI_DOSAGE_KEYWORDS = (
    "POWDER, METERED",
    "INHALANT, METERED",
)
DPI_ROUTE_KEYWORDS = (
    "RESPIRATORY",
    "INHAL",
)


def is_dpi(dosage_form: str, route: str) -> bool:
    df = (dosage_form or "").upper()
    r = (route or "").upper()
    return (any(k in df for k in DPI_DOSAGE_KEYWORDS)
            and any(k in r for k in DPI_ROUTE_KEYWORDS))


# ============================================================
# Oral-solids slice (PEG headline slice; matches gluten filter)
# ============================================================
ORAL_SOLID_INCLUDE = ("TABLET", "CAPSULE", "GRANULE", "PELLET")
ORAL_SOLID_EXCLUDE = ("ORALLY DISINTEGRATING",)


def is_oral_solid(dosage_form: str) -> bool:
    df = (dosage_form or "").upper()
    if not any(k in df for k in ORAL_SOLID_INCLUDE):
        return False
    if any(x in df for x in ORAL_SOLID_EXCLUDE):
        return False
    return True


# ============================================================
# Oral route
# ============================================================
def is_oral(route: str) -> bool:
    return (route or "").upper() == "ORAL"


# ============================================================
# Baseline allergens filter (Task #28, 2026-04-23)
# ============================================================
# Removes homeopathic, unapproved, and non-drug rows from the raw
# catalog before allergen flagging. Mirrors steps 1, 2, 5 of
# `filter_gluten_fullcatalog.py` (with no route restriction so DPI
# milk and other non-oral harm anchors remain in scope).
#
# Pollution measured 2026-04-23 against allergens_fullcatalog_flagged.csv:
#   contains_milk:    4,436 homeopathic + 4,905 unapproved-etc = ~25%
#   contains_peg:     48 homeopathic + 588 unapproved-etc = ~2%
#   contains_carmine: 2 homeopathic + 15 unapproved-etc = ~10%
# Without this filter, milk numbers in particular were overstated.

BASELINE_ALLOWED_DOCUMENT_TYPES = {
    "HUMAN OTC DRUG LABEL",
    "HUMAN PRESCRIPTION DRUG LABEL",
    "HUMAN PRESCRIPTION DRUG LABEL WITH HIGHLIGHTS",
    "HUMAN COMPOUNDED DRUG LABEL",
}

BASELINE_ALLOWED_APPROVAL_TYPES = {
    # FDA-approved drug categories. Case-normalized to uppercase.
    "ANDA",
    "NDA",
    "NDA AUTHORIZED GENERIC",
    "BLA",
    "OTC MONOGRAPH DRUG",
    "OTC MONOGRAPH FINAL",
    "OTC MONOGRAPH NOT FINAL",
}

BASELINE_DISALLOWED_BULK_CATEGORIES = {
    "homeopathic",
    "other",  # vaccines, devices, bulk ingredients, supplements, etc.
}


def passes_baseline(row: dict) -> bool:
    """Return True if the row is a real FDA-recognized human medication.

    Excludes homeopathic, unapproved drugs, dietary supplements, animal
    products, vaccines, medical devices, bulk ingredients, allergenics,
    cosmetics, plasma derivatives, cellular/gene therapies, etc.

    Designed for the allergens-pipeline baseline (Task #28). Rows
    failing this filter would pollute milk/PEG/carmine prevalence
    counts with non-medication rows.
    """
    bc = (row.get("bulk_category") or "").strip().lower()
    if bc in BASELINE_DISALLOWED_BULK_CATEGORIES:
        return False
    dt = (row.get("document_type") or "").strip().upper()
    if dt not in BASELINE_ALLOWED_DOCUMENT_TYPES:
        return False
    at = (row.get("approval_type") or "").strip().upper()
    if at not in BASELINE_ALLOWED_APPROVAL_TYPES:
        return False
    return True
