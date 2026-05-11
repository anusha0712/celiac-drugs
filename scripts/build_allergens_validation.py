#!/usr/bin/env python3
"""
build_allergens_validation.py — generator for three per-allergen
validation tables: milk, PEG, carmine.

Schema (enforced on every row, Task #21 strict):
    fda_term        exact string or regex
    match_type      "exact" or "regex"
    flag_decision   contains_<allergen> | <allergen>_free | unknown
    source_url      Primary-source URL that supports the CLASSIFICATION
                    claim. For contains_X rows: URL making "this IS X".
                    For X_free rows: URL making "this is NOT X" (or the
                    compound's FDA IID record plus documented
                    non-allergen chemistry).
    iid_status      in_iid | not_in_iid  — from FDA-IID-recent-update.csv
    iid_unii        UNII from IID record if the ingredient is listed
    rationale       Why this row exists

Strict Task #21 rules applied:
  - No AI-reasoned milk_free rows remain. Rows for lactate esters,
    lactobacillus species, ethyl butyrate, plant butters are REMOVED
    because "not in FARE list" is already the default flag behaviour
    (flagger returns milk_free for non-matching tokens). Keeping them
    as explicit rows without a primary source saying "not milk"
    violated Task #21.
  - Lactulose → contains_milk per FARE listing.
  - Validation tables are primary-source-derived:
      Milk:    FARE milk-allergen ingredient list
      PEG:     USP-NF PEG monograph + FDA IID PEG MW grades
      Carmine: 21 CFR 73.100 permitted names + GSRS UNII synonym
               records for cochineal (TZ8Z31B35M) and carminic acid
               (CID8Z8N95N)

Run:
    python3 scripts/build_allergens_validation.py
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fda_iid_lookup import load_iid_index, iid_status, iid_unii_for

BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / "data" / "fullcatalog"
MILK_CSV = OUT_DIR / "milk_validation.csv"
PEG_CSV = OUT_DIR / "peg_validation.csv"
CARMINE_CSV = OUT_DIR / "carmine_validation.csv"

FIELDS = ["fda_term", "match_type", "flag_decision", "source_url",
          "iid_status", "iid_unii", "rationale"]

# Primary-source URLs
URL_CFR_73_100 = "https://www.law.cornell.edu/cfr/text/21/73.100"
URL_CFR_73_1100 = "https://www.law.cornell.edu/cfr/text/21/73.1100"
URL_GSRS_COCHINEAL = "https://precision.fda.gov/uniisearch/srs/unii/TZ8Z31B35M"
URL_GSRS_CARMINIC = "https://precision.fda.gov/uniisearch/srs/unii/CID8Z8N95N"
URL_FARE_MILK = "https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens/milk"
URL_USP_PEG = "https://www.uspnf.com/notices/peg-gen-announcement-20230929"
URL_GREENHAWT_2009 = "https://pubmed.ncbi.nlm.nih.gov/19331724/"
URL_STONE_2019 = "https://pubmed.ncbi.nlm.nih.gov/30557713/"
URL_NWG_2004 = "https://pubmed.ncbi.nlm.nih.gov/15007361/"


def iid_fields_for_exact(term: str) -> dict:
    """Return iid_status + iid_unii for an exact match term."""
    return {
        "iid_status": iid_status(term),
        "iid_unii": iid_unii_for(term),
    }


def iid_fields_for_regex(pattern: str, exemplars: list) -> dict:
    """
    For a regex pattern, check whether any of the supplied exemplar
    ingredient names (known to match the pattern) are in IID.
    Returns 'in_iid' if any exemplar is in IID; 'not_in_iid' otherwise.
    iid_unii is the UNII of the first exemplar found in IID, or empty.
    """
    for ex in exemplars:
        if iid_status(ex) == "in_iid":
            return {"iid_status": "in_iid", "iid_unii": iid_unii_for(ex)}
    return {"iid_status": "not_in_iid", "iid_unii": ""}


# ============================================================================
# MILK — FARE-derived, strict Task #21
# ============================================================================
# Every row cites FARE as the primary classification source
# (FARE explicitly names each listed ingredient as milk-derived).
# Raw-string variants preserve DailyMed source formatting.

MILK_CONTAINS_EXACT = [
    # Lactose family and lactulose removed 2026-05-05 per pharmacist review:
    # milk sugars in purified pharmaceutical form do not themselves contain
    # allergenic milk proteins; lactose intolerance is distinct from milk
    # allergy.

    # Casein family — FARE lists "Casein", "Casein hydrolysate", "Caseinates"
    ("CASEIN", "FARE names 'Casein'."),
    ("SODIUM CASEINATE", "FARE names 'Caseinates (all forms)'."),
    ("CALCIUM CASEINATE", "FARE names 'Caseinates (all forms)'."),
    ("POTASSIUM CASEINATE", "FARE names 'Caseinates (all forms)'."),
    ("HYDROLYZED CASEIN", "FARE names 'Casein hydrolysate'."),
    ("HYDROLYZED CASEIN (ENZYMATIC", "Raw-string casein-hydrolysate variant. FARE milk list."),

    # Whey family — FARE lists "Whey (all forms)", "Whey protein hydrolysate"
    ("WHEY", "FARE names 'Whey (in all forms)'."),
    ("WHEY PROTEIN HYDROLYSATE", "FARE names 'Whey protein hydrolysate'."),

    # Specific milk proteins — FARE lists Lactalbumin, Lactoglobulin, Lactoferrin
    ("ALPHA-LACTALBUMIN", "FARE names 'Lactalbumin'."),
    (".ALPHA.-LACTALBUMIN", "Raw-string lactalbumin variant. FARE milk list."),
    ("ALPHA-LACTALBUMIN (BOVINE)", "Raw-string bovine-lactalbumin variant. FARE milk list."),
    ("BETA-LACTOGLOBULIN", "FARE names 'Lactoglobulin'."),
    ("LACTOFERRIN", "FARE names 'Lactoferrin'."),
    ("LACTOFERRIN, BOVINE", "Raw-string bovine-lactoferrin variant. FARE milk list."),
    ("LACTOPEROXIDASE", "Related milk-protein enzyme; FARE classifies as milk-derived under protein fraction."),
    ("LACTOPEROXIDASE BOVINE", "Raw-string bovine-lactoperoxidase variant."),

    # Whole milk + milk fat — FARE lists Milk (all forms), Milkfat, Buttermilk
    ("MILK", "FARE names 'Milk (in all forms...)'."),
    ("SKIM MILK", "FARE names 'Milk ... skimmed, nonfat'."),
    ("COW MILK", "FARE names 'Milk (in all forms)'."),
    ("COW MILK FAT", "FARE names 'Milkfat'."),
    ("GOAT MILK", "FARE names 'milk from other animals' including goat."),
    ("BOS TAURUS COLOSTRUM", "Bovine colostrum is a milk derivative. FARE milk list."),
    ("MILK PROTEIN", "FARE names 'Milk protein'."),
    ("MILK PROTEIN CONCENTRATE", "FARE names 'Milk protein' fraction."),
    ("AMINO ACIDS, MILK", "Amino acids sourced from milk. FARE milk list."),
    ("NONFAT DRY MILK", "FARE names 'Milk ... nonfat, dry'."),
    ("BUTTERMILK", "FARE names 'Buttermilk'."),
]


def build_milk_csv():
    rows = []
    for term, rationale in MILK_CONTAINS_EXACT:
        row = {
            "fda_term": term,
            "match_type": "exact",
            "flag_decision": "contains_milk",
            "source_url": URL_FARE_MILK,
            "rationale": rationale,
            **iid_fields_for_exact(term),
        }
        rows.append(row)

    MILK_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(MILK_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


# ============================================================================
# PEG — tight-scope, USP-NF-anchored, strict Task #21
# ============================================================================
# Scope locked to unconjugated PEG polymer per 2026-04-22 decision.
# All 4 regex patterns have IID cross-reference via exemplars.

PEG_CONTAINS_REGEX = [
    # (pattern, rationale, exemplars for IID cross-check)
    (r"\bPOLYETHYLENE\s+GLYCOL",
     "USP-NF PEG monograph name. Catches all MW grades, unspecified, plural.",
     ["POLYETHYLENE GLYCOL 400", "POLYETHYLENE GLYCOL 3350",
      "POLYETHYLENE GLYCOL 8000", "POLYETHYLENE GLYCOL"]),

    (r"\bPOLYETHYLENE\s+OXIDE",
     "Same polymer as PEG at higher MW. USP-NF PEO monograph.",
     ["POLYETHYLENE OXIDE"]),

    (r"\bMACROGOL",
     "EU/USP-EP name for PEG. Synonym per USP-NF cross-reference.",
     ["MACROGOL"]),

    (r"\bCARBOWAX",
     "Dow trade name for PEG (rare in DailyMed; kept as defensive).",
     ["CARBOWAX"]),

    # Note (2026-04-23 Task #23 reconsideration): `\bPEG\b` was
    # considered as a 5th regex row but rejected. Word-boundary
    # `\bPEG\b` matches 264 unique DailyMed excipient strings —
    # almost all PEG-N derivatives (PEG-40 STEARATE, BIS-PEG-12
    # DIMETHICONE, PEG-10 .BETA.-SITOSTEROL, etc.) which fall under
    # the explicitly-excluded adjacent families per §3.6 (tight
    # scope). Adding it would re-broaden the flag classification
    # past the tight-scope decision. The `\bPEG\b` token is kept in
    # `analyze_peg_labels.py` warning-detector vocabulary because
    # warning detection runs against SPL XML warning-section text
    # (where "PEG-allergic" is real label vocabulary), not against
    # excipient strings. The asymmetry is by design and disclosed
    # in methodology.md §5 + limitations.md §PEG.
]


def build_peg_csv():
    rows = []
    for pat, rationale, exemplars in PEG_CONTAINS_REGEX:
        row = {
            "fda_term": pat,
            "match_type": "regex",
            "flag_decision": "contains_peg",
            "source_url": URL_USP_PEG,
            "rationale": rationale,
            **iid_fields_for_regex(pat, exemplars),
        }
        rows.append(row)

    PEG_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(PEG_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


# ============================================================================
# CARMINE — 21 CFR + GSRS synonym-derived, strict Task #21
# ============================================================================

CARMINE_CONTAINS_EXACT = [
    # 21 CFR 73.100(d)(2) permitted names
    ("CARMINE", URL_CFR_73_100,
     "21 CFR 73.100(d)(2) permitted name for cochineal-extract color "
     "additive. Greenhawt 2009 anaphylaxis anchor."),
    ("COCHINEAL EXTRACT", URL_CFR_73_100,
     "21 CFR 73.100(d)(2) permitted name."),

    # GSRS UNII TZ8Z31B35M (COCHINEAL) synonym record
    ("COCHINEAL", URL_GSRS_COCHINEAL,
     "GSRS UNII TZ8Z31B35M preferred name."),
    ("DACTYLOPIUS COCCUS COLORANT", URL_GSRS_COCHINEAL,
     "GSRS synonym on COCHINEAL (species-name form)."),
    ("DACTYLOPIUS CACTI COLORANT", URL_GSRS_COCHINEAL,
     "GSRS synonym on COCHINEAL (species-name form)."),
    ("COCCUS CACTI COLORANT", URL_GSRS_COCHINEAL,
     "GSRS synonym on COCHINEAL (older genus form)."),

    # GSRS UNII CID8Z8N95N (CARMINIC ACID) synonym record
    ("CARMINIC ACID", URL_GSRS_CARMINIC,
     "GSRS UNII CID8Z8N95N preferred name. The anthraquinone component "
     "of cochineal/carmine."),
    ("CI 75470", URL_GSRS_CARMINIC,
     "Colour Index 75470 = carminic acid (GSRS synonym)."),
    ("C.I. 75470", URL_GSRS_CARMINIC,
     "Punctuated variant. GSRS synonym."),
    ("NATURAL RED 4", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("C.I. NATURAL RED 4", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("NATURAL RED 2180", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("E 120", URL_GSRS_CARMINIC,
     "EU food colorant number. GSRS synonym."),
    ("E-120", URL_GSRS_CARMINIC,
     "Hyphenated variant. GSRS synonym."),
    ("E120", URL_GSRS_CARMINIC,
     "Unspaced variant of E 120. Defensive."),
    ("INS-120", URL_GSRS_CARMINIC,
     "Codex INS code for carmine. GSRS synonym."),
    ("INS 120", URL_GSRS_CARMINIC,
     "Spaced variant. Defensive."),
    ("COCHINEAL CARMINE", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("CARMINE 5297", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("COCHINEAL RED PWD", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
    ("SUN RED NO. 1", URL_GSRS_CARMINIC,
     "GSRS synonym on CARMINIC ACID."),
]

CARMINE_CONTAINS_REGEX = [
    (r"\bCARMINE\b", URL_CFR_73_100,
     "Word-boundary CARMINE. Avoids CROSCARMELLOSE false-match.",
     ["CARMINE"]),
    (r"\bCARMINIC\b", URL_GSRS_CARMINIC,
     "Word-boundary CARMINIC (catches CARMINIC ACID and variants).",
     ["CARMINIC ACID"]),
    (r"\bCOCHINEAL\b", URL_GSRS_COCHINEAL,
     "Word-boundary COCHINEAL.",
     ["COCHINEAL", "COCHINEAL EXTRACT"]),
]


def build_carmine_csv():
    rows = []
    for term, url, rationale in CARMINE_CONTAINS_EXACT:
        row = {
            "fda_term": term,
            "match_type": "exact",
            "flag_decision": "contains_carmine",
            "source_url": url,
            "rationale": rationale,
            **iid_fields_for_exact(term),
        }
        rows.append(row)
    for pat, url, rationale, exemplars in CARMINE_CONTAINS_REGEX:
        row = {
            "fda_term": pat,
            "match_type": "regex",
            "flag_decision": "contains_carmine",
            "source_url": url,
            "rationale": rationale,
            **iid_fields_for_regex(pat, exemplars),
        }
        rows.append(row)

    CARMINE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(CARMINE_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    # Load IID once (cached via lru_cache)
    name_idx, _ = load_iid_index()
    print(f"FDA IID loaded: {len(name_idx):,} unique ingredient names")
    print()

    n_milk = build_milk_csv()
    n_peg = build_peg_csv()
    n_carmine = build_carmine_csv()
    print(f"Wrote {MILK_CSV.relative_to(BASE_DIR)} ({n_milk} entries)")
    print(f"Wrote {PEG_CSV.relative_to(BASE_DIR)} ({n_peg} entries)")
    print(f"Wrote {CARMINE_CSV.relative_to(BASE_DIR)} ({n_carmine} entries)")

    # Quick IID coverage summary
    for path in (MILK_CSV, PEG_CSV, CARMINE_CSV):
        with open(path) as f:
            rows = list(csv.DictReader(f))
        in_iid_count = sum(1 for r in rows if r["iid_status"] == "in_iid")
        print(f"  {path.stem}: {in_iid_count}/{len(rows)} rows in FDA IID")


if __name__ == "__main__":
    main()
