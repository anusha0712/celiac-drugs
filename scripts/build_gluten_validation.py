#!/usr/bin/env python3
"""
build_gluten_validation.py — One-time script to build data/fullcatalog/gluten_validation.csv

Combines the 48 pilot validation entries (with product counts updated to reflect
the full catalog) with new entries researched from the bulk dataset.

Total entries: 133 (48 pilot + 85 new)
  - 36 new flagged gluten_free
  - 23 new flagged contains_gluten
  - 26 new flagged unknown

This script is a one-shot generator. The output CSV is the source of truth.
Re-running this script will regenerate the same CSV deterministically.

Run:
  python3 build_gluten_validation.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from allergen_filters import EXCIPIENT_DELIMITER

BASE_DIR = Path(__file__).parent.parent
# Pilot CSV is read here as input for PILOT_OVERRIDES inheritance only
# (Phase 1-3 historical entries are preserved). The pilot remains
# documented separately in `analysis/allergens/gluten/methodology_pilot.md`
# (Task #33); this cross-reference is the only code-level link.
BULK_CSV = BASE_DIR / "data" / "fullcatalog" / "dailymed_fullcatalog_raw.csv"
PILOT_CSV = BASE_DIR / "data" / "pilot" / "gluten_pilot_validation.csv"
OUTPUT_CSV = BASE_DIR / "data" / "fullcatalog" / "gluten_validation.csv"

# Source URL constants
URL_GLUTEN_DEF = "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101/subpart-F/section-101.91"
URL_FDA_IIG = "https://www.fda.gov/drugs/drug-approvals-and-databases/inactive-ingredients-database-download"
URL_FDA_CPG = "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-578100-starches-common-or-usual-names"
URL_NCA_XANTHAN = "https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/"
URL_DRUGS_SSG = "https://www.drugs.com/inactive/sodium-starch-glycolate-128.html"
URL_HANDBOOK = "https://www.pharmpress.com/product/9780857113757/handbook-of-pharmaceutical-excipients"


def get_bulk_counts():
    """Count appearances of every excipient string in the bulk catalog."""
    counts = Counter()
    with open(BULK_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = row.get("excipients_raw", "").strip()
            if not raw:
                continue
            for exc in raw.split(EXCIPIENT_DELIMITER):
                exc = exc.strip()
                if exc:
                    counts[exc.upper()] += 1
    return counts


def load_pilot_entries():
    """Load the 48 pilot validation entries."""
    entries = []
    with open(PILOT_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries


def update_pilot_rationale(entry, bulk_count):
    """Update the rationale of a pilot entry to reflect bulk catalog counts."""
    rationale = entry["rationale"]
    if bulk_count == 0:
        new_note = " Bulk catalog: 0 products."
    else:
        new_note = f" Bulk catalog: {bulk_count:,} products."
    # Append count info; do not modify pilot rationale otherwise
    entry["rationale"] = rationale.rstrip() + new_note
    # Add bulk source if found in bulk
    if bulk_count > 0 and "dailymed_bulk" not in entry["source"]:
        entry["source"] = entry["source"] + "|dailymed_bulk"
    return entry


# ----------------------------------------------------------------------------
# PILOT OVERRIDES — bulk-table revisions to pilot entries
# ----------------------------------------------------------------------------
# These overrides apply to entries that exist in the pilot validation table but
# whose flag or source URL has been revised based on later evidence (NCA, GIG,
# pharmacist consultation, etc.). The pilot CSV (data/pilot/gluten_pilot_validation.csv)
# is left unchanged — only the bulk output is modified.
#
# Format: fda_term -> dict of fields to override

PILOT_OVERRIDES = {
    "GLUCOSE SYRUP": {
        "flag_decision": "gluten_free",
        "rationale_override": (
            "Glucose syrup is a starch hydrolysate that may be derived from corn, "
            "wheat, or barley starch. Per National Celiac Association: 'Glucose syrup "
            "is considered safe even when derived from wheat, barley or rye because "
            "the process used to produce glucose syrup renders the starting material "
            "to contain less than 20 parts per million of gluten.' Reclassified from "
            "the pilot's precautionary 'unknown' flag to 'gluten_free' based on "
            "current NCA guidance."
        ),
        "source_url": "https://nationalceliac.org/ingredients-people-question/",
        "source_append": "|nca",
    },
    "LIQUID GLUCOSE": {
        "flag_decision": "gluten_free",
        "rationale_override": (
            "FDA IIG term for glucose syrup. Same compound family as GLUCOSE SYRUP. "
            "Per National Celiac Association: glucose syrup is considered gluten "
            "free regardless of starting material because processing reduces gluten "
            "below 20 ppm. Reclassified from the pilot's precautionary 'unknown' "
            "flag to 'gluten_free' based on current NCA guidance."
        ),
        "source_url": "https://nationalceliac.org/ingredients-people-question/",
        "source_append": "|nca",
    },
    "MALTODEXTRIN": {
        # No flag change — already gluten_free in pilot
        "source_url": (
            "https://www.fda.gov/media/116958/download | "
            "https://nationalceliac.org/ingredients-people-question/"
        ),
        "source_append": "|nca",
    },
}


def apply_pilot_override(entry):
    """Apply any override defined in PILOT_OVERRIDES for this pilot entry."""
    term = entry["fda_term"].strip().upper()
    override = PILOT_OVERRIDES.get(term)
    if not override:
        return entry
    if "flag_decision" in override:
        entry["flag_decision"] = override["flag_decision"]
    if "rationale_override" in override:
        # Replace pilot rationale entirely; bulk count will still be appended later
        entry["rationale"] = override["rationale_override"]
    if "source_url" in override:
        entry["source_url"] = override["source_url"]
    if "source_append" in override and override["source_append"] not in entry["source"]:
        entry["source"] = entry["source"] + override["source_append"]
    return entry


# ----------------------------------------------------------------------------
# NEW ENTRIES — full catalog excipients not in pilot table
# ----------------------------------------------------------------------------
# Format: (fda_term, flag_decision, rationale, source_url, eu_equivalent)
# Source field is hardcoded to "dailymed_bulk" for all new entries.

NEW_ENTRIES = [

    # ========================================================================
    # GLUTEN_FREE — source-specified non-gluten starches and starch derivatives
    # ========================================================================

    ("STARCH, TAPIOCA", "gluten_free",
     "Starch derived from cassava root (Manihot esculenta). Tapioca is not a cereal grain and contains no gluten. Source explicitly specified. UNII: 24SC3U704I / B8WCK70T7I.",
     URL_FDA_IIG, "Tapioca starch"),

    ("STARCH, RICE", "gluten_free",
     "Starch derived from rice (Oryza sativa). Rice is not a gluten-containing grain per FDA 21 CFR 101.91. Source explicitly specified. UNII: 4DGK8B7I3S.",
     URL_GLUTEN_DEF, "Rice starch"),

    ("ORYZA SATIVA (RICE) STARCH", "gluten_free",
     "Latin botanical naming for rice starch. Rice is not a gluten-containing grain per FDA 21 CFR 101.91. Same compound as STARCH, RICE.",
     URL_GLUTEN_DEF, "Rice starch"),

    ("DIMETHYLIMIDAZOLIDINONE RICE STARCH", "gluten_free",
     "Modified rice starch with dimethylimidazolidinone substitution. Rice is not a gluten-containing grain per FDA 21 CFR 101.91. Source explicitly specified as rice.",
     URL_FDA_IIG, ""),

    ("SOLANUM TUBEROSUM (POTATO) STARCH", "gluten_free",
     "Latin botanical naming for potato starch. Potato is not a cereal grain. Same compound as STARCH, POTATO.",
     URL_FDA_IIG, "Potato starch"),

    ("SODIUM HYDROLYZED POTATO STARCH DODECENYLSUCCINATE", "gluten_free",
     "Modified potato starch (hydrolyzed, dodecenylsuccinate ester, sodium salt). Potato source explicitly specified. Potato is not a cereal grain. UNII: APY6XCX4XA.",
     URL_FDA_IIG, ""),

    ("DEXTRIN, CORN", "gluten_free",
     "Dextrin derived from corn starch. Corn is not a gluten-containing grain. Source explicitly specified.",
     URL_FDA_IIG, ""),

    ("DEXTRIN, POTATO", "gluten_free",
     "Dextrin derived from potato starch. Potato is not a cereal grain. Source explicitly specified. UNII: ML93R7MDR7.",
     URL_FDA_IIG, ""),

    ("DEXTRIN PALMITATE (CORN", "gluten_free",
     "Dextrin palmitate ester with corn source specified. Note: incomplete parenthesis in DailyMed label data — appears as 'DEXTRIN PALMITATE (CORN' without closing paren. Same substance as the pilot entry 'DEXTRIN PALMITATE (CORN)'. Corn is not a gluten-containing grain.",
     URL_FDA_IIG, ""),

    ("CORN GRAIN", "gluten_free",
     "Corn (Zea mays) kernel. Corn is not a gluten-containing grain per FDA 21 CFR 101.91. UNII: C1Z9U7094Z.",
     URL_GLUTEN_DEF, ""),

    ("CORN STARCH 3-E-DODECENYL SUCCINIC ANHYDRIDE MODIFIED", "gluten_free",
     "Modified corn starch with dodecenyl succinic anhydride substitution. Corn source explicitly specified. Corn is not a gluten-containing grain.",
     URL_FDA_IIG, "Modified starch"),

    ("RICE BRAN OIL", "gluten_free",
     "Oil extracted from rice bran. Rice is not a gluten-containing grain per FDA 21 CFR 101.91. UNII: H5WVD9LZUD / LZO6K1506A.",
     URL_GLUTEN_DEF, ""),

    ("ORYZA SATIVA (RICE) BRAN", "gluten_free",
     "Rice bran (Latin botanical naming). Rice is not a gluten-containing grain per FDA 21 CFR 101.91. Same as the pilot entry RICE BRAN.",
     URL_GLUTEN_DEF, ""),

    ("RICE BRAN, DEFATTED", "gluten_free",
     "Defatted rice bran. Rice is not a gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("AMINO ACIDS, CORN GLUTEN", "gluten_free",
     "Amino acids derived from corn zein (the storage protein of corn, sometimes called 'corn gluten'). Despite the name, corn 'gluten' is NOT the same as wheat gluten that causes celiac disease. Corn is not a gluten-containing grain per FDA 21 CFR 101.91. UNII: 0540V8ZD7V.",
     URL_GLUTEN_DEF, ""),

    # ========================================================================
    # GLUTEN_FREE — gums (plant-derived, fermentation, or cellulose-based)
    # ========================================================================

    ("CELLULOSE GUM", "gluten_free",
     "Sodium carboxymethylcellulose. Cellulose-based, derived from wood pulp/cotton — NOT starch-derived. Same chemical class as croscarmellose sodium. Inherently gluten-free. UNII: K679OBS311 / others.",
     URL_FDA_IIG, ""),

    ("DEHYDROXANTHAN GUM", "gluten_free",
     "Chemically modified xanthan gum (dehydration product). Xanthan gum is produced by Xanthomonas campestris fermentation. Per National Celiac Association, xanthan gum does not contain gluten. Same classification reasoning applies to dehydroxanthan gum.",
     URL_NCA_XANTHAN, ""),

    ("SCLEROTIUM GUM", "gluten_free",
     "Polysaccharide produced by fermentation of Sclerotium rolfsii (a fungus). Plant-derived fermentation product, not a cereal grain derivative.",
     URL_FDA_IIG, ""),

    ("ACACIA SENEGAL GUM", "gluten_free",
     "Gum exudate from Acacia senegal tree. Same substance as the pilot entry ACACIA (gum arabic). Plant-derived, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("ACACIA SEYAL GUM", "gluten_free",
     "Gum exudate from Acacia seyal tree (a different Acacia species producing similar gum). Plant-derived, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("GUM TALHA", "gluten_free",
     "Alternative name for Acacia seyal gum. Plant-derived tree exudate, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("PISTACIA LENTISCUS (MASTIC) GUM", "gluten_free",
     "Mastic resin from Pistacia lentiscus tree. Tree-derived resin, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("BOSWELLIA SERRATA GUM", "gluten_free",
     "Frankincense gum from Boswellia serrata tree. Tree-derived resin, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("EUCALYPTUS GUM", "gluten_free",
     "Resin from Eucalyptus trees. Tree-derived, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("KARAYA GUM", "gluten_free",
     "Gum from Sterculia urens tree (also called gum karaya). Tree-derived exudate, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("STYRAX BENZOIN GUM", "gluten_free",
     "Resin from Styrax benzoin tree (gum benjamin). Tree-derived, no cereal grain connection.",
     URL_FDA_IIG, ""),

    ("LOCUST BEAN GUM", "gluten_free",
     "Galactomannan from carob seeds (Ceratonia siliqua) — a legume. No cereal grain connection. UNII: V4716MY704.",
     URL_FDA_IIG, ""),

    ("CYAMOPSIS TETRAGONOLOBA (GUAR) GUM", "gluten_free",
     "Latin botanical naming for guar gum. Same substance as the pilot entry GUAR GUM. Derived from guar bean (legume).",
     URL_FDA_IIG, ""),

    ("CAESALPINIA SPINOSA GUM", "gluten_free",
     "Tara gum from seeds of Caesalpinia spinosa tree (a legume). No cereal grain connection.",
     URL_FDA_IIG, ""),

    ("GELLAN GUM (HIGH ACYL)", "gluten_free",
     "High-acyl form of gellan gum, produced by Sphingomonas elodea bacterial fermentation. Same classification as the pilot entry GELLAN GUM (LOW ACYL). Bacterial fermentation typically does not use wheat substrates.",
     URL_FDA_IIG, ""),

    ("GELLAN GUM", "gluten_free",
     "Bacterial polysaccharide from Sphingomonas elodea fermentation. Same substance as the LOW ACYL and HIGH ACYL variants.",
     URL_FDA_IIG, ""),

    ("DIUTAN GUM", "gluten_free",
     "Microbial polysaccharide produced by Sphingomonas sp. bacterial fermentation. Not a cereal grain derivative.",
     URL_FDA_IIG, ""),

    ("RHIZOBIAN GUM", "gluten_free",
     "Polysaccharide produced by Rhizobium bacteria. Bacterial fermentation product, not a cereal grain derivative.",
     URL_FDA_IIG, ""),

    ("BIOSACCHARIDE GUM-1", "gluten_free",
     "Polysaccharide produced by bacterial fermentation. Cosmetic/skincare ingredient, not a cereal grain derivative. Per cosmetic ingredient databases, derived from bacterial fermentation of plant sugars.",
     URL_FDA_IIG, ""),

    ("BIOSACCHARIDE GUM-2", "gluten_free",
     "Polysaccharide produced by bacterial fermentation. Same family as BIOSACCHARIDE GUM-1. Not a cereal grain derivative.",
     URL_FDA_IIG, ""),

    ("BIOSACCHARIDE GUM-4", "gluten_free",
     "Polysaccharide produced by bacterial fermentation. Same family as BIOSACCHARIDE GUM-1. Not a cereal grain derivative.",
     URL_FDA_IIG, ""),

    # ========================================================================
    # CONTAINS_GLUTEN — wheat-derived excipients
    # ========================================================================

    ("WHEAT GERM", "contains_gluten",
     "Embryo of the wheat (Triticum) kernel. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91. Wheat germ contains residual gluten proteins. UNII: YR3G369F5A.",
     URL_GLUTEN_DEF, ""),

    ("WHEAT BRAN", "contains_gluten",
     "Outer husk of the wheat kernel. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91. Wheat bran contains gluten proteins.",
     URL_GLUTEN_DEF, ""),

    ("WHEAT SPROUT", "contains_gluten",
     "Sprouted wheat. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91. Sprouting reduces but does not eliminate gluten content.",
     URL_GLUTEN_DEF, ""),

    ("WHEAT GLUTEN", "contains_gluten",
     "Wheat gluten — by definition contains gluten proteins (gliadin + glutenin). Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91. UNII: 1534K8653J.",
     URL_GLUTEN_DEF, ""),

    ("AMINO ACIDS, WHEAT", "contains_gluten",
     "Amino acids derived from wheat protein hydrolysis. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91. Hydrolyzed wheat protein products may retain gluten residues.",
     URL_GLUTEN_DEF, ""),

    ("HYDROLYZED WHEAT PROTEIN (ENZYMATIC, 3000 MW)", "contains_gluten",
     "Wheat protein hydrolyzed to ~3000 molecular weight by enzymatic action. Despite hydrolysis, wheat-derived hydrolyzed proteins may retain gluten residues above the 20 ppm gluten-free threshold. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("HYDROLYZED WHEAT PROTEIN (ENZYMATIC", "contains_gluten",
     "Same compound family as 'HYDROLYZED WHEAT PROTEIN (ENZYMATIC, 3000 MW)'. Note: incomplete parenthesis in DailyMed label data. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("WHEAT GERM OIL", "contains_gluten",
     "Oil extracted from wheat germ. While oil extraction reduces protein content, wheat germ oil may still contain residual gluten proteins. Wheat source explicitly identified. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("WHEAT GERM OIL UNSAPONIFIABLES", "contains_gluten",
     "Unsaponifiable fraction of wheat germ oil. Wheat-derived. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("TRITICUM VULGARE (WHEAT) GERM", "contains_gluten",
     "Wheat germ — Latin botanical naming with English clarification. Same substance as WHEAT GERM. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("TRITICUM VULGARE (WHEAT) GERM OIL", "contains_gluten",
     "Wheat germ oil — Latin botanical naming with English clarification. Same substance as WHEAT GERM OIL. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("TRITICUM VULGARE (WHEAT) GERM OIL UNSAPONIFIABLES", "contains_gluten",
     "Unsaponifiable fraction of wheat germ oil — Latin botanical naming. Wheat-derived. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("TRITICUM AESTIVUM WHOLE", "contains_gluten",
     "Whole wheat plant material (Triticum aestivum = common bread wheat). Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("TRITICUM AESTIVUM POLLEN", "contains_gluten",
     "Wheat pollen. While pollen itself is from the flower (not the grain), the label identifies wheat as the source. A celiac patient cannot determine safety from this labeling. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("SODIUM COCOYL WHEAT AMINO ACIDS", "contains_gluten",
     "Wheat-derived amino acids reacted with coconut fatty acids to form a surfactant. Wheat source identified in name. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("CETEARYL WHEAT STRAW GLYCOSIDES", "contains_gluten",
     "Glycosides derived from wheat straw, paired with cetearyl alcohol. While wheat straw (stem) contains less gluten than the grain, the label identifies wheat. Wheat is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    # ========================================================================
    # CONTAINS_GLUTEN — barley-derived excipients
    # ========================================================================

    ("BARLEY MALT", "contains_gluten",
     "Malted barley grain. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91. Malt is the most common gluten exposure source from barley. UNII: R3NBG8914U.",
     URL_GLUTEN_DEF, ""),

    ("BARLEY MALT SYRUP", "contains_gluten",
     "Syrup made from malted barley. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91. Contains hydrolyzed barley proteins including gluten. UNII: 22P8DKP670.",
     URL_GLUTEN_DEF, ""),

    ("BARLEY BRAN", "contains_gluten",
     "Outer husk of the barley kernel. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("HORDEUM VULGARE WHOLE", "contains_gluten",
     "Whole barley plant material (Hordeum vulgare = common barley). Barley is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("HORDEUM VULGARE TOP", "contains_gluten",
     "Top portions of the barley plant. Label identifies barley source. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("HORDEUM VULGARE ROOT", "contains_gluten",
     "Barley root. Label identifies barley source. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    ("HORDEUM DISTICHON (BARLEY) EXTRACT", "contains_gluten",
     "Extract from Hordeum distichon (two-row barley). Label identifies barley. Barley is a primary gluten-containing grain per FDA 21 CFR 101.91.",
     URL_GLUTEN_DEF, ""),

    # ========================================================================
    # UNKNOWN — source-unspecified starches and starch derivatives
    # ========================================================================

    ("ALUMINUM STARCH OCTENYLSUCCINATE", "unknown",
     "Aluminum salt of starch octenylsuccinate ester. Used as an absorbent and anti-caking agent in topical products and oral medications. The starch source is not specified on the label — may be corn, tapioca, or potato in pharmaceutical practice, but wheat-derived starches are also possible. Per project rules, source-unspecified starch derivatives are flagged unknown. This is the highest-impact new entry by product count.",
     URL_FDA_IIG, "Modified starch"),

    ("HYDROGENATED STARCH HYDROLYSATE", "unknown",
     "Mixture of sugar alcohols (sorbitol, maltitol, longer-chain polyols) produced by hydrogenation of partially hydrolyzed starch. The starch source is not specified on the label — could be corn, wheat, or other starches. Per project rules, source-unspecified starch derivatives are flagged unknown.",
     URL_FDA_IIG, ""),

    ("HYDROXYPROPYL STARCH", "unknown",
     "Modified starch with hydroxypropyl substitution. Source not specified on the label. UNII: 9M44R3409A. Per project rules, source-unspecified starch derivatives are flagged unknown. NOTE: distinct from HYDROXYPROPYL CORN STARCH (5% SUBSTITUTION BY WEIGHT) which has corn source specified.",
     URL_FDA_IIG, ""),

    ("HYDROXYETHYL STARCH 130/0.4", "unknown",
     "Pharmaceutical-grade hydroxyethyl starch, 130 kDa molecular weight, substitution degree 0.4. Used as a plasma volume expander in IV solutions. While pharmaceutical HES is overwhelmingly derived from waxy maize (corn) per industry practice, the label does not specify the source. Per project rules, source-unspecified starch derivatives are flagged unknown for patient-facing labeling analysis. UNII: 1GVO236S58.",
     URL_FDA_IIG, ""),

    ("GLUCOSE", "gluten_free",
     "Glucose (D-glucose, dextrose) listed as an excipient. Per National Celiac Association: 'Dextrose is simply another word for glucose. It is considered gluten free regardless of the starting material.' Glucose syrup processing reduces gluten below 20 ppm even when starting material is wheat or barley. Reclassified from initial 'unknown' precautionary flag to 'gluten_free' per current NCA guidance.",
     "https://nationalceliac.org/ingredients-people-question/", "Glucose syrup"),

    ("SODIUM POLYACRYLATE STARCH (12 MICROMETER PARTICLE)", "unknown",
     "Cross-linked sodium polyacrylate-starch superabsorbent polymer with 12 micrometer particle size. The starch component source is not specified on the label. Per project rules, source-unspecified starch derivatives are flagged unknown, even when the compound is highly processed and unlikely to retain native protein.",
     URL_FDA_IIG, ""),

    ("SODIUM POLYACRYLATE STARCH (25 MICROMETER PARTICLE)", "unknown",
     "Cross-linked sodium polyacrylate-starch superabsorbent polymer with 25 micrometer particle size. Same compound family as the 12 micrometer variant. Starch source not specified on the label.",
     URL_FDA_IIG, ""),

    ("SODIUM POLYACRYLATE STARCH (7 MICROMETER PARTICLE)", "unknown",
     "Cross-linked sodium polyacrylate-starch superabsorbent polymer with 7 micrometer particle size. Same compound family. Starch source not specified.",
     URL_FDA_IIG, ""),

    ("SODIUM POLYACRYLATE STARCH (400 MICROMETER PARTICLE)", "unknown",
     "Cross-linked sodium polyacrylate-starch superabsorbent polymer with 400 micrometer particle size. Same compound family. Starch source not specified.",
     URL_FDA_IIG, ""),

    # ========================================================================
    # UNKNOWN — oats and oat derivatives (cross-contamination risk)
    # ========================================================================
    # Following the pilot's OATS / OAT FIBER classification: oats are not
    # classified as a gluten-containing grain by FDA (21 CFR 101.91) but are
    # frequently cross-contaminated with wheat/barley/rye during cultivation
    # and processing. Flagged unknown precautionarily.

    ("OAT", "unknown",
     "Oat (Avena sativa). Not classified as a gluten-containing grain by FDA per 21 CFR 101.91, but commonly cross-contaminated with wheat, barley, or rye during cultivation and processing. Flagged unknown precautionarily, consistent with the pilot's OATS classification.",
     URL_GLUTEN_DEF, "Oats"),

    ("OAT KERNEL OIL", "unknown",
     "Oil extracted from oat kernels. Same cross-contamination concerns as oats. UNII: 3UVP41R77R.",
     URL_GLUTEN_DEF, "Oats"),

    ("OAT BRAN", "unknown",
     "Oat bran. Same cross-contamination concerns as oats. UNII: KQX236OK4U.",
     URL_GLUTEN_DEF, "Oats"),

    ("OAT STRAW", "unknown",
     "Oat plant straw (stem material). Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("OAT AMINO ACIDS", "unknown",
     "Amino acids derived from oats. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AMINO ACIDS, OAT", "unknown",
     "Amino acids derived from oats (alternate naming). Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("SODIUM LAUROYL OAT AMINO ACIDS", "unknown",
     "Oat-derived amino acids reacted with lauric acid to form a surfactant. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("STARCH, OAT", "unknown",
     "Oat starch. Same cross-contamination concerns as oats. UNII: 904CE6697V.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA WHOLE", "unknown",
     "Whole oat plant material (Avena sativa = common oat). Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA LEAF", "unknown",
     "Oat leaf. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA TOP", "unknown",
     "Oat plant top portions. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA FLOWERING TOP", "unknown",
     "Oat flowering top. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA POLLEN", "unknown",
     "Oat pollen. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA (OAT) KERNEL OIL", "unknown",
     "Oat kernel oil — Latin botanical naming with English clarification. Same substance as OAT KERNEL OIL. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA (OAT) KERNEL EXTRACT", "unknown",
     "Oat kernel extract — Latin botanical naming. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA (OAT) BRAN", "unknown",
     "Oat bran — Latin botanical naming. Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    ("AVENA SATIVA (OAT) STARCH", "unknown",
     "Oat starch — Latin botanical naming. Same substance as STARCH, OAT (UNII: 904CE6697V). Same cross-contamination concerns as oats.",
     URL_GLUTEN_DEF, "Oats"),

    # ========================================================================
    # GLUTEN_FREE — cyclodextrin family (interim decision, 2026-04-09)
    # ========================================================================
    # Source: Gluten Intolerance Group (GIG) "Medications and the Gluten-Free
    # Diet," Jan 2019. NOTE: source is >5 years old (stale per project rule).
    # Pending pharmacist consultation (see analysis/allergens/gluten/validation_table_review_gluten.md Q3).
    # Cyclodextrins are CYCLIC oligosaccharides — chemically distinct from
    # maltodextrin (linear). Their classifications are NOT chained.

    ("CYCLODEXTRINS", "gluten_free",
     "Cyclic oligosaccharides produced by enzymatic action on starch. Per the Gluten Intolerance Group's January 2019 patient education guide, cyclodextrins are listed in the 'could be derived from wheat or barley' category, but interim project decision is gluten_free pending pharmacist consultation. NOTE: GIG source is >5 years old (stale). Cyclodextrin is chemically distinct from maltodextrin (cyclic vs linear) — classifications not chained.",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("CYCLODEXTRIN", "gluten_free",
     "Singular form of CYCLODEXTRINS. Same compound class. Interim gluten_free per GIG 2019 (stale source) — pending pharmacist consultation.",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("BETADEX", "gluten_free",
     "Beta-cyclodextrin (USP/INCI name BETADEX). Cyclic oligosaccharide derived from starch. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYL BETADEX", "gluten_free",
     "Hydroxypropyl ether of beta-cyclodextrin. Modified cyclodextrin used to enhance drug solubility. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("BETADEX SULFOBUTYL ETHER SODIUM", "gluten_free",
     "Sulfobutyl ether sodium salt of beta-cyclodextrin. Used to enhance solubility of poorly soluble drugs. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYL .GAMMA.-CYCLODEXTRIN", "gluten_free",
     "Hydroxypropyl ether of gamma-cyclodextrin. Same compound class as the beta variant. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYL .ALPHA.-CYCLODEXTRIN", "gluten_free",
     "Hydroxypropyl ether of alpha-cyclodextrin. Same compound class as the beta variant. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYL .BETA.-CYCLODEXTRIN", "gluten_free",
     "Hydroxypropyl ether of beta-cyclodextrin (same as HYDROXYPROPYL BETADEX, alternate naming). Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("SULFOBUTYLETHER .BETA.-CYCLODEXTRIN", "gluten_free",
     "Sulfobutyl ether of beta-cyclodextrin (same as BETADEX SULFOBUTYL ETHER SODIUM, alternate naming). Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("GAMMA CYCLODEXTRIN", "gluten_free",
     "Gamma-cyclodextrin. Cyclic oligosaccharide (8-glucose ring). Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYLBETADEX (0.58-0.68 MS)", "gluten_free",
     "Hydroxypropyl beta-cyclodextrin with degree of substitution 0.58-0.68. Same compound family as HYDROXYPROPYL BETADEX. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("ADRABETADEX", "gluten_free",
     "USP/INN name for a hydroxypropyl-beta-cyclodextrin variant used as an active in some formulations. Cyclodextrin family. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    (".BETA.-CYCLODEXTRIN SULFOBUTYL ETHER", "gluten_free",
     "Sulfobutyl ether of beta-cyclodextrin (alternate naming). Same compound as BETADEX SULFOBUTYL ETHER SODIUM. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("O-METHYL-.BETA.-CYCLODEXTRIN (1.8 METHYLS PER SACCHARIDE)", "gluten_free",
     "Methylated beta-cyclodextrin with average 1.8 methyl groups per glucose unit. Cyclodextrin family. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale).",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    ("HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE)", "gluten_free",
     "Hydroxypropyl beta-cyclodextrin with degree of substitution 0.6 hydroxypropyl groups per glucose unit. Cyclodextrin family. Interim gluten_free pending pharmacist consultation. Source: GIG 2019 (stale). Originally excluded as a keyword false positive — corrected to cyclodextrin classification.",
     "https://gluten.org/2019/10/17/medications-and-the-gluten-free-diet/", ""),

    # ========================================================================
    # GLUTEN_FREE — maltodextrin family extensions
    # ========================================================================

    ("ICODEXTRIN", "gluten_free",
     "Starch-derived glucose polymer (linear). Used as an osmotic agent in peritoneal dialysis solutions. Chemically related to maltodextrin (linear starch hydrolysate). Per NCA, maltodextrin is gluten free regardless of starting material because processing reduces gluten below 20 ppm. Same reasoning applies to icodextrin. Bulk catalog: 186 products.",
     "https://nationalceliac.org/ingredients-people-question/", ""),

    ("MALTODEXTRIN/VP COPOLYMER (1000 MPA.S)", "gluten_free",
     "Copolymer of maltodextrin and vinylpyrrolidone (VP). Maltodextrin is a linear starch hydrolysate flagged gluten_free per NCA. Vinylpyrrolidone is a synthetic monomer with no grain involvement. The '1000 MPA.S' specifies viscosity, not chemistry. Used as a film former. Bulk catalog: 2 products.",
     "https://nationalceliac.org/ingredients-people-question/", ""),

    # ========================================================================
    # GLUTEN_FREE — keyword false positives
    # ========================================================================
    # These excipient strings matched our gluten-adjacent keyword search but
    # are NOT grain-derived. Added to the validation table per Option A so the
    # table is the single source of truth — re-running build_gluten_excipient_list.py
    # will not require re-excluding these by hand.

    # --- Glycolate esters (matched 'glycolate' but not starch glycolate) ---

    ("SODIUM GLYCOLATE", "gluten_free",
     "Keyword false positive — sodium salt of glycolic acid (an alpha-hydroxy acid). Matched 'glycolate' keyword but is unrelated to sodium STARCH glycolate. Not grain-derived.",
     URL_FDA_IIG, ""),

    ("ETHYL GLYCOLATE", "gluten_free",
     "Keyword false positive — ester of glycolic acid. Not grain-derived.",
     URL_FDA_IIG, ""),

    ("ALLYL AMYL GLYCOLATE", "gluten_free",
     "Keyword false positive — fragrance compound (ester of glycolic acid). Not grain-derived.",
     URL_FDA_IIG, ""),

    ("BUTYL GLYCOLATE", "gluten_free",
     "Keyword false positive — butyl ester of glycolic acid. Not grain-derived.",
     URL_FDA_IIG, ""),

    ("CEFATRIZINE PROPYLENE GLYCOLATE", "gluten_free",
     "Keyword false positive — cephalosporin antibiotic salt (propylene glycolate form). Not grain-derived.",
     URL_FDA_IIG, ""),

    # --- Methyl glucose esters (matched 'glucose' but synthetic emulsifiers) ---

    ("PEG-120 METHYL GLUCOSE DIOLEATE", "gluten_free",
     "Keyword false positive — synthetic cosmetic emulsifier. Methyl glucoside esterified with oleic acid and modified with PEG. The 'glucose' in the name refers to the glucoside backbone, not grain-derived glucose. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("METHYL GLUCOSE SESQUISTEARATE", "gluten_free",
     "Keyword false positive — synthetic cosmetic emulsifier (methyl glucoside esterified with stearic acid). Not gluten-related.",
     URL_FDA_IIG, ""),

    ("PEG-20 METHYL GLUCOSE SESQUISTEARATE", "gluten_free",
     "Keyword false positive — PEG-20 modified methyl glucose sesquistearate. Synthetic cosmetic emulsifier. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("METHYL GLUCOSE DIOLEATE", "gluten_free",
     "Keyword false positive — synthetic cosmetic emulsifier. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("PPG-20 METHYL GLUCOSE ETHER", "gluten_free",
     "Keyword false positive — synthetic cosmetic emulsifier (PPG-modified methyl glucoside). Not gluten-related.",
     URL_FDA_IIG, ""),

    ("PPG-20 METHYL GLUCOSE ETHER DISTEARATE", "gluten_free",
     "Keyword false positive — synthetic cosmetic emulsifier. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("METHYL GLUCOSE", "gluten_free",
     "Keyword false positive — synthetic methylated sugar derivative. Not gluten-related.",
     URL_FDA_IIG, ""),

    # --- Glucose biochemicals (matched 'glucose' but lab/biochemical reagents) ---

    ("GLUCOSE OXIDASE", "gluten_free",
     "Keyword false positive — enzyme protein from Aspergillus niger fungus, not a sugar. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("DIPOTASSIUM GLUCOSE-6-PHOSPHATE", "gluten_free",
     "Keyword false positive — phosphorylated sugar biochemical. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("PSEUDOMONAS GLUCOSE FERMENTATION RHAMNOLIPIDS", "gluten_free",
     "Keyword false positive — biosurfactant from Pseudomonas fermentation of glucose. The product is a rhamnolipid, not a glucose-containing compound. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("2,3 DI-O-METHYL-D-GLUCOSE", "gluten_free",
     "Keyword false positive — synthetic methylated sugar derivative. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("GLUCOSE-6-PHOSPHATE", "gluten_free",
     "Keyword false positive — phosphorylated sugar biochemical reagent. Not gluten-related.",
     URL_FDA_IIG, ""),

    ("GLUCOSE PENTAACETATE", "gluten_free",
     "Keyword false positive — chemically derivatized glucose (acetylated). Not gluten-related.",
     URL_FDA_IIG, ""),

    ("GLUCOSE 1,6-BISPHOSPHATE", "gluten_free",
     "Keyword false positive — bisphosphorylated sugar biochemical. Not gluten-related.",
     URL_FDA_IIG, ""),

    (".ALPHA.-GLUCOSE-1-PHOSPHATE DIPOTASSIUM DIHYDRATE", "gluten_free",
     "Keyword false positive — alpha-glucose-1-phosphate biochemical (potassium salt, dihydrate). Not gluten-related.",
     URL_FDA_IIG, ""),

    # --- Silicone "gum" ---

    ("DIMETHICONOL GUM", "gluten_free",
     "Keyword false positive — silicone polymer (high molecular weight dimethicone). 'Gum' refers to physical texture, not a plant gum. Not gluten-related.",
     URL_FDA_IIG, ""),
]


def main():
    print("Building data/fullcatalog/gluten_validation.csv")
    print()

    # Step 1: get bulk catalog counts
    print("Counting excipients in bulk catalog...")
    bulk_counts = get_bulk_counts()
    print(f"  {len(bulk_counts):,} unique excipient strings")
    print()

    # Step 2: load pilot entries, apply bulk-revision overrides, then annotate counts
    print("Loading and updating pilot entries...")
    pilot_entries = load_pilot_entries()
    for entry in pilot_entries:
        term = entry["fda_term"].strip().upper()
        bulk_count = bulk_counts.get(term, 0)
        apply_pilot_override(entry)  # apply any override BEFORE rationale annotation
        update_pilot_rationale(entry, bulk_count)
    overridden = sum(1 for e in pilot_entries
                     if e["fda_term"].strip().upper() in PILOT_OVERRIDES)
    print(f"  {len(pilot_entries)} pilot entries loaded and annotated "
          f"({overridden} with bulk-revision overrides)")
    print()

    # Step 3: convert new entries to dict format
    print("Adding new entries...")
    new_entry_dicts = []
    flag_counts = Counter()
    for term, flag, rationale, url, eu in NEW_ENTRIES:
        bulk_count = bulk_counts.get(term.upper(), 0)
        annotated_rationale = rationale + f" Bulk catalog: {bulk_count:,} products."
        new_entry_dicts.append({
            "fda_term": term,
            "source": "dailymed_bulk",
            "flag_decision": flag,
            "rationale": annotated_rationale,
            "source_url": url,
            "eu_equivalent": eu,
        })
        flag_counts[flag] += 1
    print(f"  {len(new_entry_dicts)} new entries added")
    print(f"  Flag distribution: {dict(flag_counts)}")
    print()

    # Step 4: write combined CSV
    print(f"Writing {OUTPUT_CSV}...")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["fda_term", "source", "flag_decision", "rationale", "source_url", "eu_equivalent"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for entry in pilot_entries:
            writer.writerow({k: entry.get(k, "") for k in fieldnames})
        for entry in new_entry_dicts:
            writer.writerow(entry)

    total = len(pilot_entries) + len(new_entry_dicts)
    print(f"  Total entries: {total}")

    # Final flag distribution
    print()
    print("Final flag distribution:")
    final_flags = Counter()
    for e in pilot_entries:
        final_flags[e["flag_decision"]] += 1
    for e in new_entry_dicts:
        final_flags[e["flag_decision"]] += 1
    for flag, count in final_flags.most_common():
        print(f"  {flag}: {count}")


if __name__ == "__main__":
    main()
