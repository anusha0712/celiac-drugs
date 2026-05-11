# PEG in FDA-Regulated Drug Labels — Findings

*Data snapshot: DailyMed bulk download, April 6, 2026.*
*Validation table: `data/fullcatalog/peg_validation.csv` (4 regex patterns — tight scope, 2026-04-22).*
*Flagged CSV: `data/fullcatalog/allergens_fullcatalog_flagged.csv` (165,757 rows after baseline filter).*
*Label analysis: `data/fullcatalog/peg_label_analysis.csv`.*

## Scope

`contains_peg` is restricted to unconjugated PEG polymer:
POLYETHYLENE GLYCOL, POLYETHYLENE OXIDE, MACROGOL, CARBOWAX. Adjacent
families (polysorbates, poloxamers, polyoxyl derivatives, mPEG, PEG-N
surfactants, TPGS, Kollicoat IR) are out of scope. Rationale and
documentation: `methodology.md` §3.5–3.6.

## Baseline filter

The flagger applies a baseline that drops 34,204 of the raw 199,961
catalog rows (homeopathics, unapproved drugs, dietary supplements,
non-drug document types). PEG numbers shifted only marginally —
the dropped rows contain very few PEG-flagged products (~595 of
the original 28,551 contained_peg = ~2%). Detail in
`methodology.md` and `limitations.md` §PEG.

## Prevalence

| Slice | N | contains_peg | % excluding no_data |
|---|---:|---:|---:|
| Full catalog (post-baseline) | 165,757 | 27,956 | 17.71% |
| Oral route | 75,435 | 24,781 | 34.25% |
| Oral tablets/capsules/granules/pellets (ODT-excluded) | 64,123 | 23,834 | 38.06% |
| Oral solutions / powders for solution or suspension | 3,253 | 398 | 13.16% |
| Parenteral routes (IV/IM/SC/IT/IA — Stone 2019 anchor) | 11,052 | 226 | 2.44% |
| Gluten-methodology parity (ORAL only, swallowed, FDA-recognized) | 69,137 | 24,556 | 35.52% |

Reker 2019 reported PEG in 36.03% of 42,052 oral solids (Pillbox v201605).
Our oral-solids figure is 38.06% under the tight scope (post-baseline).
Differences from Reker reflect catalog snapshot, dosage-form keyword
mapping, and curation (per `methodology.md` §3.8).

The parenteral slice surfaces the Stone 2019 PEG-anaphylaxis pathway
context — PEGylated drugs and contrast agents administered IV/IM/SC.
Of 11,052 parenteral products post-baseline, 226 list a PEG-polymer
excipient (2.04% — most are PEGylated biologics or solubilizers).

The gluten-methodology parity row reports `contains_peg` against the
69,137-row gluten-filtered set (ORAL only, FDA-recognized, swallowed)
for like-for-like comparison with gluten findings.

## Three-layer regulatory gap

**Layer 1 — class rule.** No FDA rule mandates a PEG-allergen warning in
drug labels. 21 CFR 201.100 (Rx) and 21 CFR 201.66 (OTC Drug Facts)
require inactive-ingredient disclosure only. Contrast: 21 CFR 201.22
(mandatory sulfite warning) and 21 CFR 201.20 (FD&C Yellow No. 5
warning). No comparable mandate exists for PEG.
https://www.law.cornell.edu/cfr/text/21/201.22
https://www.law.cornell.edu/cfr/text/21/201.20

**Layer 2 — product inconsistency.** Of 16,450 unique set_ids flagged
`contains_peg` in the oral-solids slice (post-baseline), 16,293 had
parseable SPL XML (after rebuilding the label parser to cover both Rx
sections and OTC Drug Facts structure). None carry PEG-allergy language
in any warning section. 157 set_ids had no warning-relevant sections
at all.

| Warning level | Count | % of parseable |
|---|---:|---:|
| Section 4 Contraindication | 0 | 0.00% |
| Boxed Warning | 0 | 0.00% |
| Section 5 Warnings and Precautions | 0 | 0.00% |
| Silent | 16,293 | 100.00% |

Warning patterns require an allergy-context token (`allerg` / `hypersens`
/ `anaphyla` / `contraindicat`) within 80 characters of a PEG-family
name. Anchor sources: 21 CFR 201.22 (FDA sulfite warning mandate),
AAAAI/ACAAI 2022 Drug Allergy Practice Parameter (PMID 36122788),
Advair Diskus §4 contraindication template. Documented in
`methodology.md` §5 "Warning-pattern vocabulary."

**Layer 3 — silent listing.** 16,293 labels list PEG as an inactive
ingredient without any accompanying allergy-warning text. A patient
with documented PEG allergy reviewing their oral-solid medication has
no label cue distinguishing these products from PEG-free alternatives.

**Note on prior version (2026-04-23 reconciliation):** an earlier
version of this analysis reported 3 PEG-warning matches under bare-name
patterns; subsequent review found those 3 were ingredient-list
mentions inside boxed-warning sections, not real PEG-allergy warnings.
Patterns were tightened to require allergy-context tokens; the
corrected count is 0. Documented in `reconciliation_pass.md` Fix 1.

## Harm anchor references

- Stone CA Jr et al. 2019 — two PEG 3350 anaphylaxis index cases +
  53 FAERS reports. https://pubmed.ncbi.nlm.nih.gov/30557713/
- Wolfson AR et al. 2021 — 80-patient post-mRNA-vaccine PEG/polysorbate
  skin-test cohort. https://pubmed.ncbi.nlm.nih.gov/34166844/
- Greenhawt M et al. 2023 — GRADE consensus: PEG skin-test sensitivity
  0.02, specificity 0.99. https://pubmed.ncbi.nlm.nih.gov/36321821/

PEG 3350 as an active ingredient (MiraLAX family, 151 products) is out
of scope for this excipient-level analysis per the inactive-ingredients-
only project rule.

## Limitations

See `limitations.md` §PEG.
