# Allergen Study Replication Project — Gluten & Celiac Focus

## Project Goal
Science journalism piece analyzing a Portuguese study on gluten excipients in
medications, and replicating the methodology using US data via DailyMed. The
story centers on the information asymmetry celiac patients face: they cannot
reliably determine from drug labels whether their medications contain
gluten-source excipients, because starch sourcing is not consistently disclosed.
This is a labeling transparency and regulatory gap story, not a toxicology story.

## Source Study
- **Citation:** Figueiredo et al. (2025). "Presence of gluten and soy derived excipients 
  in medicinal products and their implications on allergen safety and labeling." 
  Scientific Reports, 15, 10976. https://doi.org/10.1038/s41598-025-95525-6
- **Database used:** INFOMED (Portugal's national drug database)
- **Sample:** 308 drugs across 3 therapeutic categories
- **Key findings (gluten only):**
  - 44.4% of paracetamol (analgesic/antipyretic) drugs contained gluten
  - 8.2% of ibuprofen (NSAIDs) contained gluten
  - 0% of antiasthmatics/bronchodilators contained gluten
  - 51.2% of solid oral analgesic/antipyretic forms contained gluten
  - Film-coated tablets (61.1%) and regular tablets (60%) were highest risk
  - Inhalers were the safest category overall

## Output Type
Science journalism — not a clinical study. No IRB needed. No clinical co-author 
required. Audience is informed general public, specifically those affected by or 
interested in celiac disease and medication safety.

## Active Skills
- **scientific-critical-thinking** — for methodology critique, bias detection, 
  evidence quality assessment
- **scholar-evaluation** — for structured assessment of the source paper

## Statistical Testing — Keep When Relevant
The original study used chi-squared and Fisher's exact test. These are important 
and should be explained when relevant — they confirm that percentage differences 
between drug categories are real and not sampling flukes. When referencing stats, 
explain them in plain language accessible to a general audience.

## US Methodology Equivalents
| Portugal | USA |
|---|---|
| INFOMED database | DailyMed (dailymed.nlm.nih.gov) |
| SmPC (Summary of Product Characteristics) | Package Insert / Prescribing Information |
| INFARMED authorization check | FDA National Drug Code (NDC) Directory |
| Excipient definitions (EU naming) | FDA Inactive Ingredient Database |

## Gluten Excipient List (from source paper, Table 1)
These are the excipients flagged in the original study. US equivalents MUST be 
validated against FDA Inactive Ingredient Database before use — EU and FDA naming 
conventions differ in some cases.

**May contain gluten:**
Wheat, Rye, Barley, Semolina, Bran, Malt, Glucose syrup, Gelatinized starch,
Pre-gelatinized starch, Sodium carboxymethyl starch, Modified starch, 
Starch (source unspecified), Oats, Xanthan gum

**Gluten-free — do NOT flag:**
Corn starch, Potato starch, Croscarmellose sodium (cellulose-based, NOT starch),
Pregelatinized corn starch, Modified corn starch, Maltodextrin, Tapioca starch,
Sodium starch glycolate type A potato

**Note on Xanthan gum:** Flagged precautionarily. May contain gluten traces 
depending on production source. Not definitively gluten-containing. 
Decision on whether to flag must be recorded in excipient_validation.csv.

## Drug Categories to Replicate
1. **Analgesics/Antipyretics** — acetaminophen (paracetamol equivalent in US)
2. **NSAIDs** — ibuprofen

**Dropped:** Antiasthmatics/bronchodilators — original study included them as a
control group (inhalers don't use starch excipients, so always 0%). Not relevant
to the journalism angle, which focuses on oral medications celiac patients swallow.

---

## Project Phases

### Phase 1: Paper Analysis ✅ COMPLETE
- [x] Critical analysis of methodology using scientific-critical-thinking skill
- [x] Structured evaluation using scholar-evaluation skill (composite: 2.9/5)
- [x] Key question: Is this study solid enough to anchor a journalism piece? → YES, with framing caveats
- [x] Key question: What are the honest limitations to disclose to readers? → 6 key caveats documented
- [x] Key question: Is US replication viable with DailyMed? → YES, and would be stronger
- [x] Output: analysis/phase1_paper_analysis.md

### Phase 2: US Data Collection ✅ COMPLETE
- [x] Build excipient_validation.csv — 48 entries from 3 sources (Portuguese study,
      FDA IIG, DailyMed data). Restructured from EU-mapping to comprehensive lookup table.
- [x] Decide on starch (unspecified): `unknown`
- [x] Decide on xanthan gum: reclassified to `gluten_free` per National Celiac Association
      (departure from Portuguese study). Source: https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/
- [x] Key finding: sodium carboxymethyl starch = sodium starch glycolate (same compound);
      croscarmellose sodium is DIFFERENT (cellulose-based, gluten-free)
- [x] Key finding: FDA CPG 578.100 says unqualified "starch" in US = corn starch,
      but a celiac patient reading the label wouldn't know this rule
- [x] Pull acetaminophen products from DailyMed — 4,986 products
- [x] Pull ibuprofen products from DailyMed — 1,619 products
- [x] Misspelling sweep — searched for common misspellings, added 2 Scot-Tussin products
- [x] Second-pass excipient audit — extracted 511 unique excipient strings, identified
      all gluten-adjacent terms, added to validation table with rationale and citations
- [x] NDC Directory spot-check — decided to skip, documented as limitation
- [x] Exclude injectables — 33 removed (IV acetaminophen, IV ibuprofen)
- [x] Include single-ingredient AND combination products (3,259 single, 3,346 combo)
- [x] Include both generic and branded products (2,747 generic, 128 brand, 3,763 OTC monograph)
- [x] Apply flags → dailymed_flagged.csv using four-tier system:
      gluten_free / unknown / contains_gluten / no_data
- [x] Final dataset: 6,605 products

### Phase 3: Data Analysis ✅ COMPLETE
- [x] Count gluten excipient presence by drug category and dosage form
- [x] Count by OTC vs Rx, and OTC/Rx × category cross-tabs
- [x] Count by single-ingredient vs combination
- [x] Rank sources of uncertainty by excipient
- [x] Compare US findings to Portugal findings (methodological reference)
- [x] Identify notable differences and possible explanations
- [x] Document findings objectively in analysis/findings.md with separate
      interpretation section using scientific critical thinking
- [x] Note limitations honestly in analysis/limitations.md (includes flagging methodology)
- [x] Key results: 97.2% gluten_free, 2.7% unknown, 0.02% contains_gluten
      (excluding no_data). 1 product with confirmed wheat starch. 92.8% of
      uncertainty from single excipient (SSG Type A, no source specified).

---

## Output File Structure

All output files live in the project directory as follows. 
Claude must save to these exact paths and never overwrite raw data files.

```
project/
├── CLAUDE.md                          ← this file
├── SESSION_LOG.md                     ← updated at end of every session
│
├── scripts/                           ← all data extraction and processing scripts
│   ├── extract_bulk.py                ← full-catalog extraction (bulk ZIPs → CSV)
│   ├── pull_dailymed.py               ← pilot extraction (API → CSV, aceto+ibu only)
│   ├── build_excipient_list.py        ← keyword search, builds research worklist
│   └── build_validation_table.py      ← assembles complete validation CSV
│
├── data/
│   ├── dailymed_bulk_raw.csv          ← full catalog (199,961 rows from bulk download)
│   ├── bulk/                          ← full-catalog derived files
│   │   ├── excipient_validation.csv   ← complete validation table (171 entries)
│   │   └── excipient_research_worklist.csv  ← intermediate (new terms researched)
│   └── eda/                           ← pilot/exploratory data (acetaminophen + ibuprofen)
│       ├── dailymed_raw.csv           ← pilot raw pull, never modified
│       ├── dailymed_flagged.csv       ← pilot data + gluten flag columns applied
│       └── excipient_validation.csv   ← pilot validation table (48 entries,
│                                         preserved as historical snapshot)
│
├── bulk-data/                         ← raw DailyMed bulk download (April 6, 2026)
│   ├── human-otc/                     ← ~87K ZIPs across 11 subfolders
│   ├── human-prescription/            ← ~54K ZIPs across 6 subfolders
│   ├── homeopathic/                   ← ~16K ZIPs in 1 subfolder
│   └── other/                         ← ~2.5K ZIPs in 1 subfolder (remainder labels)
│
└── analysis/
    ├── phase1_paper_analysis.md       ← methodology critique and scholar evaluation
    ├── findings.md                    ← analytical conclusions, updated per phase
    └── limitations.md                 ← running log of methodological caveats
```

**Note on script execution:** All scripts in `scripts/` use `Path(__file__).parent.parent`
(or equivalent) to resolve to the project root, so they should be run from the project
root: `python3 scripts/build_validation_table.py`

### File Specifications

**data/dailymed_bulk_raw.csv** — Full catalog extraction. 43 columns, 199,961 rows.
Never modify after creation. Re-run `extract_bulk.py` to regenerate.

**data/eda/dailymed_raw.csv** — Pilot dataset (acetaminophen + ibuprofen only). Never modify.
39 columns extracted from DailyMed SPL XML via API. Core columns: `drug_name, generic_name,
brand_generic, category, dosage_form, route, active_ingredients, single_or_combo,
excipients_raw, excipient_uniis, ndc_code, approval_number, approval_type,
marketing_status, manufacturer, color, shape, imprint, set_id, dailymed_url`

**data/eda/dailymed_flagged.csv** — Pilot data with gluten flags. Columns:
`drug_name, brand_generic, category, dosage_form, excipients_raw, gluten_flag
(gluten_free/unknown/contains_gluten), flagged_excipients, ndc_code`

**data/eda/excipient_validation.csv** — Pilot validation table (48 entries). One row per
excipient decision. Columns: `fda_term, source, flag_decision (gluten_free/unknown/contains_gluten),
rationale, source_url, eu_equivalent`

**data/bulk/excipient_validation.csv** — Complete validation table for the full catalog
(171 entries: 48 pilot + 123 new after Apr 9 revisions). Same schema as the pilot
table. Pilot entries are preserved and annotated with `Bulk catalog: N products.`
in the rationale. New entries have `source = "dailymed_bulk"`. Three pilot entries
have bulk-table revisions applied via the `PILOT_OVERRIDES` dict in
`scripts/build_validation_table.py` — the pilot CSV itself remains unchanged as a
historical snapshot. Generated by `scripts/build_validation_table.py` — re-running
the script regenerates the file deterministically.

---

## Session Log Instructions

**At the end of every session, Claude must update SESSION_LOG.md.**

Use this format:

```
## Session [date]

### What was completed
- [bullet list]

### Decisions made
- [bullet list — include rationale for any non-obvious decisions]

### Assumptions flagged this session
- [copy any ⚠️ ASSUMPTION blocks from this session here]

### Open questions for next session
- [bullet list]

### Where to pick up
[One sentence summary of the immediate next step]
```

If SESSION_LOG.md does not exist yet, create it. Always append — never overwrite previous sessions.

---

## Known Methodological Limitations to Carry Forward
These apply to the original study AND the US replication:
- Analysis is label-based only — actual gluten levels are not measured
- Cross-contamination during manufacturing cannot be detected this way
- Some package inserts list "starch" without specifying the source
- Xanthan gum is flagged precautionarily — not confirmed gluten-containing
- Only 2 drug categories studied (acetaminophen, ibuprofen) — not all medications
- Source study's 44.4% headline figure = labeling ambiguity ceiling, not confirmed gluten
  (zero products in Table 3 contained wheat, rye, barley, or any confirmed gluten grain)

## Key Decisions — RESOLVED
- **Starch (unspecified):** flagged `unknown` — precautionary, consistent with source study.
  NOTE: FDA CPG 578.100 says unqualified "starch" in the US legally = corn starch,
  but a celiac patient reading the label has no way to know this regulatory technicality.
  Decision recorded in excipient_validation.csv.
- **Xanthan gum:** RECLASSIFIED `unknown` → `gluten_free` (2026-03-27).
  The National Celiac Association states xanthan gum does not contain gluten.
  Source: https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/
  This is a methodological departure from the Portuguese study, which flagged it
  precautionarily. Our reclassification reduces `unknown` from 893 to 166 products.
  Decision recorded in excipient_validation.csv.
- **Antiasthmatics:** dropped — 0% findings in source study add no value to journalism angle.
- **Combination products:** INCLUDED — reflects the real OTC landscape celiac patients face.
- **Data source:** 100% DailyMed (the tool FDA recommends patients use).
  Script uses DailyMed API for set_id collection + DailyMed XML endpoint for label data.
  No OpenFDA dependency (40% coverage gap identified).
- **Three-tier flagging:** gluten_free / unknown / contains_gluten
  (replaces original yes/no/uncertain — clearer semantics)
- **New excipients:** any excipient found in US data but not on Portuguese list gets added
  to excipient_validation.csv only with documented rationale and source — no blind additions.
- **Misspelling sweep (2026-03-27):** DailyMed contains products with misspelled active
  ingredient names. Searched for common misspellings of both drugs. Results:
  - `acetominophen`: 5 hits. Disposition:
    - Rite Aid Multi-Symptom Cold and Flu Relief (NDC 11822-1988) — already in dataset
    - Scot-Tussin Original Multi-Symptom (IriSys, NDC 15187-004) — ADDED to dataset
    - Scot-Tussin Original SF Multi-Symptom (Scot-Tussin Pharmacal, NDC 0372-0004) — ADDED
    - Propoxyphene Napsylate and Acetominophen (Andrx, NDC 62037-882) — EXCLUDED,
      propoxyphene withdrawn from US market Nov 2010 (FDA safety announcement)
    - Propoxyphene Napsylate and Acetominophen (Andrx, NDC 62037-930/931) — EXCLUDED,
      same reason as above
  - `acetamenophen`, `acetamiophen`, `acetaminiphen`: 0 hits each
  - `ibuprofin`, `ibuprophen`, `ibuprofein`: 0 hits each
  - Dataset updated from 6,636 → 6,638 rows after adding 2 Scot-Tussin products.
- **Unit of analysis:** NDC-level (not set_id). Two NDCs under the same SPL label can have
  different excipient profiles — the NDC is what a patient encounters on the shelf.
- **Reporting scope:** OTC, Rx, and combined — all three views reported separately.
- **Index completeness:** Acknowledged as limitation. No cross-reference against FDA NDC
  Directory — DailyMed is the patient-facing tool and our sole authoritative source.

### Bulk Extraction Decisions (2026-04-07)
These decisions apply to the full-catalog extraction (`extract_bulk.py` → `dailymed_bulk_raw.csv`).

- **Data source: DailyMed bulk download (April 6, 2026).** Downloaded the complete catalog
  from https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm as ZIP archives.
  Four download categories: Human OTC Labels (11 parts), Human Prescription Labels (6 parts),
  Homeopathic Labels (1 file), Remainder Labels (1 file). No API calls — all local extraction.
- **Scope: all 159,431 labels, no filtering.** Every ZIP in the bulk download is extracted.
  No injectable filtering, no drug-name filtering, no category filtering. Raw data = complete.
  Filtering belongs in analysis, not extraction.
- **All fields come from XML or folder — zero AI inference.** Every column in
  `dailymed_bulk_raw.csv` is either:
  (a) mechanically parsed from the HL7 SPL XML using XPath element/attribute extraction,
  (b) derived from the folder path (`bulk_category`),
  (c) derived from the ZIP filename (`source_zip`, `set_id`), or
  (d) constructed by concatenating a fixed URL prefix with set_id (`dailymed_url`).
  No natural language processing, classification, or inference was used.
- **`brand_generic` classification: deterministic rule, not inference.** Based on the FDA
  application number prefix in the XML's `<approval><id extension="...">` field:
  ANDA → `generic` (Abbreviated New Drug Application = generic drugs),
  NDA → `brand` (New Drug Application = innovator/brand drugs),
  BLA → `brand` (Biologics License Application = biological products),
  anything else → `otc_monograph` (OTC monograph drugs without NDA/ANDA/BLA numbers).
  Source: https://www.fda.gov/drugs/how-drugs-are-developed-and-approved/types-applications
- **`bulk_category` from folder name, not XML.** Homeopathic products have
  `document_type = "HUMAN OTC DRUG LABEL"` in the XML (LOINC 34390-5) because they are
  marketed as OTC drugs. The distinction between homeopathic and conventional OTC is only
  available via (a) the DailyMed download category (our `bulk_category` field) or
  (b) the `marketing_status` field in the XML (which reads "unapproved homeopathic" for
  homeopathic products). Both fields are captured. Mapping:
  `human-otc/` → `human_otc`, `human-prescription/` → `human_prescription`,
  `homeopathic/` → `homeopathic`, `other/` → `other` (remainder labels: vaccines,
  medical devices, bulk ingredients, dietary supplements, allergenics, etc.).
- **`document_type` from XML, not folder.** The LOINC code in the XML root
  `<code displayName="...">` element. Common values: `HUMAN OTC DRUG LABEL` (34390-5),
  `HUMAN PRESCRIPTION DRUG LABEL` (34391-3), `VACCINE LABEL`, `MEDICAL DEVICE`, etc.
  Note: case inconsistency exists in DailyMed data (e.g. "HUMAN PRESCRIPTION DRUG LABEL"
  vs "Human Prescription Drug Label") — normalization deferred to analysis.
- **`dea_schedule`: new field.** Extracted from `<policy><code displayName="...">` in the XML.
  Values: CII, CIII, CIV, CV. Empty for non-controlled substances. 7,984 products have a
  DEA schedule in the full dataset.
- **`set_id` from ZIP filename, cross-checked against XML.** ZIP filenames are
  `{date}_{set_id}.zip`. The UUID after the underscore matches `<setId root="...">` in the
  XML. Extracted from filename for efficiency; XML value used as fallback.
- **Old `category` column dropped.** The analgesic_antipyretic/nsaid classification was
  specific to the acetaminophen/ibuprofen pilot. Not applicable to the full catalog.
- **No injectable filtering in extraction.** The pilot script excluded injectables by
  route code. The bulk script extracts all routes. Filtering by route, dosage form, or
  any other criterion is done in analysis scripts, not at extraction time.
- **Unit of analysis: NDC-level (same as pilot).** One SPL label can contain multiple
  `<manufacturedProduct>` blocks with different NDC codes, dosage forms, and excipient
  profiles. Each becomes its own row. 159,431 labels → 199,961 rows.
- **Error handling: log and continue.** If a ZIP is corrupt or XML fails to parse, the
  error is logged to `data/extract_errors.txt` and processing continues. Result: 0 errors
  across all 159,431 ZIPs.

### Bulk Excipient Validation Decisions (2026-04-09)
These decisions apply to building `data/bulk/excipient_validation.csv` — the complete
gluten-flagging table for the full catalog (171 entries after revisions; see also
`analysis/validation_table_review.md` for the full pending-changes log).

- **Discovery method: keyword search on unique excipient strings.** The bulk catalog
  contains 10,019 unique excipient strings (case-normalized to uppercase). A word-boundary
  regex search using 20 keywords identified 130 gluten-adjacent terms; 23 already in the
  pilot table; 107 new terms requiring research. Originally 85 of those 107 were
  classified into the table and 22 were excluded as false positives, but the Apr 9
  revisions moved all 22 false positives into the table as `gluten_free` (Option A,
  see below) and added 16 cyclodextrin/dextrin entries that were missed by the original
  keyword search. Final new-entry count: 123. Script: `build_excipient_list.py`.

- **Keyword sources (3 categories, 20 keywords total):**
  1. **Portuguese study (Figueiredo et al. 2025) Table 1** — direct gluten excipient terms:
     `wheat`, `rye`, `barley`, `semolina`, `bran`, `malt`, `oat`, `oats`, `starch`,
     `gluten`, `glucose`, `pregelatinized`, `flour`, `grain`
  2. **Latin botanical names for gluten grains** — caught homeopathic/cosmetic naming:
     `avena` (oat), `triticum` (wheat), `hordeum` (barley), `secale` (rye)
  3. **Starch chemistry terms** — caught variants and derivatives:
     `glycolate` (catches SSG variants), `dextrin` (starch hydrolysis product),
     `gum` (catches fermentation gums where wheat substrate is theoretically possible)
  Word-boundary regex (`\b...\b`) was used to avoid false matches like "oat" in "coated".

- **False positive exclusions — now in table (Option A, 2026-04-09 revision).**
  21 terms originally flagged as keyword false positives are now in the validation
  table as `gluten_free` with rationale "Keyword false positive — matched gluten-adjacent
  search term but compound is not grain-derived." This makes the validation table the
  single source of truth — re-running `build_excipient_list.py` will not require
  re-excluding these by hand. Categories:
  - **Glycolate esters** (5): SODIUM GLYCOLATE, ETHYL GLYCOLATE, ALLYL AMYL GLYCOLATE,
    BUTYL GLYCOLATE, CEFATRIZINE PROPYLENE GLYCOLATE — esters of glycolic acid, unrelated
    to sodium starch glycolate
  - **Methyl glucose esters** (7): PEG-120 METHYL GLUCOSE DIOLEATE, METHYL GLUCOSE
    SESQUISTEARATE, PEG-20 METHYL GLUCOSE SESQUISTEARATE, METHYL GLUCOSE DIOLEATE,
    PPG-20 METHYL GLUCOSE ETHER, PPG-20 METHYL GLUCOSE ETHER DISTEARATE, METHYL GLUCOSE —
    synthetic cosmetic emulsifiers, "glucose" refers to the sugar backbone unit
  - **Glucose biochemicals** (8): GLUCOSE OXIDASE (an enzyme), GLUCOSE-6-PHOSPHATE,
    DIPOTASSIUM GLUCOSE-6-PHOSPHATE, GLUCOSE 1,6-BISPHOSPHATE, .ALPHA.-GLUCOSE-1-PHOSPHATE
    DIPOTASSIUM DIHYDRATE, GLUCOSE PENTAACETATE, 2,3 DI-O-METHYL-D-GLUCOSE,
    PSEUDOMONAS GLUCOSE FERMENTATION RHAMNOLIPIDS — phosphorylated/methylated/acetylated
    sugar derivatives, biochemical compounds, not grain-derived
  - **Silicone** (1): DIMETHICONOL GUM — silicone polymer, "gum" refers to physical
    texture, not a plant gum
  - **Correction:** HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE)
    was originally excluded as a false positive but is actually a cyclodextrin variant.
    Now classified with the cyclodextrin family (gluten_free), not as a false positive.
  - **Note:** SODIUM POLYACRYLATE STARCH variants (4 particle sizes) are NOT false
    positives — they are flagged `unknown` because the project rule is consistent:
    starch with no source specified = unknown.

- **Case normalization at lookup time, not in storage.** The validation table stores
  `fda_term` strings exactly as they appear in DailyMed (uppercase by convention).
  ~6% of bulk data rows contain mixed-case excipients; the flagging script will
  normalize via `.upper().strip()` before lookup. The 113 case-only orphan strings
  in the bulk data contain zero gluten-adjacent terms, so no information is lost.

- **All wheat/barley/rye derivatives → `contains_gluten`.** Per FDA 21 CFR 101.91,
  wheat, barley, and rye are the three confirmed gluten-containing grains. Any excipient
  with a label that identifies one of these grains as the source is flagged
  `contains_gluten`, regardless of plant part (germ, bran, sprout, straw, root, top,
  pollen, whole) and regardless of processing (oil extraction, hydrolysis). Rationale:
  the project's framing is labeling transparency. If the label says "wheat," a celiac
  patient sees "wheat" and cannot determine safety. Whether the actual gluten content
  is below 20 ppm is a toxicology question, not a labeling one.
  - HYDROLYZED WHEAT PROTEIN (143+25 products) → contains_gluten
  - WHEAT GERM OIL (77+4 products) → contains_gluten
  - CETEARYL WHEAT STRAW GLYCOSIDES (2 products) → contains_gluten
  - HORDEUM VULGARE TOP, HORDEUM VULGARE ROOT → contains_gluten

- **All oat derivatives → `unknown` (precautionary).** Consistent with the pilot's
  OATS / OAT FIBER classification. Oats are NOT classified as a gluten-containing grain
  by FDA per 21 CFR 101.91, but cross-contamination with wheat/barley/rye during
  cultivation and processing is well documented. Affected: OAT (312 products), OAT KERNEL
  OIL, OAT BRAN, AVENA SATIVA WHOLE/LEAF/TOP/POLLEN, AVENA SATIVA (OAT) variants,
  OAT AMINO ACIDS, SODIUM LAUROYL OAT AMINO ACIDS, STARCH, OAT, etc. (17 oat-related entries total)

- **AMINO ACIDS, CORN GLUTEN → `gluten_free`.** Despite the name, corn "gluten" (zein)
  is NOT the same protein as wheat gluten. Corn is not a gluten-containing grain per
  FDA 21 CFR 101.91. UNII: 0540V8ZD7V.

- **Highest-impact new classification: ALUMINUM STARCH OCTENYLSUCCINATE → `unknown`
  (861 products).** Modified starch used as an absorbent in topical products. Source not
  specified on the label. Per project rules, source-unspecified starch derivatives are
  flagged unknown. This single new term is larger than the entire pilot's `unknown`
  category (166 products).

- **HYDROXYETHYL STARCH 130/0.4 → `unknown` (1 product).** Pharmaceutical-grade HES is
  invariably derived from waxy maize (corn) per industry practice, but the label does not
  specify the source. Per project rules (label-based, not industry-knowledge-based), this
  is flagged unknown for consistency with the pilot's STARCH (unspecified) treatment.

- **GLUCOSE family → `gluten_free` (revised 2026-04-09).** GLUCOSE (42 products),
  GLUCOSE SYRUP, and LIQUID GLUCOSE were originally flagged `unknown`. Reclassified
  to `gluten_free` per current National Celiac Association guidance:
  *"Glucose syrup is considered safe even when derived from wheat, barley or rye
  because the process used to produce glucose syrup renders the starting material
  to contain less than 20 parts per million of gluten. Dextrose is simply another
  word for glucose. It is considered gluten free regardless of the starting material."*
  Source: https://nationalceliac.org/ingredients-people-question/
  GLUCOSE SYRUP and LIQUID GLUCOSE are pilot entries — overrides applied via the
  PILOT_OVERRIDES dict in `scripts/build_validation_table.py`. The pilot CSV
  (`data/eda/excipient_validation.csv`) is left unchanged as a historical record.

- **All gums → `gluten_free`.** Plant exudate gums (acacia, mastic, boswellia, eucalyptus,
  karaya, styrax benzoin), legume gums (locust bean, guar, tara/Caesalpinia spinosa),
  bacterial fermentation gums (gellan, diutan, rhizobian, biosaccharide-1/-2/-4), fungal
  fermentation gum (sclerotium), and cellulose gum (sodium CMC, wood pulp/cotton-derived)
  are all gluten-free. Dehydroxanthan gum follows the xanthan gum classification per
  National Celiac Association guidance.

- **Pilot entries get bulk catalog count appended to rationale.** Each pilot rationale
  is annotated with `Bulk catalog: N products.` to reflect new prevalence in the full
  catalog. The pilot rationale text is otherwise preserved unchanged. Notable changes:
  - SODIUM STARCH GLYCOLATE TYPE A: pilot 154 → bulk 1,123 products
  - XANTHAN GUM: pilot 727 → bulk 9,268 products
  - STARCH, CORN: pilot 2,801 → bulk 26,409 products
  - WHEAT (standalone): pilot 0 → bulk 22 products
  - BARLEY (standalone): pilot 0 → bulk 89 products
  - RYE (standalone): pilot 0 → bulk 4 products

- **Cyclodextrins added — interim `gluten_free` (2026-04-09).** 15 cyclodextrin/betadex
  string variants (CYCLODEXTRINS, CYCLODEXTRIN, BETADEX, HYDROXYPROPYL BETADEX,
  BETADEX SULFOBUTYL ETHER SODIUM, the alpha/beta/gamma variants, ADRABETADEX, and the
  substitution-degree variants) cover 559 product appearances across 381 unique products.
  None matched the original 20 keywords (no "cyclodextrin" or "betadex" keyword), so they
  were missed by the keyword search and added later via cross-reference against the
  Gluten Intolerance Group (GIG) "Medications and the Gluten-Free Diet" PDF (Jan 2019).
  ⚠️ The GIG source is >5 years old (stale per the project's 5-year cutoff for fast-moving
  fields). Cyclodextrin classification is interim, pending pharmacist consultation
  (see Q3 in `analysis/validation_table_review.md`). NOTE: cyclodextrins are CYCLIC
  oligosaccharides and chemically distinct from MALTODEXTRIN (a LINEAR polysaccharide) —
  their classifications are NOT chained.

- **ICODEXTRIN → `gluten_free` (2026-04-09).** Linear starch hydrolysate used as an
  osmotic agent in peritoneal dialysis solutions. 186 products. Chains from MALTODEXTRIN
  classification (current NCA + FDA IIG sources). Does NOT depend on the GIG 2019 source.

- **MALTODEXTRIN/VP COPOLYMER (1000 MPA.S) → `gluten_free` (2026-04-09).** Copolymer of
  maltodextrin (linear starch hydrolysate, gluten_free) and vinylpyrrolidone (synthetic
  monomer). 2 products. Chains from MALTODEXTRIN classification.

- **Source provenance rule.** All classification decisions must cite a source. Sources
  are flagged as **current** (within 5 years) or **stale** (older). Decisions resting
  only on stale sources are flagged for re-evaluation. The 5-year cutoff applies because
  celiac science and pharmaceutical labeling guidance evolve quickly. Currently the only
  decision resting on a stale source is the cyclodextrin family (GIG 2019).

### Bulk Filtering Decisions (2026-04-10)
These decisions apply to the 6-step filter pipeline that restricts the bulk DailyMed
catalog to the analysis-ready dataset. Implemented in `scripts/filter_bulk.py`.

- **Methodology statement.** The dataset includes only **FDA-recognized human
  medications that are directly delivered to the GI tract by swallowing**. Excluded:
  biologics, animal products, dietary supplements, devices, cosmetics, bulk ingredients,
  mouth-only delivery (lozenges, mouthwash, dental, sublingual, buccal), inhaled,
  injected, topical, transdermal, homeopathic preparations, herbal/traditional
  supplements, foreign-imported unapproved products, and grandfathered marketed-
  unapproved drugs.

- **Filter order does not change the final result.** All 6 filters are independent
  column conditions combined with AND. The order shown below was chosen for audit
  readability, not correctness. Re-running the pipeline in any order produces an
  identical 72,358-row output.

- **Pipeline is fully deterministic.** No AI / LLM / inference at any step. Every
  filter is a pandas equality check, set membership test, or word-boundary regex.
  The validation table used in the downstream flagging step (`scripts/flag_bulk.py`)
  is a static CSV produced earlier by `build_validation_table.py`.

- **Step 1 — `document_type` filter.** Keep only the four human drug label types:
  HUMAN OTC DRUG LABEL, HUMAN PRESCRIPTION DRUG LABEL, HUMAN PRESCRIPTION DRUG LABEL
  WITH HIGHLIGHTS, HUMAN COMPOUNDED DRUG LABEL. Drops 6,507 rows
  (199,961 → 193,454). Removed: biologics (vaccines, plasma derivatives, allergenics,
  cellular/gene therapy), animal products, dietary supplements, medical devices,
  cosmetics, bulk ingredients, indexing entries. Examples dropped: "Smut, Bermuda
  Grass" (Allermed Laboratories — non-standardized allergenic), "Lyfgenia" (Genetix
  Biotherapeutics — cellular therapy), "Oxibendazole" (Professional Group of
  Pharmacists — bulk ingredient).

- **Step 2 — `bulk_category` filter.** Drop `homeopathic`. Drops 19,940 rows
  (193,454 → 173,514). Per the user's "FDA-recognized real medications only"
  criterion, homeopathic preparations are excluded entirely. Examples dropped:
  "Bowel Nosode B Faecalis" (Apotheca Company), "Gelsemium Sempervirens" (Standard
  Homeopathic Company), "CS Brain" (King Bio Inc.).

- **Step 3 — `route` filter.** Keep only `route = ORAL`. Drops 96,334 rows
  (173,514 → 77,180). Removed all topical, injection, inhalation, ophthalmic,
  dental, sublingual, buccal, oropharyngeal, enteral, transmucosal, intragastric,
  and other non-oral routes. Examples dropped: "Pharmacy's Prescription Hand
  Sanitizer" (TOPICAL liquid), "Sun Bum Signature SPF 30 Sunscreen Lip Balm"
  (TOPICAL stick), "Mineral Sun Silk Moisturizer Sunscreen" (TOPICAL cream).
  Rationale: gluten in an excipient can only reach a celiac patient's GI tract
  via swallowed delivery.

- **Step 4 — `dosage_form` filter.** Drop dosage forms that are not swallowed,
  in three groups:
  - **Group A — mouth-only delivery (not swallowed):** LOZENGE, MOUTHWASH,
    GUM (CHEWING), PASTE (DENTIFRICE), POWDER (DENTIFRICE), GEL (DENTIFRICE),
    RINSE, PASTE, PASTILLE, TROCHE.
  - **Group B — wrong-route data errors (route says ORAL but the form is for a
    different route):** INJECTION (all variants), AEROSOL/INHALANT/METERED-SPRAY
    (all variants), CREAM, LOTION, OINTMENT, SWAB, SPONGE, DRESSING, PATCH.
  - **Group C — other not-swallowed forms:** SPRAY, GEL, FILM, FILM (SOLUBLE),
    STRIP, TABLET (ORALLY DISINTEGRATING) and its delayed-release variant.
  Drops 3,174 rows (77,180 → 74,006). Examples dropped: "BIOTENE" (PASTE),
  "CVS Wild Cherry Throat Drop" (LOZENGE), "Tyvaso DPI" (INHALANT), "Pro-Den Rx"
  (GEL), "Doctor's Choice" (GEL, DENTIFRICE).
  - **Kept dosage forms (per user decision):** KIT (multi-component packages —
    1,292 rows), PELLET non-homeopathic (real prescription pellet capsules like
    Pradaxa, Entresto, Hep C drugs — 38 rows), CRYSTAL (Epsom salt as oral saline
    laxative — 3 rows), and all standard tablets / capsules / liquids / suspensions /
    syrups / chewables / extended- and delayed-release forms.
  - **Inconsistency note:** dissolvable films (e.g. orally disintegrating films,
    Suboxone film, Viagra film) and orally disintegrating tablets (Zofran ODT,
    Claritin RediTabs) were both dropped under the same rule. The active
    ingredient is mostly absorbed via buccal/sublingual mucosa rather than
    reaching the GI tract via swallowing. The user accepted dropping ODTs
    explicitly.

- **Step 5 — `approval_type` filter.** Keep only FDA-recognized real medications:
  ANDA, NDA, NDA AUTHORIZED GENERIC, BLA, OTC MONOGRAPH DRUG (all spelling/case
  variants: "OTC Monograph Drug", "OTC monograph final", "OTC monograph not final").
  Drops 1,619 rows (74,006 → 72,387). Removed: `unapproved drug other` (1,445),
  `export only` (106), `unapproved homeopathic` (48 — homeopathics that escaped
  Step 2), `unapproved drug for use in drug shortage` (8), `unapproved medical gas`
  (4), `dietary supplement` (4), `cosmetic` (2), `Emergency Use Authorization` (2).
  - **Trade-off explicitly accepted:** the `unapproved drug other` bucket contains
    both real grandfathered medications (Phenobarbital, Phenazopyridine, Hyoscyamine,
    Salsalate, Armour Thyroid, NP Thyroid, Donnatal, Effer-K) AND non-medications
    (herbal supplements, Korean traditional medicine, foreign imports, vitamin
    combinations). Manual classification of the 400 unique active ingredients in
    that bucket was considered but rejected in favor of the cleaner "FDA-recognized"
    cut. Real grandfathered medications are excluded as a documented limitation.
  - Examples dropped: "Foltamin" (PureTek Corporation — vitamin combo, unapproved
    drug other), "Borax" (Warsan Homeopathic — unapproved homeopathic),
    "Acetaminophen 325 mg" (Granules India — export only), "INATAL Ultra"
    (Nnodum Pharmaceuticals — unapproved drug other), "Apis Mellifica" (Warsan
    Homeopathic — unapproved homeopathic).

- **Step 6 — Mouthwash-by-name slip cleanup.** Drop the 29 rows where `drug_name`
  contains "MOUTHWASH" / "MOUTH WASH" / "MOUTH RINSE" / "MOUTH GARGLE" / "GARGLE"
  but `dosage_form` is something other than MOUTHWASH (LIQUID in 27 cases, plus
  one SOLUTION and one TABLET CHEWABLE). These are mouthwash products that bypassed
  Step 4 because of inconsistent SPL labeling at the source. Examples dropped:
  "Mouthwash" (Discount Drug Mart, LIQUID), "SEACALL Mouthwash" (Guangdong Quadrant,
  LIQUID), "Prevention Oncology Mouth Rinse" (Prevention Health Sciences, LIQUID),
  "Amber Mouth Rinse" (Filo America, LIQUID).

- **Final dataset.** `data/bulk/dailymed_bulk_filtered.csv` — **72,358 rows ×
  43 columns** (all original raw columns preserved). Breakdown by `bulk_category`:
  56,400 human_prescription + 15,958 human_otc. The downstream `flag_bulk.py` script
  reads this file, applies the validation table, and writes
  `data/bulk/dailymed_bulk_flagged.csv` with two added columns (`gluten_flag`,
  `flagged_excipients`). Final flag distribution: gluten_free 68,277 (94.36%),
  no_data 3,041 (4.20%), unknown 1,028 (1.42%), contains_gluten 12 (0.02%).

---

## Critical Instructions for Claude

### Flag Assumptions Explicitly
Whenever you make an assumption — about methodology, data interpretation, 
terminology equivalence, or anything else — flag it clearly using this format:

> ⚠️ **ASSUMPTION:** [state the assumption] — [explain why you made it and 
> what the alternative interpretations are]

Do not bury assumptions in prose. Surface them prominently so the journalist 
can make informed decisions. Copy all assumption flags into SESSION_LOG.md 
at the end of the session.

### Cite Sources for All Claims
Every factual claim that is not directly from the source paper must include 
a citation or source reference. Acceptable sources include:
- FDA official documentation and databases
- Peer-reviewed journal articles
- CDC, NIH, or other federal health agencies
- Celiac Disease Foundation or equivalent patient advocacy organizations

Format citations clearly at the end of any section where they appear.
Do not make unsourced claims about celiac disease prevalence, gluten thresholds, 
FDA regulations, or medication safety.

### Never Overwrite Raw Data
`data/dailymed_bulk_raw.csv` and `data/eda/dailymed_raw.csv` are sacred.
If re-extraction is needed, save as a new versioned file and note the reason
in SESSION_LOG.md.

### Tone
Keep analysis rigorous but translate findings into plain language. 
This is journalism, not a clinical paper.