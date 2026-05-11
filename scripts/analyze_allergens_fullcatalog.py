#!/usr/bin/env python3
"""
analyze_allergens_fullcatalog.py — Compute category-sliced counts for the three allergens.

Reads data/fullcatalog/allergens_fullcatalog_flagged.csv (199,961 rows) and emits
per-allergen prevalence numbers for the findings docs.

Slices:
    milk     — full catalog, all respiratory-route, DPIs (harm anchor,
               pMDIs excluded via allergen_filters.is_dpi), oral route
    peg      — full catalog, oral route, oral solids (TABLET/CAPSULE/
               GRANULE/PELLET, ODT-excluded, via allergen_filters.is_oral_solid),
               oral solutions / powders-for-solution-or-suspension
    carmine  — landscape (no pre-filter) across route, dosage_form,
               approval_type, bulk_category, brand_generic, top active
               ingredients (drug identity only, not allergen matching),
               top manufacturers

Run:
    python3 scripts/analyze_allergens_fullcatalog.py
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from allergen_filters import is_dpi, is_oral, is_oral_solid

BASE = Path(__file__).parent.parent
FLAGGED = BASE / "data" / "fullcatalog" / "allergens_fullcatalog_flagged.csv"
GLUTEN_FILTERED = BASE / "data" / "fullcatalog" / "gluten_fullcatalog_filtered.csv"

# Parenteral routes for Task #29 per-allergen harm-anchor slicing.
# - PEG: PEGylated drugs and contrast agents are the bloodstream
#   anaphylaxis pathway (Stone 2019).
# - Milk: Hatcher 2025 detected trace bovine casein in IV
#   methylprednisolone vials.
PARENTERAL_ROUTES = {"INTRAVENOUS", "INTRAMUSCULAR", "SUBCUTANEOUS",
                     "INTRA-ARTERIAL", "INTRATHECAL", "INTRA-ARTICULAR"}


def pct(n, d):
    if d == 0:
        return "0.00%"
    return f"{n / d * 100:.2f}%"


def is_parenteral(route: str) -> bool:
    return (route or "").upper() in PARENTERAL_ROUTES


def load_gluten_filtered_keys():
    """Return set of (set_id, ndc_code) tuples in the gluten-filtered set.

    Used for the Task #30 gluten-comparable parity stat — counts how
    many allergen-flagged products would also pass the gluten filter
    pipeline (ORAL only, FDA-recognized, swallowed). Returns empty set
    if the gluten-filtered CSV is missing (skip the stat with a note).
    """
    if not GLUTEN_FILTERED.exists():
        return None
    keys = set()
    with open(GLUTEN_FILTERED, "r", newline="") as f:
        for row in csv.DictReader(f):
            keys.add((row.get("set_id", ""), row.get("ndc_code", "")))
    return keys


def main():
    with open(FLAGGED, "r", newline="") as f:
        rows = list(csv.DictReader(f))
    total = len(rows)
    print(f"Total rows (post-baseline filter): {total:,}\n")

    gluten_keys = load_gluten_filtered_keys()
    if gluten_keys is None:
        print("(gluten_fullcatalog_filtered.csv missing — gluten-parity stat skipped)\n")
    else:
        print(f"Gluten-comparable parity reference set: {len(gluten_keys):,} (set_id, ndc) pairs\n")

    # --- MILK ----------------------------------------------------------------
    print("=" * 60)
    print("MILK")
    print("=" * 60)

    # DPI filter: shared definition from allergen_filters (strict —
    # excludes AEROSOL, METERED pMDIs which do not use lactose carriers).
    dpi_respiratory = [r for r in rows if is_dpi(r.get("dosage_form"), r.get("route"))]
    all_respiratory = [r for r in rows if "RESPIRATORY" in (r.get("route", "") or "").upper()
                                         or "INHAL" in (r.get("route", "") or "").upper()]

    oral = [r for r in rows if is_oral(r.get("route"))]
    parenteral = [r for r in rows if is_parenteral(r.get("route"))]

    def slice_flags(subset, allergen):
        contains = sum(1 for r in subset if r.get(f"{allergen}_flag") == f"contains_{allergen}")
        free = sum(1 for r in subset if r.get(f"{allergen}_flag") == f"{allergen}_free")
        no_data = sum(1 for r in subset if r.get(f"{allergen}_flag") == "no_data")
        return contains, free, no_data

    def gluten_parity_count(subset, allergen):
        """Task #30: count `contains_<allergen>` rows that ALSO appear in
        the gluten-filtered set (gluten methodology denominator)."""
        if gluten_keys is None:
            return None
        return sum(
            1 for r in subset
            if r.get(f"{allergen}_flag") == f"contains_{allergen}"
            and (r.get("set_id", ""), r.get("ndc_code", "")) in gluten_keys
        )

    for label, subset in [("Full catalog", rows),
                          ("All respiratory-route", all_respiratory),
                          ("DPIs (POWDER/INHALANT METERED + respiratory, pMDIs excluded)", dpi_respiratory),
                          ("Oral route", oral),
                          ("Parenteral routes (IV/IM/SC/IT/IA — Hatcher 2025 anchor)", parenteral)]:
        if not subset:
            print(f"  {label}: EMPTY")
            continue
        c, f, n = slice_flags(subset, "milk")
        print(f"  {label} (N={len(subset):,})")
        print(f"    contains_milk: {c:,} ({pct(c, len(subset))})")
        print(f"    milk_free:     {f:,} ({pct(f, len(subset))})")
        print(f"    no_data:       {n:,} ({pct(n, len(subset))})")
    if gluten_keys is not None:
        gp = gluten_parity_count(rows, "milk")
        print(f"  GLUTEN-PARITY (full catalog under gluten filter, N={len(gluten_keys):,}):")
        print(f"    contains_milk: {gp:,} ({pct(gp, len(gluten_keys))})")
    print()

    # --- PEG -----------------------------------------------------------------
    print("=" * 60)
    print("PEG")
    print("=" * 60)

    # Oral-solids slice: shared definition from allergen_filters (matches
    # gluten workflow's filter_gluten_fullcatalog.py convention — TABLET/CAPSULE/GRANULE/
    # PELLET substring, ORALLY DISINTEGRATING excluded).
    oral_solid = [r for r in oral if is_oral_solid(r.get("dosage_form"))]
    oral_solutions = [r for r in oral if "SOLUTION" in (r.get("dosage_form", "") or "").upper()
                                         or "POWDER, FOR SOLUTION" in (r.get("dosage_form", "") or "").upper()
                                         or "POWDER, FOR SUSPENSION" in (r.get("dosage_form", "") or "").upper()]

    # PEG 3350 bowel-prep slice removed 2026-04-22 per user directive:
    # allergen flags must be based on inactive ingredients only. PEG 3350 as
    # active ingredient (MiraLAX-family) is out of scope for this analysis.

    for label, subset in [("Full catalog", rows),
                          ("Oral route", oral),
                          ("Oral tablets/capsules/granules/pellets (ODT-excluded)", oral_solid),
                          ("Oral solutions/powders-for-solution-or-suspension", oral_solutions),
                          ("Parenteral routes (IV/IM/SC/IT/IA — Stone 2019 anchor)", parenteral)]:
        if not subset:
            print(f"  {label}: EMPTY")
            continue
        c, f, n = slice_flags(subset, "peg")
        print(f"  {label} (N={len(subset):,})")
        print(f"    contains_peg: {c:,} ({pct(c, len(subset))})")
        print(f"    peg_free:     {f:,} ({pct(f, len(subset))})")
        print(f"    no_data:      {n:,} ({pct(n, len(subset))})")
    if gluten_keys is not None:
        gp = gluten_parity_count(rows, "peg")
        print(f"  GLUTEN-PARITY (full catalog under gluten filter, N={len(gluten_keys):,}):")
        print(f"    contains_peg: {gp:,} ({pct(gp, len(gluten_keys))})")
    print()

    # --- CARMINE -------------------------------------------------------------
    # Task #22 landscape analysis: no pre-filtering. Describe all
    # contains_carmine products across every meaningful categorical dimension.
    # active_ingredients used for drug-identity labeling only, never for
    # allergen matching.
    print("=" * 60)
    print("CARMINE — landscape (no pre-filtering)")
    print("=" * 60)

    carmine_products = [r for r in rows if r.get("carmine_flag") == "contains_carmine"]
    total_c = len(carmine_products)
    print(f"\nTotal products flagged contains_carmine: {total_c}\n")
    if gluten_keys is not None:
        gp = sum(
            1 for r in carmine_products
            if (r.get("set_id", ""), r.get("ndc_code", "")) in gluten_keys
        )
        print(f"GLUTEN-PARITY (under gluten-methodology filter, N={len(gluten_keys):,}): "
              f"{gp} ({pct(gp, len(gluten_keys))})\n")
    if total_c == 0:
        print("  (no products to analyze)")
    else:
        from collections import Counter
        def breakdown(col, label, top=None):
            vals = [(r.get(col) or "").strip() or "(empty)" for r in carmine_products]
            c = Counter(vals)
            items = c.most_common(top) if top else c.most_common()
            print(f"Breakdown by {label}:")
            for k, n in items:
                print(f"  {k:<50} {n:>5}  ({pct(n, total_c)})")
            print()

        breakdown("route", "route")
        breakdown("dosage_form", "dosage_form")
        breakdown("approval_type", "approval_type")
        breakdown("bulk_category", "bulk_category")
        breakdown("brand_generic", "brand_generic")

        # Active ingredients (drug identity only — never allergen matching).
        # Task #31: split single-active vs combo products. The previous
        # head-ingredient counter under-represented combo products by
        # only counting the first active. Now reports both:
        #   - single-active count (140 of 176 carmine products, ~80%)
        #   - combo-product enumeration with full active lists +
        #     per-active tally for combos.
        def parse_actives(s):
            s = (s or "").upper().strip()
            if not s:
                return []
            return [t.strip() for t in s.split(";") if t.strip()]

        single_active = []
        combo_products = []
        for r in carmine_products:
            actives = parse_actives(r.get("active_ingredients"))
            if len(actives) <= 1:
                single_active.append((r, actives[0] if actives else "(empty)"))
            else:
                combo_products.append((r, actives))

        print(f"Active-ingredient breakdown ({total_c} carmine products):")
        print(f"  Single-active products: {len(single_active)}")
        print(f"  Combo products (2+ actives): {len(combo_products)}")
        print()

        single_ingr = Counter(active for (_, active) in single_active)
        print(f"Top active ingredients in SINGLE-ACTIVE products ({len(single_active)} of {total_c}):")
        for k, n in single_ingr.most_common(15):
            print(f"  {k:<50} {n:>5}  ({pct(n, len(single_active))})")
        print()

        if combo_products:
            print(f"Combo products containing carmine ({len(combo_products)} products):")
            for r, actives in combo_products:
                name = (r.get("drug_name") or "")[:40]
                print(f"  {name:<42}  {' + '.join(actives)}")
            print()

            combo_actives = Counter()
            for _, actives in combo_products:
                for a in actives:
                    combo_actives[a] += 1
            print(f"Per-active tally within combo products:")
            for k, n in combo_actives.most_common(15):
                print(f"  {k:<50} {n:>5}")
            print()

        # Top manufacturers — Task #32 normalization (case + punctuation
        # + whitespace + standard suffixes) so variant spellings of the
        # same company collapse into one entry.
        import re as _re
        SUFFIXES_RE = _re.compile(
            r",?\s+("
            r"INC|LLC|LTD|LIMITED|"
            r"CO\.?|CORP\.?|CORPORATION|"
            r"COMPANY|"
            r"PHARMACEUTICALS?|PHARMA|"
            r"GMBH|S\.A\.|N\.V\.|PLC|"
            r"INCORPORATED|HOLDINGS"
            r")(\.|,)*$",
            _re.IGNORECASE,
        )

        def norm_mfg(s):
            t = (s or "").strip()
            if not t:
                return "(empty)"
            # Normalize whitespace, then iteratively strip standard suffixes.
            t = " ".join(t.split())
            prev = None
            while prev != t:
                prev = t
                t = SUFFIXES_RE.sub("", t).strip().rstrip(",.;:")
            return t.upper()

        # For display we want the normalized key but a representative
        # original spelling for readability. Track most-common original
        # per normalized key.
        mfg_norm_counts = Counter()
        mfg_display = {}
        for r in carmine_products:
            raw = (r.get("manufacturer") or "").strip()
            key = norm_mfg(raw) if raw else "(empty)"
            mfg_norm_counts[key] += 1
            # First-seen non-empty original wins as display label
            if raw and key not in mfg_display:
                mfg_display[key] = raw
        print("Top manufacturers (normalized: case + punctuation + suffixes collapsed):")
        for k, n in mfg_norm_counts.most_common(10):
            display = mfg_display.get(k, k)
            print(f"  {display:<50} {n:>5}  ({pct(n, total_c)})")
        print()

if __name__ == "__main__":
    main()
