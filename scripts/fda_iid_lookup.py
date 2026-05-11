#!/usr/bin/env python3
"""
fda_iid_lookup.py — cross-reference excipient names against FDA IID.

Reads FDA-IID-recent-update.csv (user-downloaded, at project root) and
provides lookup by ingredient name. Used by build_allergens_validation.py
to populate iid_status on every row.

Exports:
    load_iid_index()  -> (name_to_records: dict, unii_to_records: dict)
    in_iid(name)      -> True if any IID record matches the name
    iid_routes(name)  -> set of routes for which IID lists the ingredient
"""

import csv
import sys
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).parent.parent
IID_CSV = BASE_DIR / "FDA-IID-recent-update.csv"


def _norm(s: str) -> str:
    """Normalize ingredient name for matching: strip, upper, collapse spaces."""
    return " ".join((s or "").upper().split())


@lru_cache(maxsize=1)
def load_iid_index():
    """Return (name_to_records, unii_to_records) — cached."""
    if not IID_CSV.exists():
        sys.exit(
            f"ERROR: FDA IID file not found at {IID_CSV}.\n"
            f"Download from "
            f"https://www.fda.gov/drugs/drug-approvals-and-databases/"
            f"inactive-ingredients-database-download\n"
            f"and place at the project root as FDA-IID-recent-update.csv."
        )
    name_idx = {}
    unii_idx = {}
    with open(IID_CSV, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = _norm(row.get("INGREDIENT_NAME", ""))
            unii = (row.get("UNII", "") or "").strip().upper()
            if name:
                name_idx.setdefault(name, []).append(row)
            if unii:
                unii_idx.setdefault(unii, []).append(row)
    return name_idx, unii_idx


def in_iid(name: str) -> bool:
    """True if an exact (normalized) ingredient name match exists in IID."""
    name_idx, _ = load_iid_index()
    return _norm(name) in name_idx


def iid_unii_for(name: str) -> str:
    """Return first UNII listed in IID for this name, or empty string."""
    name_idx, _ = load_iid_index()
    recs = name_idx.get(_norm(name), [])
    for r in recs:
        u = (r.get("UNII") or "").strip().upper()
        if u:
            return u
    return ""


def iid_routes(name: str) -> set:
    """Return set of routes under which IID lists this ingredient."""
    name_idx, _ = load_iid_index()
    recs = name_idx.get(_norm(name), [])
    return {(r.get("ROUTE") or "").strip().upper() for r in recs if r.get("ROUTE")}


def iid_status(name: str) -> str:
    """Return 'in_iid' or 'not_in_iid' for a validation-table row."""
    return "in_iid" if in_iid(name) else "not_in_iid"


if __name__ == "__main__":
    name_idx, unii_idx = load_iid_index()
    print(f"FDA IID loaded: {len(name_idx):,} unique ingredient names, "
          f"{len(unii_idx):,} unique UNIIs.")
    # Smoke test
    for probe in ("LACTOSE MONOHYDRATE", "POLYETHYLENE GLYCOL",
                  "COCHINEAL", "CARMINIC ACID", "XANTHAN GUM",
                  "ETHYL BUTYRATE", "LACTIC ACID"):
        print(f"  {probe:<30} {iid_status(probe):<15} UNII={iid_unii_for(probe)}")
