# Gluten Excipients in US Medications: A Labeling Transparency Analysis

A science journalism project analyzing whether celiac patients can determine
from US drug labels whether their medications contain gluten-source excipients.
This replicates and extends the methodology of a
[Portuguese study (Figueiredo et al. 2025)](https://doi.org/10.1038/s41598-025-95525-6)
using US data from DailyMed, the FDA's public drug label database.

The central question is not "do these drugs contain gluten?" but rather "can a
celiac patient tell from the label?" This is a labeling transparency and
regulatory gap story, not a toxicology story.

---

## Background Context

### Celiac Disease and Excipients

Celiac disease is an autoimmune condition triggered by gluten (proteins in
wheat, rye, and barley) affecting roughly 2 million Americans (per NIDDK).
Daily ingestion of as little as 50mg of gluten can cause intestinal damage
(Catassi et al. 2007, *Alimentary Pharmacology & Therapeutics*). Medications
use inactive ingredients (excipients) as binders, fillers, and disintegrants
-- some of which are starch-based. If the starch comes from wheat, it contains
gluten. If it comes from corn or potato, it does not. The problem: drug labels
do not always say which.

### The Regulatory Gap

The Food Allergen Labeling and Consumer Protection Act (FALCPA, 2004) requires
wheat disclosure on food labels. It explicitly excludes drugs
(Pub. L. 108-282, Section 203(a); 21 U.S.C. 343(w)). There is no equivalent
federal requirement for drug labels. The FDA issued a draft guidance in 2017
recommending allergen disclosure in drug labeling, but it was never finalized.
The ADINA Act (H.R. 3821), which would extend allergen labeling to drugs, was
reintroduced in Congress in June 2025 but has not passed.

### Real Patient Harm

This is not a theoretical concern. A 2024 case report (PMC10958639) documents
a celiac patient who experienced clinical harm from wheat starch in a
prednisone formulation. The patient had no way to identify the risk from the
drug label.

### What Is DailyMed?

[DailyMed](https://dailymed.nlm.nih.gov) is the FDA's official repository of
drug labeling information. It is the tool the FDA recommends patients and
healthcare providers use to look up drug labels. Each label is stored as a
Structured Product Labeling (SPL) XML document following the HL7 standard.
These XML files contain machine-readable fields for active ingredients,
inactive ingredients (excipients), dosage form, route, manufacturer, NDC codes,
and more. DailyMed provides both a public API for searching and XML endpoints
for retrieving individual labels.

### The Portuguese Source Study

Figueiredo et al. (2025), "Presence of gluten and soy derived excipients in
medicinal products and their implications on allergen safety and labeling,"
published in *Scientific Reports* 15, 10976. The study examined 308 drugs
across three therapeutic categories in Portugal's INFOMED database. Key
findings for gluten:

- 44.4% of paracetamol (acetaminophen) products classified "non-gluten-free"
- 8.2% of ibuprofen products classified "non-gluten-free"
- 0% of antiasthmatics/bronchodilators

Critically: zero products in the study contained a confirmed gluten grain
(wheat, rye, barley). Every "non-gluten-free" classification came from starch
derivatives whose botanical source was unspecified on the label. The 44.4%
figure represents labeling ambiguity, not confirmed gluten presence.

NOTE: I did this to make sure the study is scientifically viable for our methodolody and is not just fake, biased, statistically inaccurate, contain bad scientists or something. The skills use Cochrane Risk of Bias, GRADE and scholar evaluation framework grounded in this paper: https://arxiv.org/abs/2510.16234. The skills are MIT liceses and have nearly 17.2k stars and 1.7k forks on the repo. Community acknowledged as robust. 

We are not following the exact methodology - didn't end up happening - but just as a starting point of the story.

Full paper: https://doi.org/10.1038/s41598-025-95525-6

---

## Repository Structure

```
celiac-drugs/
├── README.md                          <- this file
├── CLAUDE.md                          <- project instructions, methodology
│                                         decisions, phase tracking, rules
│                                         for Claude. Governing document.
├── SESSION_LOG.md                     <- chronological record of every
│                                         session: what was done, decisions,
│                                         assumptions flagged, open questions.
│
├── scripts/                           <- all data extraction and processing
│   ├── pull_dailymed.py               <- Pilot extraction (API → CSV,
│   │                                     acetaminophen + ibuprofen only).
│   ├── extract_bulk.py                <- Full-catalog extraction
│   │                                     (bulk ZIPs → CSV).
│   ├── build_excipient_list.py        <- Keyword search across bulk catalog
│   │                                     to discover gluten-adjacent terms.
│   └── build_validation_table.py      <- Assembles complete validation CSV
│                                         from pilot entries + new entries +
│                                         bulk-table revision overrides.
│
├── data/
│   ├── dailymed_bulk_raw.csv          <- Full DailyMed catalog. 199,961 rows
│   │                                     × 43 columns. Extracted from the
│   │                                     April 2026 bulk download. NEVER
│   │                                     modified after creation.
│   ├── bulk/                          <- Full-catalog derived files
│   │   ├── excipient_validation.csv   <- Complete validation table.
│   │   │                                 171 entries (48 pilot + 123 new).
│   │   │                                 Generated by build_validation_table.py.
│   │   └── excipient_research_worklist.csv  <- Intermediate file: new terms
│   │                                            from keyword search needing
│   │                                            classification.
│   └── eda/                           <- Pilot data (acetaminophen + ibuprofen)
│       ├── dailymed_raw.csv           <- Pilot raw pull. 6,605 rows × 39 cols.
│       ├── dailymed_flagged.csv       <- Pilot data + gluten flag columns.
│       └── excipient_validation.csv   <- Pilot validation table (48 entries).
│                                         Preserved unchanged as historical
│                                         snapshot of pilot-era decisions.
│
├── bulk-data/                         <- Raw DailyMed bulk download (April
│                                         2026): 159,431 ZIP files across
│                                         human-otc/, human-prescription/,
│                                         homeopathic/, other/.
│
└── analysis/
    ├── phase1_paper_analysis.md       <- Critical analysis of the Portuguese
    │                                     source study. Composite ScholarEval
    │                                     score: 2.9/5.
    ├── findings.md                    <- Pilot analytical results.
    ├── limitations.md                 <- Flagging methodology + known
    │                                     limitations of pilot.
    └── validation_table_review.md     <- Pending changes log for the bulk
                                          validation table, with source
                                          provenance for each decision and
                                          a pharmacist consultation list (Q1-Q8)
                                          for decisions awaiting expert review.
```

---

## Methodology

### Phase 1: Paper Analysis

Before collecting any US data, we critically evaluated the Portuguese source
study to determine whether it was solid enough to anchor a journalism piece and
whether US replication was viable. Two Claude skills were used:

- **scientific-critical-thinking** -- a structured framework for evaluating
  methodology, detecting bias, assessing evidence quality, evaluating claims,
  and checking logical consistency.

- **scholar-evaluation** -- the ScholarEval framework, which scores a paper
  across 8 dimensions (problem formulation, literature review, methodology,
  data collection, analysis, results, writing, citations) on a 1-5 scale.
  The paper scored 2.9/5: publishable as a preliminary descriptive survey,
  with significant caveats about conflating excipient names with allergen
  presence.

Verdict: the study is solid enough to anchor journalism IF the framing is
precise -- "patients can't tell from labels" rather than "drugs contain
gluten." US replication via DailyMed would actually be stronger due to
structured XML data and larger sample sizes.

Full analysis: `analysis/phase1_paper_analysis.md`

### Phase 2: Data Collection

Data was collected programmatically using `pull_dailymed.py`, a Python script
that hits DailyMed's public API. No AI agents browsed the web or scraped pages.


#### How the script works

**Step 1 -- Discover products.** The script calls DailyMed's JSON API
(`/services/v2/spls.json?drug_name=acetaminophen`) and paginates through all
results, 100 at a time. It collects a `set_id` (DailyMed's unique label
identifier) for every product matching "acetaminophen" or "ibuprofen." This
list is cached to `.setid_cache.json` so it never re-runs.

**Step 2 -- Download labels.** For each set_id, the script fetches the full SPL
XML document from DailyMed's XML endpoint
(`/services/v2/spls/{setid}.xml`). Each XML file is cached individually in
`.xml_cache/`. If the script is interrupted (Ctrl+C), it skips
already-downloaded files on restart. Rate limiting is adaptive: starts at 0.5s
between requests, backs off to 5-10s if DailyMed returns HTTP 429, then
gradually recovers.

**Step 3 -- Parse XML.** Each SPL document is structured HL7 XML. The script
walks the XML tree to extract 39 fields per product: drug name, NDC code,
dosage form, route, active ingredients (with UNII codes and strengths),
inactive ingredients (with UNII codes), manufacturer, approval info, marketing
status, physical characteristics (color, shape, imprint), and packaging info.
One SPL label can contain multiple `manufacturedProduct` blocks (different
NDCs or strengths) -- each becomes its own CSV row.

**Step 4 -- Write CSV.** All extracted data goes into `dailymed_raw.csv`.

#### Error recovery

The initial run produced 44 errors. Three recovery strategies were applied:

1. **Retry** -- recovered 29 products (transient network failures)
2. **DESCRIPTION prose parsing** -- recovered 10 prescription labels that used
   a different XML structure (no structured `<ingredient>` elements; excipients
   were embedded in freetext description sections)
3. **Web page scraping** -- recovered 3 labels with malformed XML by fetching
   the DailyMed web page and parsing the HTML instead
4. **Unrecoverable** -- 2 products returned 404 (removed from DailyMed between
   search indexing and retrieval). Logged in `pull_errors.txt`.

#### Misspelling sweep

DailyMed contains products with misspelled active ingredient names. The API
was searched for common misspellings of both drugs:

- "acetominophen": 5 hits. 2 added to dataset (Scot-Tussin products), 2
  excluded (propoxyphene, withdrawn from US market 2010), 1 already captured.
- "acetamenophen", "acetamiophen", "acetaminiphen": 0 hits each.
- "ibuprofin", "ibuprophen", "ibuprofein": 0 hits each.

#### Exclusions

- Injectable formulations (33 products: IV acetaminophen, IV ibuprofen) --
  removed because the analysis focuses on oral medications celiac patients
  swallow.
- Antiasthmatics/bronchodilators -- dropped entirely. The Portuguese study
  included them as a control group (inhalers don't use starch excipients, so
  always 0%). 

  I wanted to cut down work for EDA. 

#### Final dataset

6,605 products: 4,986 acetaminophen, 1,619 ibuprofen. Both single-ingredient
and combination products (e.g., Tylenol PM, NyQuil, Advil Cold & Sinus) are
included because that reflects the real OTC landscape celiac patients face.

### Phase 3: Analysis

Each product was classified using the excipient validation table (see next
section) and the results were cut by drug category, dosage form, OTC vs.
prescription, single vs. combination, and sources of uncertainty. A comparison
to the Portuguese findings was included with methodological context.

Full results: `analysis/findings.md`
Full limitations: `analysis/limitations.md`

### Phase 4: Full DailyMed Catalog Extraction

The pilot's 6,605-product dataset (acetaminophen + ibuprofen) was expanded to
the full DailyMed catalog. Method:

1. **Bulk download** of every DailyMed label as ZIP archives from
   https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm.
   159,431 ZIP files across four download categories: human OTC labels,
   human prescription labels, homeopathic labels, and remainder labels
   (vaccines, devices, bulk ingredients, dietary supplements, allergenics).
2. **`scripts/extract_bulk.py`** parses every ZIP, extracts 43 fields per
   product from the SPL XML, and writes `data/dailymed_bulk_raw.csv`.
   Result: 199,961 product rows, 0 errors.
3. No filtering at extraction time. All routes, all dosage forms, all drug
   categories. Filtering belongs in analysis, not extraction.
4. New `bulk_category` field distinguishes human_otc / human_prescription /
   homeopathic / other based on download source folder.
5. New `dea_schedule` field extracted from XML policy elements.
6. `brand_generic` classification is deterministic based on FDA application
   number prefix (ANDA → generic, NDA → brand, BLA → brand, otherwise →
   otc_monograph).

### Phase 5: Bulk Excipient Validation Table

The pilot's 48-entry validation table was insufficient for the full catalog,
which contains 10,019 unique excipient strings. Method:

1. **`scripts/build_excipient_list.py`** runs a word-boundary keyword search
   across all unique excipient strings using 20 keywords drawn from the
   Portuguese study, Latin botanical names for gluten grains, and starch
   chemistry terms. Output: a research worklist of new gluten-adjacent terms.
2. **`scripts/build_validation_table.py`** assembles the complete bulk
   validation table at `data/bulk/excipient_validation.csv` (171 entries:
   48 pilot + 123 new). Pilot entries are preserved with bulk catalog product
   counts appended; the pilot CSV itself remains unchanged. Three pilot
   entries (GLUCOSE SYRUP, LIQUID GLUCOSE, MALTODEXTRIN) have bulk-table
   revisions applied via a `PILOT_OVERRIDES` dict in the script.
3. New entries cover starch derivatives, gums, oat-related compounds,
   wheat/barley/rye derivatives, the cyclodextrin family, ICODEXTRIN,
   MALTODEXTRIN/VP COPOLYMER, and 21 keyword false positives flagged as
   `gluten_free` with explicit "Keyword false positive" rationales (Option A:
   the validation table is the single source of truth).
4. The cyclodextrin family (15 string variants) was added as interim
   `gluten_free` based on the Gluten Intolerance Group's January 2019 PDF
   "Medications and the Gluten-Free Diet." This source is older than the
   project's 5-year cutoff and is flagged as stale, pending pharmacist
   consultation.
5. **`analysis/validation_table_review.md`** rigorously catalogues every
   pending classification decision with explicit source provenance (current
   vs stale) and an "Open Questions for Pharmacist Consultation" list
   (Q1-Q8) for decisions that need expert input.

Final flag distribution in the bulk validation table: 105 gluten_free,
35 unknown, 31 contains_gluten.

---

## Excipient Classification System

### Three-Tier Flags

Every product gets one of four flags based on its inactive ingredients:

| Flag | Meaning |
|---|---|
| `contains_gluten` | At least one excipient is a confirmed gluten grain or explicitly names a gluten source (wheat, rye, barley) |
| `unknown` | At least one excipient is a starch or starch derivative whose source grain is not specified on the label. No excipient is confirmed gluten. |
| `gluten_free` | All excipients either specify a non-gluten source, are not grain-derived, or are not in the validation table |
| `no_data` | The label lists no inactive ingredients at all |

A product's flag is determined by its worst excipient: if any excipient is
`contains_gluten`, the product is `contains_gluten`. If none are confirmed
but any are `unknown`, the product is `unknown`. If all are clear, it's
`gluten_free`.

### What "Unknown" Means

A product flagged `unknown` **does not mean it contains gluten.** It means a celiac patient reading the label cannot determine whether the product is safe. The label says something
like "sodium starch glycolate" without specifying whether the starch comes
from corn (safe) or wheat (not safe). The flag measures an information gap,
not a safety hazard.

In practice, the vast majority of these products almost certainly contain
zero gluten -- pharmaceutical-grade starch glycolate is predominantly
potato- or corn-derived. But "almost certainly" is not the same as "the
label confirms it," and that gap is what this project measures.

### Key Judgment Calls

**Xanthan gum** -- Reclassified from `unknown` (matching the Portuguese study)
to `gluten_free` based on National Celiac Association guidance, which states
xanthan gum does not contain gluten. This was the single largest
classification decision: it moved 727 products from `unknown` to
`gluten_free`. Source: https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/

**Bare "starch" (no source specified)** -- Flagged `unknown`. FDA Compliance
Policy Guide 578.100 states that unqualified "starch" in the US is the common
name for corn starch. However, a celiac patient reading the label has no way
to know this regulatory technicality. The flag reflects patient-facing
information, not regulatory interpretation. (Note: whether CPG 578.100
actually applies to drug inactive ingredient labeling, or only to food, is an
open -- see Next Steps.)

**Croscarmellose sodium vs. sodium starch glycolate (SSG)** -- These are
frequently confused because the names sound similar, but they are completely
different compounds. Croscarmellose sodium is cellulose-based (derived from
wood pulp or cotton) and is inherently gluten-free regardless of source. SSG
is starch-based and depends on the source grain. Croscarmellose sodium is
flagged `gluten_free`; SSG without a specified source is flagged `unknown`.

**Maltodextrin** -- Flagged `gluten_free` despite "malt" in the name.
Maltodextrin is produced by partial hydrolysis of corn starch. It is
chemically unrelated to barley malt. Similarly, maltitol, ethyl maltol, and
isomalt are excluded from the validation table entirely -- the substring
"malt" is not sufficient to flag an excipient.

**Rice bran** -- Flagged `gluten_free`. Unspecified "bran" defaults to
`contains_gluten` (most common source is wheat), but when the label specifies
rice, it is evaluated by its source. Rice is not a gluten-containing grain
(21 CFR 101.91).

### The Validation Tables

There are two validation tables in this project:

**`data/eda/excipient_validation.csv`** (pilot) — 48 entries drawn from three
sources: the Portuguese study's Table 1 (14 EU excipient terms), the FDA
Inactive Ingredient Database (standard US naming), and actual strings observed
on product labels in the pilot's DailyMed data. Preserved unchanged as a
historical snapshot of pilot-era decisions.

**`data/bulk/excipient_validation.csv`** (bulk) — 171 entries (48 pilot +
123 new). Generated by `scripts/build_validation_table.py` from the pilot
table plus new entries discovered via keyword search across the full
DailyMed catalog. Three pilot entries have bulk-table revisions applied
via the script's `PILOT_OVERRIDES` dict (the pilot CSV itself is left
unchanged). Final flag distribution: 105 gluten_free, 35 unknown,
31 contains_gluten.

Each entry in either table includes the exact string to match against label
data, the flag decision, a rationale explaining the chemical identity, a
citation URL, and an EU equivalent name where applicable. All new excipients
were added with documented rationale and source — no blind additions.

`analysis/validation_table_review.md` catalogues pending changes with explicit
source provenance for every decision and lists open questions awaiting
pharmacist consultation.

---

## Role of AI in This Project

### What Claude Did


- **Designed the methodology.** The three-tier classification system, the
  excipient validation approach, the reporting structure were all designed by Claude in
  conversation with the user.
- **Built the excipient validation tables.** For the pilot, Claude extracted
  all 511 unique excipient strings from the 6,605-product dataset and built
  a 48-entry validation table. For the full catalog, Claude extracted all
  10,019 unique excipient strings from the 199,961-product bulk dataset, ran
  a keyword search to find gluten-adjacent terms, classified each with
  rationale and citations, and built a 171-entry validation table. All
  research used FDA documentation, current celiac organization guidance
  (National Celiac Association), and pharmaceutical references.
- **Critiqued the source study.** The Phase 1 paper analysis was produced using
  two Claude skills: `scientific-critical-thinking` and `scholar-evaluation`.

### What Claude Did NOT Do

- **No data was AI-generated.** Every data point comes from DailyMed's public
  API and XML endpoints. Claude did not fabricate, infer, or hallucinate any
  product data.
- **No clinical claims.** Claude did not assess whether any product is safe or
  unsafe for celiac patients. The analysis measures label information only.

### Claude Skills Used

Two specialized Claude skills were loaded for this project:

- **scientific-critical-thinking** -- Provides a structured framework for
  evaluating scientific claims: methodology critique, bias detection, evidence
  quality assessment, claim evaluation, and logical consistency checking. Used
  in Phase 1 (paper analysis) and Phase 3 (interpretation section of
  findings.md).
- **scholar-evaluation** -- The ScholarEval framework for structured
  assessment of scholarly work across 8 dimensions with quantitative scoring.
  Used in Phase 1 only.

Both skills are relevant to evaluating and contextualizing research. They had
no role in data collection or the technical pipeline.


---

## Known Limitations

A brief summary. Full documentation is in `analysis/limitations.md`.

- **Label-based only.** Actual gluten protein levels are not measured. A
  product flagged `unknown` may contain zero gluten.
- **Cross-contamination undetectable.** Manufacturing cross-contamination
  cannot be identified from labels.
- **KIT components not extracted.** 428 KIT products (multi-component
  packages like day/night combo packs) show `no_data` because the script
  parsed the KIT-level label, not the individual component parts inside it.
  The component data exists in the cached XML but was not extracted. See
  Next Steps, task 3.
- **DailyMed index completeness unverified.** We did not cross-reference
  against the FDA NDC Directory. Products missing from DailyMed's search
  index would be absent from our dataset. However, DailyMed is supposed to be the most complete and up-to-date database of labels and something the FDA recommends for patients. 
- **Snapshot in time.** Data pulled March 26, 2026. Formulations and labels
  change.
- **Pilot scope: two drug categories.** The pilot dataset (Phases 1-3)
  covered only acetaminophen and ibuprofen. The full DailyMed catalog
  (Phases 4-5) covers all drug categories — 199,961 products — but the
  flagging pipeline that applies the validation table to the full catalog
  has not yet been written.
- **No dose-level analysis.** Excipient quantity per dose is not analyzed.

---

## Key Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Unit of analysis | NDC (not set_id) | Two NDCs under the same SPL label can have different excipient profiles. The NDC is what a patient encounters on the shelf. |
| Xanthan gum classification | `gluten_free` | Per National Celiac Association guidance. Methodological departure from Portuguese study. Moved 727 products from `unknown` to `gluten_free`. |
| Include combination products | Yes | Reflects the real OTC landscape celiac patients face. Source study also included all products "containing paracetamol/ibuprofen." |
| Drop antiasthmatics | Yes | 0% findings in source study. Inhalers don't use starch excipients. No journalistic value. |
| Bare "starch" flag | `unknown` | FDA CPG 578.100 says it legally means corn starch, but patients can't know that from the label. |
| Data source | 100% DailyMed | The tool FDA recommends patients use. OpenFDA was rejected due to ~40% coverage gap. |
| Include OTC and Rx | Both, reported separately | Matches source study. Both populations are relevant. |
| Exclude injectables | Yes | Analysis focuses on oral medications patients swallow. |
| Misspellings | Searched and added | DailyMed contains misspelled drug names. 2 products added from "acetominophen" search. |

---

## Next Steps / Open Tasks

1. **Apply the bulk validation table to the full catalog.** Write
   `scripts/flag_bulk.py` to read `data/dailymed_bulk_raw.csv` (199,961 rows)
   and `data/bulk/excipient_validation.csv` (171 entries), apply gluten flags
   per the worst-excipient rule, and write `data/bulk/dailymed_bulk_flagged.csv`.
   This is the immediate next step after the validation table is finalized.

2. **Resolve pending validation table decisions.** See
   `analysis/validation_table_review.md` for the catalogued open questions
   awaiting pharmacist consultation (Q1-Q8: ASO, SSG, cyclodextrins,
   maltodextrin, HES 130/0.4, HSH, source-unspecified starches generally,
   oats). The cyclodextrin classification specifically rests on a stale
   (2019) source and should be re-evaluated with current evidence.

3. **Bulk catalog analysis.** Once the flagged bulk dataset exists, run the
   same cuts as the pilot (drug category, dosage form, OTC/Rx, etc.) across
   all drug categories in the full catalog. The pilot covered only
   acetaminophen + ibuprofen; the full catalog reveals whether the labeling
   transparency gap is similar across other drug classes.

4. **Decide on route filtering.** The bulk extraction includes all routes
   (oral, topical, injectable, ophthalmic, etc.). Filtering by route is an
   analysis-time decision. The user has indicated the analysis will likely
   focus on oral routes only.

5. **CPG 578.100 research.** Investigate whether FDA Compliance Policy Guide
   578.100 ("starch" = corn starch) actually applies to drug inactive
   ingredient labeling, or only to food. Determine whether it is a binding
   regulation or just guidance. The project currently treats unqualified
   "starch" on drug labels as `unknown` for patient-facing purposes
   regardless.

6. **KIT component extraction.** Update the pilot's `pull_dailymed.py` to
   parse `<part>/<partProduct>` elements inside KIT labels, extracting each
   component's excipients. This would recover the 428 KIT products flagged
   `no_data` in the pilot. May not be needed if the bulk catalog supersedes
   the pilot for the journalism piece.

7. **FDA IIG cross-reference.** Cross-reference unique excipient strings
   against the FDA Inactive Ingredient Database. Identify strings not in the
   IIG and investigate why (OTC monograph products, non-standard naming
   variants, recently added excipients, label errors).

## Final Verification

Before publication, the following manual checks should be completed:

1. **Manually check the excipient validation table. Talk to a pharmacist.**
   The 171-entry validation table at `data/bulk/excipient_validation.csv` was
   built by Claude with documented rationale and citations for every entry,
   but it has not been independently reviewed by a domain expert. A pharmacist
   should walk through each entry, particularly the borderline cases catalogued
   in `analysis/validation_table_review.md` (cyclodextrins, sodium starch
   glycolate, oats, source-unspecified starches, hydroxyethyl starch).

2. **Verify if any human drugs are in animal bulk downloads we did not download
   from DailyMed.** DailyMed offers separate bulk download buckets for animal
   drugs. Our bulk extraction (April 2026) only pulled the human OTC, human
   prescription, homeopathic, and remainder-labels buckets. There is a
   possibility that legitimate human drugs ended up in an animal-drug bulk
   bucket due to manufacturer-side classification errors. Spot-check the animal
   drug downloads against the final filtered dataset to confirm no human
   medications were missed.
