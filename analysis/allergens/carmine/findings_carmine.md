# Carmine / Cochineal Extract / Carminic Acid in FDA-Regulated Drug Labels — Findings

*Data snapshot: DailyMed bulk download, April 6, 2026.*
*Validation table: `data/fullcatalog/carmine_validation.csv` (21 exact + 3 regex, primary-source-derived).*
*Flagged CSV: `data/fullcatalog/allergens_fullcatalog_flagged.csv` (165,757 rows after baseline filter).*
*Label analysis: `data/fullcatalog/carmine_label_analysis.csv`.*

## Units of analysis

Three counts appear in this document and in `methodology.md` §4. All
three are correct at different granularities:

- **161 products (NDC-level).** One row per
  `<manufacturedProduct>` block in SPL XML. Used for catalog-wide
  prevalence (e.g. "161 of 165,757 products").
- **141 set_ids (SPL-label-level).** One SPL label can list multiple
  NDCs with different excipient profiles. Used for label analysis
  (`analyze_carmine_labels.py` parses one SPL XML per set_id).
- **24 validation-table rows (rule-level).** The number of match
  rules (21 exact-match strings + 3 word-boundary regex patterns).
  Rules are primary-source-derived from 21 CFR 73.100 and the two
  carmine-family GSRS UNII records.

## Scope

`contains_carmine` = any of the permitted names for cochineal-derived
color additives on a drug label: carmine, cochineal, cochineal extract,
carminic acid, plus GSRS synonyms (C.I. 75470, Natural Red 4, E 120,
INS-120, cochineal carmine, etc.). Primary-source derivation: 21 CFR
73.100 permitted names + GSRS UNII synonym records for cochineal
(TZ8Z31B35M) and carminic acid (CID8Z8N95N).
https://www.law.cornell.edu/cfr/text/21/73.100
https://precision.fda.gov/uniisearch/srs/unii/TZ8Z31B35M
https://precision.fda.gov/uniisearch/srs/unii/CID8Z8N95N

## Baseline filter

The flagger applies a baseline that drops 34,204 of the raw 199,961
catalog rows (homeopathic, unapproved drugs, dietary supplements,
non-drug document types). 15 carmine-flagged products were dropped
by the baseline (mostly homeopathic combo remedies and unapproved-drug
or dietary-supplement entries) — current 161 carmine count is
post-baseline. Detail in `methodology.md` and `limitations.md` §Carmine.

## Prevalence — landscape view

161 of 165,757 catalog products (0.097%) list a carmine-family
excipient post-baseline. Under the gluten-methodology filter (ORAL
only, FDA-recognized, swallowed, 69,137 rows), 130 products list
carmine (0.19%). The universe is small enough to characterize across
every categorical dimension without further pre-filtering.

**Route:** 135 ORAL (83.9%); 26 TOPICAL (16.1%).

**Approval type:** 61 ANDA generics (37.9%); 40 NDA brands (24.8%); OTC
monograph variants combined 60 (37.3%) across case-variant spellings.
(Homeopathic / dietary-supplement / unapproved-drug entries removed
by the baseline filter.)

**Bulk category:** 95 human_otc (59.0%); 66 human_prescription (41.0%).
(Homeopathic and `other` bulk_category dropped by baseline.)

**Brand/generic:** 40 brand; 61 generic; 60 OTC monograph.

**Oral dosage forms (135 products):** TABLET 37; TABLET DELAYED RELEASE
26; TABLET CHEWABLE 23; TABLET FILM COATED 22; LOZENGE 5; CAPSULE LIQUID
FILLED 7; TABLET EXTENDED RELEASE 5; TABLET FILM COATED EXTENDED RELEASE
5; TABLET COATED 1; CAPSULE 3; plus small single-digit counts across
other tablet/capsule variants and 2 SOLUTION.

**Active-ingredient breakdown (drug identity, not allergen matching):**
176 carmine products split into 140 single-active products (79.5%) and
36 combo products (20.5%, 2-11 actives each).

*Top single-active ingredients (140 products):* omeprazole 26;
levothyroxine sodium 22; calcium carbonate 16; azithromycin
monohydrate 8; zinc oxide 6; titanium dioxide 6; colchiceine 6;
lamotrigine 6; menthol 5; amitriptyline hydrochloride 5; bismuth
subsalicylate 4; loratadine 4; ropinirole hydrochloride 4. (Counts
restricted to single-active products so the percentage denominator
is honest.)

*Combo products (36):* fall into recognizable families — sunscreen
lip cosmetics (OCTINOXATE + OCTISALATE + AVOBENZONE / HOMOSALATE,
~12 products); cold/flu OTC multi-symptom (ACETAMINOPHEN +
DEXTROMETHORPHAN + PHENYLEPHRINE ± GUAIFENESIN ± TRIPROLIDINE,
~7 products); prescription combos (LUMACAFTOR + IVACAFTOR = Orkambi
4×; SULOPENEM ETZADROXIL + PROBENECID = Orlynvah 1×; EFAVIRENZ +
EMTRICITABINE + TENOFOVIR DISOPROXIL = HIV combo 1×); homeopathic
combo remedies ("kids cough" with 7 botanical actives 2×);
multi-vitamin combos (Dialyvite, Natal PNV, Fusion Plus, AREDS 2,
~6 products).

*Per-active tally within combos:* OCTISALATE 11; ACETAMINOPHEN 8;
OCTINOXATE 8; DEXTROMETHORPHAN HYDROBROMIDE 7; PHENYLEPHRINE
HYDROCHLORIDE 7; ASCORBIC ACID 6; HOMOSALATE 5; RIBOFLAVIN 5;
FOLIC ACID 5; GUAIFENESIN 4; OCTOCRYLENE 4; AVOBENZONE 4;
LUMACAFTOR 4; IVACAFTOR 4; BIOTIN 4.

**Top manufacturers** (normalized — case + punctuation + standard
suffixes collapsed): Haleon US Holdings 11; Sixarp 10; A-S
Medication Solutions 10; Procter & Gamble Manufacturing 5; Estee
Lauder 5; Accord Healthcare 5; Vertex Pharmaceuticals 4; MedVantx 4;
Teva Pharmaceuticals 4; Makeup Art Cosmetics 3.

## Three-layer regulatory gap

**Layer 1 — class rule.** 21 CFR 73.100(d)(2) requires "cochineal
extract" or "carmine" declaration in **food** ingredient statements.
21 CFR 73.1100 governs the same color additive in **drugs** and does
NOT impose an analogous common-or-usual-name mandate — labeling
conforms to 21 CFR 70.25, which is a color-additive-container rule.
FDA explicitly stated in the 2009 food rule (74 FR 207, E8-31253) that
drugs "would be addressed in a separate rulemaking"; no such drug
rulemaking has been issued in the 17 years since. Manual Federal
Register and FDA.gov searches through April 2026 returned no proposed
rule, guidance, or final rule on carmine/cochineal drug labeling.
https://www.law.cornell.edu/cfr/text/21/73.100
https://www.law.cornell.edu/cfr/text/21/73.1100
https://www.federalregister.gov/documents/2009/01/05/E8-31253/

**Layer 2 — product inconsistency.** Of 141 unique set_ids flagged
`contains_carmine` post-baseline, 138 had parseable warning-relevant
sections after the parser was extended to cover OTC Drug Facts
structure (allergy alert, do-not-use, ask-doctor sections alongside
Rx sections). 3 set_ids had no warning-relevant sections at all.

| Warning level | Count |
|---|---:|
| Section 4 Contraindication | 0 |
| Boxed Warning | 0 |
| Section 5 Warnings and Precautions | 0 |
| OTC Allergy Alert / Do-Not-Use / Ask-Doctor | 0 |
| Silent | 138 |

Warning patterns require an allergy-context token (`allerg` /
`hypersens` / `anaphyla` / `contraindicat`) within 80 characters of a
carmine-family name. Anchor sources: 21 CFR 201.22, AAAAI/ACAAI 2022
Drug Allergy Practice Parameter (PMID 36122788), Advair Diskus §4
template. Documented in `methodology.md` §5 "Warning-pattern
vocabulary."

**Layer 3 — silent listing.** 138 of 138 parseable drug labels (Rx +
OTC) list carmine or a carmine synonym in the inactive ingredients
without any accompanying allergy-warning text in any warning-relevant
SPL section. A patient with documented carmine hypersensitivity has no
label cue on any of these products.

## Harm anchor references

- Greenhawt M et al. 2009 — only US-published medication-induced
  carmine anaphylaxis case (generic azithromycin tablet with pink
  carmine film coating). https://pubmed.ncbi.nlm.nih.gov/19331724/
- Takeo N et al. 2018 — 22 Japanese cochineal-dye anaphylaxis cases.
  https://pubmed.ncbi.nlm.nih.gov/29705083/
- Sadowska B et al. 2022 — carmine-positive skin-prick in 8% of
  chronic-urticaria patients studied. Journal year is 2022, not 2020
  as some secondary sources cite. https://pubmed.ncbi.nlm.nih.gov/35369613/
- Khalil HA et al. 2025 — Qatar / US co-authored recurrent-anaphylaxis
  case resolved on carmine elimination across food, cosmetics, and
  medications. https://pubmed.ncbi.nlm.nih.gov/41113612/

## Contemporary exposure path

Of 350 azithromycin-containing products in the post-baseline catalog,
8 list carmine as an excipient — all 8 are generic (ANDA) formulations.
This is the same exposure path that produced the Greenhawt 2009
anaphylaxis case. 27 of 865 omeprazole products, 22 of 851
levothyroxine products, and 15 of 909 calcium carbonate products
also list carmine.

## Limitations

See `limitations.md` §Carmine.
