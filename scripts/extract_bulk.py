"""
Extract all DailyMed bulk download ZIPs into a structured CSV.

Reads local ZIP files from bulk-data/ directory (downloaded from DailyMed's
full release archives). Each ZIP contains one SPL XML label plus images.
Extracts all structured fields from the XML into a flat CSV.

Input:  bulk-data/{human-otc,human-prescription,homeopathic,other}/*/*.zip
Output: data/dailymed_bulk_raw.csv
Errors: data/extract_errors.txt

Replicable: run on any DailyMed bulk download with the same folder structure.
No network calls. No filtering — extract everything, filter in analysis.
"""

import csv
import os
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BULK_DATA_DIR = os.path.join(PROJECT_DIR, "bulk-data")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "dailymed_bulk_raw.csv")
ERROR_FILE = os.path.join(PROJECT_DIR, "data", "extract_errors.txt")

# HL7 SPL namespace
NS = {"hl7": "urn:hl7-org:v3"}

# Map top-level folder names to bulk_category values
FOLDER_CATEGORY_MAP = {
    "human-otc": "human_otc",
    "human-prescription": "human_prescription",
    "homeopathic": "homeopathic",
    "other": "other",
}

FIELDNAMES = [
    # Sourcing metadata
    "bulk_category", "source_zip",
    # Core identification
    "drug_name", "generic_name", "brand_generic",
    # Formulation
    "dosage_form", "dosage_form_code", "route", "route_code",
    # Active ingredients
    "active_ingredients", "active_ingredient_uniis", "active_ingredient_strengths",
    "active_ingredient_count", "single_or_combo",
    # Inactive ingredients
    "excipients_raw", "excipient_uniis", "excipient_count",
    # Regulatory
    "ndc_code", "package_ndc", "approval_number", "approval_type",
    "dea_schedule",
    # Marketing
    "marketing_status", "marketing_start_date", "marketing_end_date",
    # Manufacturer
    "manufacturer", "manufacturer_duns",
    # Physical characteristics
    "package_form", "package_quantity",
    "color", "shape", "imprint", "score", "size_mm", "flavor",
    # Combination product
    "combination_product_type",
    # Document metadata
    "document_id", "document_type", "document_type_code",
    "effective_date", "spl_version",
    # DailyMed reference
    "set_id", "dailymed_url",
]


# ============================================================
# Helpers (from pull_dailymed.py)
# ============================================================

def get_text(element):
    """Safely get text from an XML element."""
    if element is not None and element.text:
        return element.text.strip()
    return ""


def get_attr(element, attr, default=""):
    """Safely get attribute from an XML element."""
    if element is not None:
        return element.get(attr, default)
    return default


# ============================================================
# ZIP discovery
# ============================================================

def discover_zips(bulk_dir):
    """Walk bulk-data/ tree, yield (zip_path, bulk_category) for each ZIP.

    Expected structure:
        bulk-data/human-otc/otc-1/*.zip
        bulk-data/human-prescription/prescription-1/*.zip
        bulk-data/homeopathic/homeopathic-1/*.zip
        bulk-data/other/other-1/*.zip
    """
    for category_folder in sorted(os.listdir(bulk_dir)):
        category_path = os.path.join(bulk_dir, category_folder)
        if not os.path.isdir(category_path):
            continue
        bulk_category = FOLDER_CATEGORY_MAP.get(category_folder)
        if bulk_category is None:
            print(f"  WARNING: Unknown folder '{category_folder}' — skipping")
            continue

        for subfolder in sorted(os.listdir(category_path)):
            subfolder_path = os.path.join(category_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            for filename in sorted(os.listdir(subfolder_path)):
                if filename.endswith(".zip"):
                    yield os.path.join(subfolder_path, filename), bulk_category


def extract_xml_from_zip(zip_path):
    """Open ZIP in memory, find the .xml file, return parsed ElementTree."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        xml_names = [n for n in zf.namelist() if n.endswith(".xml")]
        if not xml_names:
            raise ValueError("No XML file found in ZIP")
        with zf.open(xml_names[0]) as xf:
            return ET.parse(xf)


def extract_set_id_from_filename(zip_filename):
    """Extract set_id UUID from ZIP filename like '20251019_b60df498-07db-500b-e053-2a95a90aff6a.zip'."""
    base = os.path.splitext(zip_filename)[0]  # remove .zip
    parts = base.split("_", 1)
    if len(parts) == 2:
        return parts[1]
    return ""


# ============================================================
# XML parsing (adapted from pull_dailymed.py parse_spl_xml)
# ============================================================

def parse_spl_xml(tree, setid):
    """Parse an SPL XML document to extract all available product data.

    Returns a list of dicts (one per NDC/product in the label).
    Adapted from pull_dailymed.py — no injectable filtering, no category param,
    adds DEA schedule extraction.
    """
    root = tree.getroot()

    # --- Document-level fields ---
    doc_id = get_attr(root.find("hl7:id", NS), "root")
    doc_type_el = root.find("hl7:code", NS)
    doc_type_code = get_attr(doc_type_el, "code")
    doc_type = get_attr(doc_type_el, "displayName")
    doc_title = get_text(root.find("hl7:title", NS))
    effective_date = get_attr(root.find("hl7:effectiveTime", NS), "value")
    version = get_attr(root.find("hl7:versionNumber", NS), "value")

    # --- Manufacturer ---
    mfr_el = root.find(".//hl7:representedOrganization/hl7:name", NS)
    manufacturer = get_text(mfr_el)
    mfr_id_el = root.find(".//hl7:representedOrganization/hl7:id", NS)
    manufacturer_duns = get_attr(mfr_id_el, "extension")

    # --- Approval info ---
    approval_el = root.find(".//hl7:approval", NS)
    approval_number = ""
    approval_type = ""
    if approval_el is not None:
        approval_id = approval_el.find("hl7:id", NS)
        approval_number = get_attr(approval_id, "extension")
        approval_code_el = approval_el.find("hl7:code", NS)
        approval_type = get_attr(approval_code_el, "displayName")

    # --- DEA schedule (new) ---
    dea_schedule = ""
    policy_el = root.find(".//{urn:hl7-org:v3}policy/{urn:hl7-org:v3}code")
    if policy_el is not None:
        dea_schedule = get_attr(policy_el, "displayName")

    # setId from XML as cross-check (prefer filename-derived)
    xml_set_id = get_attr(root.find("hl7:setId", NS), "root")
    if not setid:
        setid = xml_set_id

    # --- Products (there can be multiple per document) ---
    products = []

    for mp in root.findall(".//hl7:manufacturedProduct/hl7:manufacturedProduct", NS):
        product = {}

        # NDC code
        product["ndc_code"] = get_attr(mp.find("hl7:code", NS), "code")

        # Drug name
        product["drug_name"] = get_text(mp.find("hl7:name", NS)) or doc_title

        # Dosage form
        form_el = mp.find("hl7:formCode", NS)
        product["dosage_form"] = get_attr(form_el, "displayName")
        product["dosage_form_code"] = get_attr(form_el, "code")

        # Generic medicine name
        generic_el = mp.find(".//hl7:asEntityWithGeneric/hl7:genericMedicine/hl7:name", NS)
        product["generic_name"] = get_text(generic_el)

        # Route — search in consumedIn elements
        route_el = None
        for consumed in root.findall(".//hl7:consumedIn/hl7:substanceAdministration/hl7:routeCode", NS):
            route_el = consumed
            break
        product["route"] = get_attr(route_el, "displayName")
        product["route_code"] = get_attr(route_el, "code")

        # Active ingredients (with UNII codes and strengths)
        active_ingredients = []
        active_ingredient_uniis = []
        active_ingredient_strengths = []
        for ing in mp.findall("hl7:ingredient[@classCode='ACTIB']", NS):
            sub = ing.find("hl7:ingredientSubstance/hl7:name", NS)
            unii = ing.find("hl7:ingredientSubstance/hl7:code", NS)
            name = get_text(sub)
            if name:
                active_ingredients.append(name)
                active_ingredient_uniis.append(get_attr(unii, "code"))
            num_el = ing.find("hl7:quantity/hl7:numerator", NS)
            den_el = ing.find("hl7:quantity/hl7:denominator", NS)
            if num_el is not None:
                strength = f"{get_attr(num_el, 'value')} {get_attr(num_el, 'unit')}"
                if den_el is not None:
                    strength += f" / {get_attr(den_el, 'value')} {get_attr(den_el, 'unit')}"
                active_ingredient_strengths.append(strength)

        for code in ["ACTIM", "ACTIR", "ACTI"]:
            for ing in mp.findall(f"hl7:ingredient[@classCode='{code}']", NS):
                sub = ing.find("hl7:ingredientSubstance/hl7:name", NS)
                unii = ing.find("hl7:ingredientSubstance/hl7:code", NS)
                name = get_text(sub)
                if name:
                    active_ingredients.append(name)
                    active_ingredient_uniis.append(get_attr(unii, "code"))

        product["active_ingredients"] = "; ".join(active_ingredients)
        product["active_ingredient_uniis"] = "; ".join(active_ingredient_uniis)
        product["active_ingredient_strengths"] = "; ".join(active_ingredient_strengths)
        product["active_ingredient_count"] = len(active_ingredients)
        product["single_or_combo"] = "single" if len(active_ingredients) <= 1 else "combo"

        # Inactive ingredients (with UNII codes)
        inactive_ingredients = []
        inactive_ingredient_uniis = []
        for ing in mp.findall("hl7:ingredient[@classCode='IACT']", NS):
            sub = ing.find("hl7:ingredientSubstance/hl7:name", NS)
            unii = ing.find("hl7:ingredientSubstance/hl7:code", NS)
            name = get_text(sub)
            if name:
                inactive_ingredients.append(name)
                inactive_ingredient_uniis.append(get_attr(unii, "code"))

        product["excipients_raw"] = "; ".join(inactive_ingredients)
        product["excipient_uniis"] = "; ".join(inactive_ingredient_uniis)
        product["excipient_count"] = len(inactive_ingredients)

        # Packaging info
        pkg_ndc_el = mp.find(".//hl7:asContent/hl7:containerPackagedProduct/hl7:code", NS)
        product["package_ndc"] = get_attr(pkg_ndc_el, "code")
        pkg_form_el = mp.find(".//hl7:asContent/hl7:containerPackagedProduct/hl7:formCode", NS)
        product["package_form"] = get_attr(pkg_form_el, "displayName")
        pkg_qty_num = mp.find(".//hl7:asContent/hl7:quantity/hl7:numerator", NS)
        if pkg_qty_num is not None:
            product["package_quantity"] = f"{get_attr(pkg_qty_num, 'value')} {get_attr(pkg_qty_num, 'unit')}"
        else:
            product["package_quantity"] = ""

        # Marketing status
        mkt_status_el = mp.find(".//hl7:asContent/hl7:subjectOf/hl7:marketingAct/hl7:statusCode", NS)
        product["marketing_status"] = get_attr(mkt_status_el, "code")
        mkt_start_el = mp.find(".//hl7:asContent/hl7:subjectOf/hl7:marketingAct/hl7:effectiveTime/hl7:low", NS)
        product["marketing_start_date"] = get_attr(mkt_start_el, "value")
        mkt_end_el = mp.find(".//hl7:asContent/hl7:subjectOf/hl7:marketingAct/hl7:effectiveTime/hl7:high", NS)
        product["marketing_end_date"] = get_attr(mkt_end_el, "value")

        # Combination product type
        for char in mp.findall(".//hl7:characteristic", NS):
            code_el = char.find("hl7:code", NS)
            if get_attr(code_el, "code") == "SPLCMBPRDTP":
                val_el = char.find("hl7:value", NS)
                product["combination_product_type"] = get_attr(val_el, "displayName")
                break
        else:
            product["combination_product_type"] = ""

        # Physical characteristics
        def get_characteristic(code_name):
            for cs in root.findall(".//hl7:characteristic[@classCode='OBS']", NS):
                ce = cs.find("hl7:code", NS)
                if get_attr(ce, "code") == code_name:
                    ve = cs.find("hl7:value", NS)
                    if ve is not None:
                        return get_attr(ve, "displayName") or get_attr(ve, "value") or get_text(ve)
            return ""

        product["flavor"] = get_characteristic("SPLFLAVOR")
        product["color"] = get_characteristic("SPLCOLOR")
        product["shape"] = get_characteristic("SPLSHAPE")
        product["imprint"] = get_characteristic("SPLIMPRINT")
        product["score"] = get_characteristic("SPLSCORE")
        product["size_mm"] = get_characteristic("SPLSIZE")

        # Document-level fields
        product["document_id"] = doc_id
        product["document_type"] = doc_type
        product["document_type_code"] = doc_type_code
        product["effective_date"] = effective_date
        product["set_id"] = setid
        product["spl_version"] = version
        product["manufacturer"] = manufacturer
        product["manufacturer_duns"] = manufacturer_duns
        product["approval_number"] = approval_number
        product["approval_type"] = approval_type
        product["dea_schedule"] = dea_schedule
        product["dailymed_url"] = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"

        # Brand vs generic determination
        if approval_number.startswith("ANDA"):
            product["brand_generic"] = "generic"
        elif approval_number.startswith("NDA") or approval_number.startswith("BLA"):
            product["brand_generic"] = "brand"
        else:
            product["brand_generic"] = "otc_monograph"

        products.append(product)

    return products


# ============================================================
# Main pipeline
# ============================================================

def main():
    print("=" * 60)
    print("DailyMed Bulk Extraction")
    print(f"Input:  {BULK_DATA_DIR}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)

    if not os.path.isdir(BULK_DATA_DIR):
        print(f"ERROR: Bulk data directory not found: {BULK_DATA_DIR}")
        sys.exit(1)

    # Discover all ZIPs
    print("\nDiscovering ZIP files...")
    zip_list = list(discover_zips(BULK_DATA_DIR))
    total_zips = len(zip_list)
    print(f"  Found {total_zips:,} ZIP files")

    # Process
    all_products = []
    errors = []
    start_time = time.time()

    for i, (zip_path, bulk_category) in enumerate(zip_list):
        zip_filename = os.path.basename(zip_path)

        try:
            tree = extract_xml_from_zip(zip_path)
            setid = extract_set_id_from_filename(zip_filename)
            products = parse_spl_xml(tree, setid)

            for p in products:
                p["bulk_category"] = bulk_category
                p["source_zip"] = zip_filename

            all_products.extend(products)

        except Exception as e:
            errors.append(f"{zip_path}\t{type(e).__name__}: {e}")

        # Progress
        if (i + 1) % 1000 == 0 or (i + 1) == total_zips:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (total_zips - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1:>7,}/{total_zips:,}] "
                  f"{len(all_products):,} products | "
                  f"{len(errors):,} errors | "
                  f"{rate:.0f} zips/sec | "
                  f"~{remaining/60:.0f}m remaining")

    # Write CSV
    print(f"\nWriting {len(all_products):,} rows to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_products)
    print(f"  Done.")

    # Write errors
    if errors:
        with open(ERROR_FILE, "w", encoding="utf-8") as f:
            for err in errors:
                f.write(err + "\n")
        print(f"\n  {len(errors):,} errors logged to {ERROR_FILE}")
    else:
        print(f"\n  No errors.")

    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"COMPLETE")
    print(f"  ZIPs processed: {total_zips:,}")
    print(f"  Products extracted: {len(all_products):,}")
    print(f"  Errors: {len(errors):,} ({100*len(errors)/total_zips:.2f}%)")
    print(f"  Time: {elapsed/60:.1f} minutes")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
