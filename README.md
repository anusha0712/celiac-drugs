# Hidden Drug Allergens in US Drug Labels

A science-journalism research repository analyzing whether US drug labels give
patients enough information to identify medications that contain four common
allergens — **gluten, milk proteins / lactose, polyethylene glycol (PEG), and
carmine / cochineal extract**. Built around DailyMed (the FDA's public drug
label database), every classification rule traces to a primary source (FDA
regulations, peer-reviewed literature, USP-NF compendial monographs, FARE
ingredient lists, GSRS UNII synonym records). The central question is not
*"do these drugs contain allergen X?"* but *"can the patient tell from the
label?"* — a labeling-transparency and regulatory-gap story, not a toxicology
story.

---

## Background context

### Why allergens in drug labels matter

Medications use **inactive ingredients** (excipients) as binders, fillers,
disintegrants, and coatings. Some excipients can trigger reactions in
patients with documented allergies or hypersensitivities. Unlike food labels,
US drug labels are **not required** to call out allergen-containing
excipients in plain language. The Food Allergen Labeling and Consumer
Protection Act (FALCPA, 2004) explicitly excludes drugs (Pub. L. 108-282
§203(a); 21 U.S.C. 343(w)). The only FDA-mandated allergen warning rules for
drugs are the sulfite warning (21 CFR 201.22) and the FD&C Yellow No. 5
warning (21 CFR 201.20). No comparable mandate exists for gluten, milk, PEG,
or carmine.

### The three-layer regulatory gap

This repository's findings sit under a single structural gap, the same shape
for every allergen studied:

1. **Class rule.** No FDA rule requires allergen-specific warning text in
   drug labels. The two exceptions (sulfites, FD&C Yellow No. 5) prove the
   rule.
2. **Product inconsistency.** Where voluntary warnings exist (Advair Diskus
   family for milk; PEG 3350 Rx bowel preps), some equivalent generics carry
   the warning and others do not. No rule mandates consistency across
   ANDA-equivalent products.
3. **Silent listing.** When an allergen-source excipient is listed in the
   inactive-ingredients block, in most cases no warning text accompanies it.

### What is DailyMed?

[DailyMed](https://dailymed.nlm.nih.gov) is the FDA's official repository of
drug labeling information. It is the tool the FDA recommends patients and
healthcare providers use to look up drug labels. Each label is stored as a
Structured Product Labeling (SPL) XML document following the HL7 standard.
Every analysis here is built from a single DailyMed bulk-download snapshot
(April 6, 2026; 199,961 NDC-level rows after extraction).

### The four allergens

All headline numbers are post-baseline filter (FDA-recognized human
medications only — homeopathic, unapproved, dietary supplements, and
non-drug labels removed; 165,757 of the original 199,961 catalog rows
remain). See `methodology.md` and per-allergen `findings_*.md` for
slicing detail.

| Allergen | Primary-source list | Harm anchor (peer-reviewed) | Headline number |
|---|---|---:|---:|
| **Gluten** | 21 CFR 101.91 (wheat / rye / barley) + Figueiredo 2025 (Sci Rep 15:10976) excipient list | Catassi 2007: 50 mg/day causes intestinal damage in celiac patients | 94.36% gluten_free / 1.42% unknown / 0.02% contains_gluten. |
| **Milk proteins** | FARE milk-allergen ingredient list (lactose family + lactulose removed 2026-05-05 per pharmacist review — purified milk sugars are not protein allergens) | Nowak-Wegrzyn 2004 (PMID 15007361): Advair Diskus DPI anaphylaxis in milk-allergic patients | 115 of 165,757 (0.07%). Oral 36 / 75,435 (0.05%). DPI: 0 of 29 strict-DPI NDCs (0%); 18 of 19 set_ids still carry §4 contraindication language. |
| **PEG (polyethylene glycol)** | USP-NF PEG monograph (tight scope: POLYETHYLENE GLYCOL, POLYETHYLENE OXIDE, MACROGOL, CARBOWAX) | Stone 2019 (PMID 30557713): 2 PEG 3350 anaphylaxis index cases + 53 FAERS reports | 27,956 of 165,757 (16.87%). Oral-solids slice 23,834 / 64,123 (37.17%). 0 of 16,293 parseable label set_ids carry a PEG-allergy warning. |
| **Carmine / cochineal** | 21 CFR 73.100 permitted names + GSRS UNII synonyms (TZ8Z31B35M, CID8Z8N95N) | Greenhawt 2009 (PMID 19331724): generic azithromycin tablet anaphylaxis in carmine-allergic patient | 161 products (NDC-level) / 141 set_ids (SPL-level). 0 of 138 parseable set_ids carry carmine-allergy language. |

The Portuguese source study (Figueiredo et al. 2025, *Scientific Reports* 15:10976,
[DOI](https://doi.org/10.1038/s41598-025-95525-6)) was the methodology anchor
for the gluten workflow. Its 308-drug INFOMED dataset reported 44.4% of
paracetamol products and 8.2% of ibuprofen products as "non-gluten-free" —
but **zero** contained a confirmed gluten grain. The figure represented
labeling ambiguity, not confirmed gluten presence. This repository extends
the same labeling-transparency framing to milk, PEG, and carmine.

### Real patient harm — not theoretical

- **Gluten:** PMC10958639 (2024 case report) — celiac patient experienced
  clinical harm from wheat starch in a prednisone formulation; no way to
  identify the risk from the label.
- **Milk:** Nowak-Wegrzyn 2004 (PMID 15007361), Robles 2014 (PMID 25309152),
  Bar-On 2022 (PMID 36555964), Hatcher 2025 (PMID 40958177) — DPI lactose
  carrier anaphylaxis in milk-allergic patients; trace bovine casein detected
  in IV methylprednisolone vials.
- **PEG:** Stone 2019 (PMID 30557713), Wolfson 2021 (PMID 34166844),
  Greenhawt 2023 (PMID 36321821) — PEG 3350 anaphylaxis FAERS cases;
  post-mRNA-vaccine PEG/polysorbate skin-test cohort.
- **Carmine:** Greenhawt 2009 (PMID 19331724), Takeo 2018 (PMID 29705083),
  Sadowska 2022 (PMID 35369613), Khalil 2025 (PMID 41113612) — only US
  medication-induced carmine anaphylaxis case (generic azithromycin tablet);
  Japanese case series; Polish urticaria cohort; recurrent anaphylaxis
  resolved on carmine elimination.

---

## Repository structure

```
celiac-drugs/
├── README.md                          ← this file
├── CLAUDE.md                          ← project instructions, methodology decisions, governing
├── SESSION_LOG.md                     ← chronological per-session record
├── TASKS.md                           ← cross-session task list
├── FDA-IID-recent-update.csv          ← FDA Inactive Ingredient Database snapshot (2026-04-22)
│
├── scripts/
│   ├── extract_fullcatalog_raw.py         ← full-catalog extraction (bulk ZIPs → CSV)
│   ├── build_gluten_excipient_list.py     ← keyword search; builds research worklist
│   ├── build_gluten_validation.py         ← assembles gluten validation CSV
│   ├── filter_gluten_fullcatalog.py       ← 6-step filter pipeline (gluten scope)
│   ├── flag_gluten_fullcatalog.py         ← apply gluten flags to filtered catalog
│   ├── analyze_gluten_fullcatalog.py      ← gluten prevalence + slices
│   ├── build_allergens_validation.py      ← assembles milk + PEG + carmine validation tables
│   ├── flag_allergens_fullcatalog.py      ← apply 3 allergen flags to RAW catalog
│   ├── analyze_allergens_fullcatalog.py   ← allergen prevalence + slices
│   ├── analyze_dpi_labels.py              ← DPI milk-warning SPL analysis
│   ├── analyze_peg_labels.py              ← PEG-warning SPL analysis
│   ├── analyze_carmine_labels.py          ← carmine-warning SPL analysis
│   ├── allergen_filters.py                ← shared DPI / oral-solid / oral filter functions
│   ├── spl_label_parser.py                ← shared SPL XML parser (Rx + OTC sections)
│   ├── fda_iid_lookup.py                  ← FDA IID local-CSV loader
│   └── build_corpus_tests.py              ← deterministic corpus-test generator
│
├── data/
│   └── fullcatalog/                                      ← full-catalog derived files
│       ├── dailymed_fullcatalog_raw.csv                  ← raw 199,961 rows (gitignored, 173 MB)
│       ├── gluten_fullcatalog_filtered.csv               ← post-6-step filter (gitignored, 60 MB)
│       ├── gluten_fullcatalog_flagged.csv                ← + gluten flag (gitignored, 61 MB)
│       ├── gluten_validation.csv                         ← gluten validation table (171 entries)
│       ├── gluten_excipient_research_worklist.csv        ← intermediate (new terms researched)
│       ├── milk_validation.csv                           ← milk validation (27 rows, FARE-anchored, post pharmacist review 2026-05-05)
│       ├── peg_validation.csv                            ← PEG validation (4 regex, USP-NF-anchored)
│       ├── carmine_validation.csv                        ← carmine validation (24 rows, 21 CFR + GSRS)
│       ├── allergens_fullcatalog_flagged.csv             ← raw + 6 allergen-flag cols (gitignored, 174 MB)
│       ├── dpi_label_analysis.csv                        ← DPI milk-warning per set_id
│       ├── peg_label_analysis.csv                        ← PEG-warning per set_id
│       ├── carmine_label_analysis.csv                    ← carmine-warning per set_id
│       └── corpus_test_{milk,peg,carmine}.csv            ← deterministic corpus regression
│
├── bulk-data/                         ← raw DailyMed bulk download (April 6, 2026; gitignored)
│   ├── human-otc/                     ← ~87K ZIPs across 11 subfolders
│   ├── human-prescription/            ← ~54K ZIPs across 6 subfolders
│   ├── homeopathic/                   ← ~16K ZIPs in 1 subfolder
│   └── other/                         ← ~2.5K ZIPs in 1 subfolder (remainder labels)
│
└── analysis/
    └── allergens/
        ├── methodology.md             ← cross-allergen methodology (Parts 1-7)
        ├── narrative_draft.md         ← cross-allergen narrative draft
        ├── limitations.md             ← per-allergen limitations
        ├── literature.md              ← annotated bibliography
        ├── reconciliation_pass.md     ← cross-workflow consistency tracker
        ├── gluten/
        │   ├── source_paper_critique_gluten.md        ← critique of Figueiredo 2025
        │   ├── findings_fullcatalog_gluten.md         ← full-catalog findings (gitignored draft)
        │   └── validation_table_review_gluten.md      ← gluten validation table review
        ├── milk/
        │   ├── research_milk.md                       ← primary-source brief
        │   └── findings_milk.md                       ← milk findings
        ├── peg/
        │   ├── research_peg.md
        │   └── findings_peg.md
        └── carmine/
            ├── research_carmine.md
            └── findings_carmine.md
```

---

## Naming conventions glossary

| Token | Meaning |
|---|---|
| `fullcatalog` | The April 2026 DailyMed bulk-download snapshot — all 199,961 NDC-level rows across every drug. |
| `gluten` | Gluten-specific scripts and data. Uses the 4-tier flag system (`gluten_free` / `unknown` / `contains_gluten` / `no_data`). |
| `allergens` | Batch grouping for the milk + PEG + carmine work. Three flags emitted per row by a single `flag_allergens_fullcatalog.py` pass. Each uses the 3-tier system (`contains_<allergen>` / `<allergen>_free` / `no_data`). |

So `flag_gluten_fullcatalog.py` flags the gluten-filtered full-catalog dataset
for gluten; `flag_allergens_fullcatalog.py` flags the unfiltered raw full
catalog for milk + PEG + carmine in one pass.

---

## How to reproduce

### Prerequisites

- **Python 3.9+** with the standard library (no third-party packages required;
  the pipeline uses only `csv`, `re`, `xml.etree`, `pathlib`, `zipfile`, `sys`).
- **DailyMed bulk download** at `bulk-data/{human-otc,human-prescription,
  homeopathic,other}/`. Download from
  <https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm>.
  ~159,431 ZIP files; ~22 GB unzipped.
- **`FDA-IID-recent-update.csv`** at the project root. Download the FDA
  Inactive Ingredient Database from
  <https://www.fda.gov/drugs/drug-approvals-and-databases/inactive-ingredients-database-download>
  and convert to CSV (or use the in-repo snapshot if present).

All scripts use `Path(__file__).parent.parent` to resolve to the project root,
so they should be run from the project root:

```bash
python3 scripts/<script_name>.py
```

### Pipeline 1 — Gluten full catalog

```bash
# 1. Extract the entire bulk download → 199,961 raw rows (~30 min)
python3 scripts/extract_fullcatalog_raw.py
#    → data/fullcatalog/dailymed_fullcatalog_raw.csv

# 2. Filter to FDA-recognized swallowed human medications (6-step pipeline; ~2 min)
python3 scripts/filter_gluten_fullcatalog.py
#    → data/fullcatalog/gluten_fullcatalog_filtered.csv (~72,358 rows)

# 3. Build / refresh gluten validation table (deterministic)
python3 scripts/build_gluten_excipient_list.py    # → research worklist
python3 scripts/build_gluten_validation.py        # → 171-entry table

# 4. Apply gluten flags (~1 min)
python3 scripts/flag_gluten_fullcatalog.py
#    → data/fullcatalog/gluten_fullcatalog_flagged.csv

# 5. Run full-catalog analysis
python3 scripts/analyze_gluten_fullcatalog.py
```

### Pipeline 2 — Allergens full catalog (milk + PEG + carmine)

This pipeline starts from the **raw** catalog (not the gluten-filtered one),
because the milk harm anchor is dry-powder inhalers — which the gluten
pipeline drops at filter step 3.

```bash
# 1. Build the three allergen validation tables (FARE / USP-NF / 21 CFR + GSRS anchored)
python3 scripts/build_allergens_validation.py
#    → data/fullcatalog/{milk,peg,carmine}_validation.csv

# 2. Apply 3 allergen flags to RAW catalog in one pass (~5 min)
python3 scripts/flag_allergens_fullcatalog.py
#    → data/fullcatalog/allergens_fullcatalog_flagged.csv (199,961 rows × 49 cols)

# 3. Compute prevalence + slices for findings docs
python3 scripts/analyze_allergens_fullcatalog.py
```

### Pipeline 3 — Per-allergen contraindication-level label analysis

For each allergen, parse SPL XML for every set_id flagged
`contains_<allergen>` and classify warning level: §4 contraindication / boxed
warning / §5 warning / OTC allergy alert / silent. Patterns require an
allergy-context token within 80 chars of the allergen name (see
`methodology.md` §5).

```bash
# DPI milk warnings (~1 min; 19 set_ids)
python3 scripts/analyze_dpi_labels.py
#    → data/fullcatalog/dpi_label_analysis.csv

# Carmine warnings (~1 min; 156 set_ids)
python3 scripts/analyze_carmine_labels.py
#    → data/fullcatalog/carmine_label_analysis.csv

# PEG warnings (~15-20 min; 16,760 set_ids in oral-solids slice)
python3 scripts/analyze_peg_labels.py
#    → data/fullcatalog/peg_label_analysis.csv
```

### Pipeline 4 — Corpus tests (regression check)

A deterministic regression generator. Run after any change to the validation
tables to see exactly which DailyMed excipient strings each rule matches
(or doesn't).

```bash
python3 scripts/build_corpus_tests.py
#    → data/fullcatalog/corpus_test_{milk,peg,carmine}.csv
```

Re-running the script on identical inputs produces byte-identical CSVs
(MD5-verified). The output flags every "inactive" rule (rule defined in the
validation table but no DailyMed string matches it under the current
snapshot) for transparency.

---

## Where to read findings

| You want to read about… | Read this |
|---|---|
| Cross-allergen narrative draft (the journalism piece) | `analysis/allergens/narrative_draft.md` |
| Methodology — shared architecture + per-allergen | `analysis/allergens/methodology.md` |
| Per-allergen limitations | `analysis/allergens/limitations.md` |
| Annotated bibliography (PMIDs, CFR, FDA, EMA, FARE, USP-NF) | `analysis/allergens/literature.md` |
| Cross-workflow consistency tracker | `analysis/allergens/reconciliation_pass.md` |
| Gluten — Portuguese source study critique | `analysis/allergens/gluten/source_paper_critique_gluten.md` |
| Gluten — full-catalog findings | `analysis/allergens/gluten/findings_fullcatalog_gluten.md` |
| Gluten — validation table review | `analysis/allergens/gluten/validation_table_review_gluten.md` |
| Milk — primary-source research brief | `analysis/allergens/milk/research_milk.md` |
| Milk — findings (DPI harm anchor + oral catalog) | `analysis/allergens/milk/findings_milk.md` |
| PEG — primary-source research brief (incl. excluded adjacent families) | `analysis/allergens/peg/research_peg.md` |
| PEG — findings (oral-solids slice + warning-section silence) | `analysis/allergens/peg/findings_peg.md` |
| Carmine — primary-source research brief | `analysis/allergens/carmine/research_carmine.md` |
| Carmine — findings (landscape view, no pre-filtering) | `analysis/allergens/carmine/findings_carmine.md` |

---

## Warning-pattern vocabulary (`ALLERGY_CONTEXT`)

The label-analysis scripts (`analyze_dpi_labels.py`,
`analyze_peg_labels.py`, `analyze_carmine_labels.py`) detect whether an SPL
warning section genuinely discusses an allergen's allergic reactions, as
opposed to merely listing the allergen name as an ingredient inside that
section. A warning match requires both an allergen name AND an allergy-context
token within 80 characters of each other:

```python
ALLERGY_CONTEXT = r"(?:allerg|hypersens|anaphyla|contraindicat)"
```

The four token roots cover inflected forms (`allergy` / `allergic` /
`allergen` / `allergies`; `hypersensitivity` / `hypersensitive`;
`anaphylaxis` / `anaphylactic`; `contraindicated` / `contraindication`).
Anchored to:

- **21 CFR 201.22** — FDA sulfite warning mandate, the only FDA-mandated
  drug-allergy warning rule. Uses "allergic-type reactions … anaphylactic …
  life-threatening …"
- **AAAAI/ACAAI 2022 Drug Allergy Practice Parameter** (PMID 36122788) —
  peer-reviewed clinical vocabulary.
- **Advair Diskus §4 contraindication template** — "contraindicated in
  patients with severe hypersensitivity to milk proteins."

Bare-name patterns (e.g. `\bpolyethylene\s+glycol` alone) were explicitly
rejected after the 2026-04-23 reconciliation pass found three PEG label
"warnings" that were actually ingredient-list mentions inside boxed-warning
sections, not real warnings. The corrected count is 0 / 16,585 parseable
oral-solid PEG labels carry a PEG-allergy warning. Full discussion in
`analysis/allergens/methodology.md` §5 and
`analysis/allergens/reconciliation_pass.md` Fix 1.

---

## Known limitations

A summary. Full per-allergen detail in
`analysis/allergens/limitations.md`.

- **Label-based only.** No ELISA / HPLC measurement of actual allergen
  content. A product flagged `unknown` may contain zero allergen.
  Cross-contamination during manufacturing is undetectable from labels.
- **NDC-level unit of analysis.** A single SPL label can contain multiple
  NDC entries with different excipient profiles. Throughout, "176 carmine
  products" is NDC-level; "156 carmine set_ids" is SPL-label-level.
- **Snapshot in time.** Data pulled April 6, 2026. Formulations and labels
  change.
- **Per-allergen scope decisions documented elsewhere.** Gluten
  4-tier system + xanthan-gum reclassification (`limitations.md` §Gluten);
  PEG tight scope excluding polysorbates / poloxamers / Cremophor /
  Kollicoat / TPGS (`limitations.md` §PEG); milk lactulose reclassified
  to `contains_milk` per FARE (`limitations.md` §Milk); carmine
  word-boundary CARMINE regex to avoid CROSCARMELLOSE false-positive
  (`limitations.md` §Carmine).
- **Source study (Figueiredo 2025) is methodological reference, not
  statistical replication.** US samples are 19-21× larger than the
  Portuguese study. Direct percentage comparisons are reported with
  caveats.

---

## Manual verifications (pending)

1. **Pharmacist spot-check across milk, PEG, and carmine validation tables.**
   Every classification row carries a primary-source URL and an FDA IID
   status flag (`in_iid` / `not_in_iid` from the local
   `FDA-IID-recent-update.csv` snapshot). What's still missing is a
   pharmacist's pass through each row to confirm the source-URL
   classification matches pharmaceutical practice. Particularly important
   for borderline cases (cyclodextrin family, source-unspecified starches,
   hydroxyethyl starch, oats).

2. **Manual `regulations.gov` docket spot-check (FDA-1998-P-0032).**
   Programmatic access to regulations.gov returned HTTP 403 during fact
   check, so 2020-2026 filings were not fully enumerated. The 2009 FDA
   final rule (74 FR 207) said drugs would be addressed in a "separate
   rulemaking"; no such drug rulemaking has been issued in the 17 years
   since per Federal Register and FDA.gov searches through April 2026.
   Manual docket spot-check would close the open question by enumerating
   any post-2009 drug-carmine filings.

3. **Gluten validation table — borderline case review.** The 8-question
   pharmacist-consultation list in `analysis/allergens/gluten/validation_table_review_gluten.md`
   covers ASO, SSG, cyclodextrins, maltodextrin, HES 130/0.4, HSH,
   source-unspecified starches, and oats. Cyclodextrin classification
   specifically rests on a 2019 Gluten Intolerance Group source flagged
   stale; should be re-evaluated with current evidence.

4. **Verify human-drug coverage in animal bulk downloads.** The April 2026
   bulk extraction pulled the human-OTC, human-prescription, homeopathic,
   and remainder buckets only. Spot-check the animal-drug bulk downloads
   to confirm no manufacturer-side classification errors moved a human
   medication into an animal bucket.

---

## Citation

If you use this repository for journalism, research, or replication:

```
Hidden Drug Allergens in US Drug Labels.
Analysis of FDA DailyMed bulk download (April 6, 2026) for the labeling
transparency of gluten, milk, PEG, and carmine excipients.
GitHub repository [insert URL]. Snapshot date 2026-04-23.
```

Primary source bibliography in `analysis/allergens/literature.md`.
