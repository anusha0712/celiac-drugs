"""
Pull acetaminophen and ibuprofen product data from DailyMed.
Extracts ALL available fields from SPL XML for gluten excipient analysis.

Strategy:
1. Use DailyMed API to get all set_ids for products containing acetaminophen/ibuprofen
2. Cache set_id list to disk so Step 1 never re-runs unnecessarily
3. Fetch each product's SPL XML from DailyMed, caching raw XML to disk
4. Parse structured XML — extract every available field
5. If interrupted, resume from where we left off (skip already-cached XMLs)

Rate limiting:
- Adaptive delay: starts at 0.5s, backs off to 5s+ on 429s, recovers gradually
- Exponential backoff on retries
- Progress saved continuously — safe to Ctrl+C and restart

Scope: All products containing acetaminophen or ibuprofen (single + combo).
Excludes: injectables (filtered post-extraction by route).
Source: 100% DailyMed.
"""

import csv
import json
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import sys
import os
import hashlib

PROJECT_DIR = "/Users/anushasubramanian/Desktop/Projects/freelance"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "dailymed_raw.csv")
CACHE_DIR = os.path.join(PROJECT_DIR, "data", ".xml_cache")
SETID_CACHE_FILE = os.path.join(PROJECT_DIR, "data", ".setid_cache.json")

# DailyMed API endpoints
LIST_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
SPL_XML_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"

# HL7 SPL namespace
NS = {"hl7": "urn:hl7-org:v3"}

# Route codes to exclude (injectables)
INJECTABLE_ROUTE_CODES = {
    "C38276",  # INTRAVENOUS
    "C38277",  # INTRAMUSCULAR
    "C38278",  # SUBCUTANEOUS
    "C38279",  # INTRADERMAL
    "C38280",  # INTRATHECAL
}

PAGESIZE = 100

# Adaptive rate limiting
MIN_DELAY = 0.5
MAX_DELAY = 10.0
NORMAL_DELAY = 0.5
current_delay = NORMAL_DELAY


def adaptive_sleep():
    """Sleep with adaptive delay. Called between requests."""
    global current_delay
    time.sleep(current_delay)
    # Gradually recover toward normal delay
    if current_delay > NORMAL_DELAY:
        current_delay = max(NORMAL_DELAY, current_delay * 0.95)


def back_off():
    """Increase delay after rate limiting or errors."""
    global current_delay
    current_delay = min(MAX_DELAY, current_delay * 2)
    print(f"  [Rate limit] Delay increased to {current_delay:.1f}s")


def fetch_url(url, accept=None, retries=5):
    """Fetch URL with exponential backoff and adaptive rate limiting."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            if accept:
                req.add_header("Accept", accept)
            req.add_header("User-Agent", "GlutenExcipientStudy/1.0 (academic research)")
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                back_off()
                wait = min(60, 5 * (2 ** attempt))
                print(f"  429 Too Many Requests — waiting {wait}s (attempt {attempt+1}/{retries})")
                time.sleep(wait)
            elif e.code == 404:
                return None
            elif e.code >= 500:
                wait = 3 * (2 ** attempt)
                print(f"  Server error {e.code} — waiting {wait}s (attempt {attempt+1}/{retries})")
                time.sleep(wait)
            else:
                print(f"  HTTP {e.code} for {url[:80]} (attempt {attempt+1}/{retries})")
                time.sleep(2 * (attempt + 1))
        except urllib.error.URLError as e:
            wait = 5 * (2 ** attempt)
            print(f"  Connection error: {e.reason} — waiting {wait}s (attempt {attempt+1}/{retries})")
            time.sleep(wait)
        except Exception as e:
            wait = 3 * (2 ** attempt)
            print(f"  Unexpected error: {e} — waiting {wait}s (attempt {attempt+1}/{retries})")
            time.sleep(wait)

    print(f"  FAILED after {retries} attempts: {url[:80]}")
    return None


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
# Step 1: Collect set_ids (with disk cache)
# ============================================================

def collect_set_ids(drug_name):
    """Collect all set_ids for a given drug name from DailyMed API."""
    set_ids = []
    page = 1
    total = None

    while True:
        url = f"{LIST_URL}?drug_name={drug_name}&page={page}&pagesize={PAGESIZE}"
        raw = fetch_url(url)

        if raw is None:
            print(f"  WARNING: Failed to fetch page {page} for {drug_name}, stopping pagination")
            break

        data = json.loads(raw.decode())

        if total is None:
            total = data.get("metadata", {}).get("total_elements", 0)
            total_pages = data.get("metadata", {}).get("total_pages", 0)
            print(f"  {drug_name}: {total} products across {total_pages} pages")

        results = data.get("data", [])
        if not results:
            break

        for item in results:
            setid = item.get("setid", "")
            title = item.get("title", "")
            if setid:
                set_ids.append({"setid": setid, "title": title})

        print(f"    Page {page}: {len(results)} results (cumulative: {len(set_ids)})")

        page += 1
        if total and page > (total // PAGESIZE) + 2:
            break

        adaptive_sleep()

    return set_ids


def collect_all_set_ids():
    """Collect set_ids for both drugs, with disk caching."""
    # Check cache
    if os.path.exists(SETID_CACHE_FILE):
        with open(SETID_CACHE_FILE, "r") as f:
            cached = json.load(f)
        print(f"  Loaded {len(cached)} cached set_ids from {SETID_CACHE_FILE}")
        return cached

    print("  No cache found — fetching from DailyMed API...")

    acetaminophen_ids = collect_set_ids("acetaminophen")
    time.sleep(2)  # pause between drug queries
    ibuprofen_ids = collect_set_ids("ibuprofen")

    # Deduplicate
    all_items = {}
    for item in acetaminophen_ids:
        all_items[item["setid"]] = {"category": "analgesic_antipyretic", "title": item["title"]}
    for item in ibuprofen_ids:
        if item["setid"] not in all_items:
            all_items[item["setid"]] = {"category": "nsaid", "title": item["title"]}

    print(f"\n  Total unique set_ids: {len(all_items)}")
    print(f"  Acetaminophen: {len(acetaminophen_ids)}")
    print(f"  Ibuprofen: {len(ibuprofen_ids)}")
    print(f"  Overlap (deduplicated): {len(acetaminophen_ids) + len(ibuprofen_ids) - len(all_items)}")

    # Save cache
    with open(SETID_CACHE_FILE, "w") as f:
        json.dump(all_items, f)
    print(f"  Cached to {SETID_CACHE_FILE}")

    return all_items


# ============================================================
# Step 2: Fetch XMLs (with disk cache per product)
# ============================================================

def get_xml_cache_path(setid):
    """Get the cache file path for a given set_id."""
    return os.path.join(CACHE_DIR, f"{setid}.xml")


def fetch_spl_xml(setid):
    """Fetch SPL XML, using disk cache if available."""
    cache_path = get_xml_cache_path(setid)

    # Check cache
    if os.path.exists(cache_path):
        try:
            return ET.parse(cache_path)
        except ET.ParseError:
            os.remove(cache_path)  # corrupted cache, re-fetch

    # Fetch from DailyMed — do NOT send Accept header (406 error with application/xml)
    url = SPL_XML_URL.format(setid=setid)
    raw = fetch_url(url)

    if raw is None:
        return None

    # Save to cache
    with open(cache_path, "wb") as f:
        f.write(raw)

    # Parse
    try:
        return ET.ElementTree(ET.fromstring(raw))
    except ET.ParseError as e:
        print(f"  XML parse error for {setid}: {e}")
        os.remove(cache_path)
        return None


# ============================================================
# Step 3: Parse XML
# ============================================================

def parse_spl_xml(tree, setid, category):
    """Parse an SPL XML document to extract ALL available product data."""
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

        # Skip injectables
        if product["route_code"] in INJECTABLE_ROUTE_CODES:
            continue

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

        # Physical characteristics — helper
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
        product["category"] = category
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
# Main
# ============================================================

def main():
    print("=" * 60)
    print("DailyMed Data Pull — Gluten Excipient Analysis")
    print("Source: 100% DailyMed")
    print("=" * 60)
    print(f"Cache dir: {CACHE_DIR}")
    print(f"Output: {OUTPUT_FILE}")

    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Step 1: Collect all set_ids (cached)
    print("\n" + "=" * 60)
    print("Step 1: Collecting set_ids")
    print("=" * 60)
    all_items = collect_all_set_ids()
    total = len(all_items)

    # Count how many XMLs are already cached
    already_cached = sum(1 for setid in all_items if os.path.exists(get_xml_cache_path(setid)))
    to_fetch = total - already_cached
    print(f"\n  Already cached: {already_cached}/{total}")
    print(f"  Remaining to fetch: {to_fetch}")
    if to_fetch > 0:
        est_minutes = (to_fetch * NORMAL_DELAY) / 60
        print(f"  Estimated time: ~{est_minutes:.0f} minutes (at {NORMAL_DELAY}s/request)")

    # Step 2: Fetch and parse each SPL XML
    print("\n" + "=" * 60)
    print("Step 2: Fetching & parsing SPL XMLs")
    print("=" * 60)

    all_products = []
    errors = []
    fetch_count = 0
    cache_hit_count = 0
    start_time = time.time()

    for i, (setid, info) in enumerate(all_items.items(), 1):
        if i % 200 == 0 or i == 1 or i == total:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / rate if rate > 0 else 0
            print(f"  [{i}/{total}] {len(all_products)} products | "
                  f"{cache_hit_count} cache hits | {fetch_count} fetched | "
                  f"{len(errors)} errors | "
                  f"~{remaining/60:.0f}m remaining | "
                  f"delay={current_delay:.1f}s")

        # Check if already cached
        was_cached = os.path.exists(get_xml_cache_path(setid))

        tree = fetch_spl_xml(setid)

        if tree is None:
            errors.append(setid)
            continue

        if was_cached:
            cache_hit_count += 1
        else:
            fetch_count += 1
            adaptive_sleep()  # only sleep after actual network requests

        try:
            products = parse_spl_xml(tree, setid, info["category"])
            if products:
                all_products.extend(products)
            else:
                errors.append(setid)
        except Exception as e:
            print(f"  Error parsing {setid}: {e}")
            errors.append(setid)

        # Periodic progress save (every 500 products) — in case of crash
        if len(all_products) > 0 and len(all_products) % 500 < len(products) if products else False:
            _write_csv(all_products, OUTPUT_FILE + ".partial")

    # Step 3: Write final CSV
    print(f"\n" + "=" * 60)
    print("Step 3: Writing final CSV")
    print("=" * 60)
    _write_csv(all_products, OUTPUT_FILE)

    # Clean up partial file if it exists
    partial = OUTPUT_FILE + ".partial"
    if os.path.exists(partial):
        os.remove(partial)

    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"DONE in {elapsed/60:.1f} minutes")
    print(f"{'=' * 60}")
    print(f"Total products written: {len(all_products)}")

    cats = {}
    for p in all_products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    print(f"  Single-ingredient: {sum(1 for p in all_products if p['single_or_combo'] == 'single')}")
    print(f"  Combo products: {sum(1 for p in all_products if p['single_or_combo'] == 'combo')}")
    print(f"  With inactive ingredients: {sum(1 for p in all_products if p['excipients_raw'])}")
    print(f"  Active marketing: {sum(1 for p in all_products if p.get('marketing_status') == 'active')}")
    print(f"  Network fetches: {fetch_count}")
    print(f"  Cache hits: {cache_hit_count}")
    print(f"  Errors/skipped: {len(errors)}")

    # Dosage form breakdown
    forms = {}
    for p in all_products:
        f = p["dosage_form"] or "UNKNOWN"
        forms[f] = forms.get(f, 0) + 1
    print(f"\nDosage forms:")
    for form, count in sorted(forms.items(), key=lambda x: -x[1])[:15]:
        print(f"  {form}: {count}")

    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"XML cache: {CACHE_DIR} ({already_cached + fetch_count} files)")

    if errors:
        error_file = os.path.join(PROJECT_DIR, "data", "pull_errors.txt")
        with open(error_file, "w") as ef:
            ef.write("\n".join(errors))
        print(f"Error set_ids ({len(errors)}): {error_file}")


def _write_csv(products, filepath):
    """Write products to CSV."""
    fieldnames = [
        # Core identification
        "drug_name", "generic_name", "brand_generic", "category",
        # Formulation
        "dosage_form", "dosage_form_code", "route", "route_code",
        # Active ingredients
        "active_ingredients", "active_ingredient_uniis", "active_ingredient_strengths",
        "active_ingredient_count", "single_or_combo",
        # Inactive ingredients (the focus of our analysis)
        "excipients_raw", "excipient_uniis", "excipient_count",
        # Regulatory
        "ndc_code", "package_ndc", "approval_number", "approval_type",
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

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(products)

    print(f"  Wrote {len(products)} rows to {filepath}")


if __name__ == "__main__":
    main()
