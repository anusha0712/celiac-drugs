#!/usr/bin/env python3
"""
spl_label_parser.py — shared SPL XML parser for contraindication /
warning analysis.

Handles BOTH Rx labels and OTC Drug Facts labels. Covers section codes
from the HL7 SPL Implementation Guide (https://www.hl7.org/documentcenter/
public/standards/v3/SPL_R8_March_2025.pdf) and LOINC registry
(https://loinc.org).

Rx-style sections:
  34066-1  BOXED WARNING SECTION
  34070-3  CONTRAINDICATIONS SECTION
  34071-1  WARNINGS SECTION
  43685-7  WARNINGS AND PRECAUTIONS SECTION
  34077-9  ADVERSE REACTIONS SECTION

OTC Drug Facts sections (HL7 SPL IG Appendix: OTC Monograph):
  42229-5  SPL UNCLASSIFIED (used for Allergy Alert, Reye's Syndrome
           alert, Drug Facts header — check section <title>)
  50570-1  DO NOT USE SECTION
  50569-3  ASK DOCTOR BEFORE USE IF YOU HAVE SECTION
  50568-5  ASK DOCTOR OR PHARMACIST BEFORE USE SECTION
  50567-7  WHEN USING THIS PRODUCT SECTION
  50566-9  STOP USE AND ASK DOCTOR IF SECTION

Used by analyze_dpi_labels.py, analyze_carmine_labels.py,
analyze_peg_labels.py.
"""

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Optional

BASE_DIR = Path(__file__).parent.parent
BULK_DIR = BASE_DIR / "bulk-data"
INDEX_CACHE = BASE_DIR / "bulk-data" / ".setid_zip_index.txt"

SPL_NS = "{urn:hl7-org:v3}"

# LOINC codes that commonly contain allergen / warning language
# (Rx + OTC Drug Facts). See HL7 SPL IG.
WARNING_SECTION_CODES = {
    # Rx labels
    "34066-1": "BOXED WARNING",
    "34070-3": "CONTRAINDICATIONS",
    "34071-1": "WARNINGS",
    "43685-7": "WARNINGS AND PRECAUTIONS",
    "34077-9": "ADVERSE REACTIONS",
    # OTC Drug Facts
    "50570-1": "DO NOT USE",
    "50569-3": "ASK DOCTOR BEFORE USE IF YOU HAVE",
    "50568-5": "ASK DOCTOR OR PHARMACIST BEFORE USE",
    "50567-7": "WHEN USING THIS PRODUCT",
    "50566-9": "STOP USE AND ASK DOCTOR IF",
    # Title-gated: 42229-5 is SPL unclassified; include only when title
    # says "Allergy alert" or similar.
    "42229-5": "SPL UNCLASSIFIED (title-gated)",
}

# Precedence order: match in this priority (first match wins)
WARNING_PRECEDENCE = [
    ("34070-3", "section_4_contraindication"),
    ("34066-1", "boxed_warning"),
    ("43685-7", "section_5_warning"),
    ("34071-1", "section_5_warning"),  # older Rx / OTC Warnings
    ("42229-5", "otc_allergy_alert"),   # title-gated below
    ("50570-1", "otc_do_not_use"),
    ("50569-3", "otc_ask_doctor"),
    ("50568-5", "otc_ask_doctor"),
    ("34077-9", "adverse_reactions"),
]

# Title patterns for the title-gated 42229-5 sections
OTC_ALLERGY_TITLE_PATTERNS = [
    r"allergy\s*alert",
    r"allergic\s*reactions",
    r"hypersensitivity",
]

# Shared allergy-context vocabulary used by every label-analysis script
# (analyze_dpi_labels.py, analyze_peg_labels.py, analyze_carmine_labels.py).
# An allergen-name match must co-occur with one of these context tokens
# within ~80 chars to count as a real warning, not an ingredient-list
# mention inside a warning section.
#
# Editorial framing (2026-04-23 audit honesty rule): this token list is
# an editorial selection, NOT prescribed verbatim by any single primary
# source. The selection is INFORMED BY (not "anchored to"):
#   - 21 CFR 201.22 (FDA sulfite warning mandate vocabulary)
#   - AAAAI/ACAAI 2022 Drug Allergy Practice Parameter (PMID 36122788)
#   - Advair Diskus §4 contraindication template
# Plus the 2026-04-23 vocabulary expansion (Task #25):
#   - `intoler` (intolerance / intolerant — real label vocabulary
#     for lactose intolerance, milk intolerance)
#   - `adverse\s+react` (adverse reaction phrase — more specific
#     than bare `adverse` to avoid generic adverse-events false
#     positives)
#   - `cross[-\s]?react` (cross-reactivity — relevant for PEG /
#     polysorbate cross-reactive patients)
#
# Tokens deliberately rejected (would trigger thousands of false
# positives because they occur in every warning section text):
# `warn`, `caution`, `avoid`, `react` (alone), `adverse` (alone),
# `risk\s+of`, `known\s+to`. These do not indicate an allergic
# response specifically.
#
# A label warning about an allergen using vocabulary still outside
# this set (e.g. "should not be taken by patients with X") would not
# be detected. See methodology.md §5 for the full disclosure +
# false-positive AI review documentation.
ALLERGY_CONTEXT = (r"(?:allerg|hypersens|anaphyla|contraindicat"
                   r"|intoler|adverse\s+react|cross[-\s]?react)")


def build_setid_index(force_rebuild: bool = False) -> dict:
    """Build or load a set_id → ZIP path index for the whole bulk-data tree."""
    if INDEX_CACHE.exists() and not force_rebuild:
        idx = {}
        with open(INDEX_CACHE, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    idx[parts[0]] = parts[1]
        return idx

    idx = {}
    for zippath in BULK_DIR.rglob("*.zip"):
        stem = zippath.stem
        if "_" in stem:
            set_id = stem.split("_", 1)[1]
            idx[set_id] = str(zippath)
    with open(INDEX_CACHE, "w") as f:
        for sid, p in idx.items():
            f.write(f"{sid}\t{p}\n")
    return idx


def open_spl_xml(set_id: str, index: dict) -> Optional[bytes]:
    """Return SPL XML bytes for a set_id, or None if not found / unparseable."""
    zp = index.get(set_id)
    if not zp or not Path(zp).exists():
        return None
    try:
        with zipfile.ZipFile(zp) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".xml"):
                    return zf.read(name)
    except zipfile.BadZipFile:
        return None
    return None


def _iter_sections(xml_bytes: bytes):
    """Yield all <section> elements in the SPL XML."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return
    for section in root.iter(f"{SPL_NS}section"):
        yield section


def _section_code(section) -> str:
    code_el = section.find(f"{SPL_NS}code")
    if code_el is None:
        return ""
    return code_el.attrib.get("code", "")


def _section_title(section) -> str:
    title_el = section.find(f"{SPL_NS}title")
    return "".join(title_el.itertext()).strip() if title_el is not None else ""


def _section_text(section) -> str:
    """Extract all human-readable text from a section's <text> and <excerpt>."""
    parts = []
    text_el = section.find(f"{SPL_NS}text")
    if text_el is not None:
        for t in text_el.itertext():
            if t and t.strip():
                parts.append(t.strip())
    excerpt_el = section.find(f"{SPL_NS}excerpt")
    if excerpt_el is not None:
        for t in excerpt_el.itertext():
            if t and t.strip():
                parts.append(t.strip())
    return " ".join(parts)


def get_warning_sections(set_id: str, index: dict) -> list:
    """
    Return a list of (loinc_code, title, text) tuples for every warning-
    relevant section in the label. Includes title-gated 42229-5 sections
    only when their title indicates an allergy/hypersensitivity alert.
    """
    xml_bytes = open_spl_xml(set_id, index)
    if xml_bytes is None:
        return []

    out = []
    for section in _iter_sections(xml_bytes):
        code = _section_code(section)
        if code not in WARNING_SECTION_CODES:
            continue
        title = _section_title(section)
        text = _section_text(section)
        if not text:
            continue

        # Title-gating for 42229-5: only count as warning source if title
        # mentions allergy / hypersensitivity / allergic reactions.
        if code == "42229-5":
            if not any(re.search(p, title, re.IGNORECASE)
                       for p in OTC_ALLERGY_TITLE_PATTERNS):
                continue

        out.append((code, title, text))
    return out


def classify_warning_level(sections: list, allergen_patterns: list) -> tuple:
    """
    Classify a label's warning level for an allergen.

    sections: list of (code, title, text) tuples from get_warning_sections.
    allergen_patterns: list of regex patterns.

    Returns: (warning_level, section_code, triggering_text_snippet)
      warning_level:
        "section_4_contraindication" | "boxed_warning" |
        "section_5_warning" | "otc_allergy_alert" |
        "otc_do_not_use" | "otc_ask_doctor" |
        "adverse_reactions" | "silent"
    """
    patterns = [re.compile(p, re.IGNORECASE) if isinstance(p, str) else p
                for p in allergen_patterns]

    def _first_hit(text):
        for pat in patterns:
            m = pat.search(text)
            if m:
                span = m.span()
                snippet = text[max(0, span[0] - 40):min(len(text), span[1] + 40)]
                return snippet
        return None

    # Build code → text map from the sections list
    code_map = {}
    for code, title, text in sections:
        if code not in code_map:
            code_map[code] = text
        else:
            code_map[code] = code_map[code] + " " + text

    # Walk precedence order; first hit wins
    for code, level_label in WARNING_PRECEDENCE:
        text = code_map.get(code, "")
        if not text:
            continue
        hit = _first_hit(text)
        if hit:
            return (level_label, code, hit)
    return ("silent", "", "")
