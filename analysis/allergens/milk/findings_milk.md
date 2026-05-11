# Milk Proteins and Lactose in FDA-Regulated Drug Labels — Findings

*Data snapshot: DailyMed bulk download, April 6, 2026.*
*Validation table: `data/fullcatalog/milk_validation.csv` (27 entries, FARE-derived after pharmacist review removed lactose family + lactulose 2026-05-05).*
*Flagged CSV: `data/fullcatalog/allergens_fullcatalog_flagged.csv` (165,757 rows after baseline filter).*
*Label analysis: `data/fullcatalog/dpi_label_analysis.csv`.*

## Scope

`contains_milk` = any excipient string that appears on the FARE milk-
ingredient list (or is a DailyMed string variant of such). Primary
source: FARE Common Allergens page (milk).
https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens/milk

Every validation-table row has a FARE source_url, an FDA IID cross-
reference status (`in_iid` / `not_in_iid`), and a rationale.

Lactose family and lactulose were removed from the validation table
2026-05-05 per pharmacist review (purified milk sugars do not
themselves contain allergenic milk proteins).

## Baseline filter

The `flag_allergens_fullcatalog.py` flagger applies a baseline filter
that drops 34,204 of the raw 199,961 catalog rows: homeopathic,
unapproved drug other / unapproved homeopathic / dietary supplement /
export only / cosmetic / unapproved medical gas, plus non-drug document
types (vaccines, medical devices, plasma derivatives, animal products,
allergenics, cellular therapies, bulk ingredients). The filter mirrors
steps 1, 2, 5 of `filter_gluten_fullcatalog.py` but keeps every route
so that respiratory / parenteral harm anchors remain in scope. Detail
in `methodology.md` §1.x and `limitations.md` §Milk.

## Prevalence

| Slice | N | contains_milk | % excluding no_data |
|---|---:|---:|---:|
| Full catalog (post-baseline) | 165,757 | 115 | 0.07% |
| Oral route | 75,435 | 36 | 0.05% |
| All respiratory route | 1,531 | 0 | 0.00% |
| Parenteral routes (IV/IM/SC/IT/IA — Hatcher 2025 anchor) | 11,052 | 0 | 0.00% |
| **DPIs (harm anchor, pMDIs excluded)** | **29 NDCs** | **0** | **0.00%** |
| Gluten-methodology parity (ORAL only, swallowed, FDA-recognized) | 69,137 | 36 | 0.05% |

The DPI slice (POWDER, METERED / INHALANT, METERED + respiratory route,
pMDIs excluded) is the lactose-carrier harm anchor. 0 of 29 DPI NDCs
list a milk-derived excipient under the revised validation table
(lactose family removed 2026-05-05).

The parenteral slice surfaces Hatcher 2025's trace-bovine-casein
finding in IV methylprednisolone vials. Of 11,052 parenteral products
post-baseline, 0 list a FARE-defined milk-derived excipient under the
revised table.

Reker 2019 reported lactose in 44.82% of 42,052 oral solid dosage
formulations (Pillbox v201605). Our oral-route figure (0.05%) reflects
milk-protein excipients only after the lactose-family exclusion.

The gluten-methodology parity row reports `contains_milk` against the
69,137-row gluten-filtered set (ORAL only, FDA-recognized, swallowed)
for like-for-like comparison with the gluten findings.

## Three-layer regulatory gap

**Layer 1 — class rule.** No FDA rule mandates milk-protein or lactose
allergen warnings in drug labels. FALCPA (2004) explicitly excludes
drugs — the statute applies only to foods.
https://www.fda.gov/food/food-allergensgluten-free-guidance-documents-regulatory-information/food-allergen-labeling-and-consumer-protection-act-2004-falcpa

**Layer 2 — product inconsistency (DPI harm anchor, set_id-level).**
19 unique DPI set_ids (distinct from 29 NDCs because multiple NDCs can
share one SPL label) were analyzed:

| Warning level | Count | Notes |
|---|---:|---|
| Section 4 Contraindication | 18 | Advair Diskus / Wixela Inhub family — "Severe hypersensitivity to milk proteins or demonstrated hypersensitivity to fluticasone propionate, salmeterol, or any of the excipients." |
| Silent | 1 | Afrezza (inhaled insulin, Mannkind) — no milk-protein warning because Afrezza does not use lactose carrier. |

Warning patterns require an allergy-context token (`allerg` /
`hypersens` / `anaphyla` / `contraindicat`) within 80 characters of a
milk-family name. Anchor sources: 21 CFR 201.22 (FDA sulfite warning
mandate), AAAAI/ACAAI 2022 Drug Allergy Practice Parameter (PMID
36122788), Advair Diskus §4 contraindication template. Documented in
`methodology.md` §5 "Warning-pattern vocabulary."

**Layer 3 — silent listing (oral).** 36 oral-route products list a
FARE-defined milk-derived excipient under the revised validation
table. None carry milk-protein allergy language.

## Harm anchor references

- Nowak-Wegrzyn A et al. 2004 — Advair Diskus milk-protein DPI
  anaphylaxis in milk-allergic patients.
  https://pubmed.ncbi.nlm.nih.gov/15007361/
- Robles J et al. 2014 — US pediatric DPI anaphylaxis case.
  https://pubmed.ncbi.nlm.nih.gov/25309152/
- Bar-On O et al. 2022 — national survey on DPI prescribing in CMPA.
  https://pubmed.ncbi.nlm.nih.gov/36555964/
- Hatcher VR et al. 2025 — IV methylprednisolone ELISA detected trace
  Bos d 11 casein in all five vials tested; Bos d 9 undetectable.
  https://pubmed.ncbi.nlm.nih.gov/40958177/

## Limitations

See `limitations.md` §Milk. Notable: Spiriva HandiHaler (powder-in-
capsule DPI) is classified in DailyMed as `CAPSULE / ORAL` rather than
`POWDER, METERED / RESPIRATORY`, so it does not appear in the DPI
harm-anchor slice above even though its lactose carrier is inhaled.
