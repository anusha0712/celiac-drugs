# Hidden Drug Allergens in US Drug Labels

A data pipeline that classifies every product in the US DailyMed catalog
for four allergens — **gluten, milk proteins and lactose, polyethylene
glycol (PEG), and carmine / cochineal extract** — based on the
inactive-ingredient block on each drug's label, then parses the same
labels' warning sections to check whether any allergy or contraindication
language is present. Everything in this repository is built from a single
DailyMed bulk-download snapshot pulled on April 6, 2026
(199,961 NDC-level rows after extraction).

---

## Repository structure

```
celiac-drugs/
├── README.md                                  ← this file
├── SESSION_LOG.md                             ← chronological per-session record
├── TASKS.md                                   ← cross-session task list
├── FDA-IID-recent-update.csv                  ← FDA Inactive Ingredient Database snapshot
│
├── scripts/
│   ├── extract_fullcatalog_raw.py             ← bulk ZIPs → 199,961-row raw CSV
│   ├── build_gluten_excipient_list.py         ← keyword search across the catalog
│   ├── build_gluten_validation.py             ← assembles gluten validation CSV
│   ├── build_allergens_validation.py          ← assembles milk, PEG, carmine tables
│   ├── filter_gluten_fullcatalog.py           ← six-step filter pipeline (gluten)
│   ├── flag_gluten_fullcatalog.py             ← apply gluten flags
│   ├── flag_allergens_fullcatalog.py          ← apply milk, PEG, carmine flags
│   ├── analyze_gluten_fullcatalog.py          ← gluten prevalence + slices
│   ├── analyze_allergens_fullcatalog.py       ← milk, PEG, carmine prevalence + slices
│   ├── analyze_dpi_labels.py                  ← DPI milk-warning label analysis
│   ├── analyze_peg_labels.py                  ← PEG-warning label analysis
│   ├── analyze_carmine_labels.py              ← carmine-warning label analysis
│   ├── allergen_filters.py                    ← shared filter helpers
│   ├── spl_label_parser.py                    ← shared SPL XML parser
│   ├── fda_iid_lookup.py                      ← FDA Inactive Ingredient Database loader
│   └── build_corpus_tests.py                  ← deterministic regression generator
│
├── data/fullcatalog/
│   ├── dailymed_fullcatalog_raw.csv           ← 199,961 raw rows (gitignored)
│   ├── gluten_fullcatalog_filtered.csv        ← 72,358 rows after the gluten filter
│   ├── gluten_fullcatalog_flagged.csv         ← + gluten flag column
│   ├── allergens_fullcatalog_flagged.csv      ← raw + 6 allergen-flag columns
│   ├── gluten_validation.csv                  ← 171 gluten entries
│   ├── milk_validation.csv                    ← 27 milk entries
│   ├── peg_validation.csv                     ← 4 PEG regular expressions
│   ├── carmine_validation.csv                 ← 24 carmine entries
│   ├── dpi_label_analysis.csv                 ← DPI milk-warning per set_id
│   ├── peg_label_analysis.csv                 ← PEG-warning per set_id
│   ├── carmine_label_analysis.csv             ← carmine-warning per set_id
│   └── corpus_test_{milk,peg,carmine}.csv     ← deterministic regression artefacts
│
├── bulk-data/                                 ← raw DailyMed bulk download (gitignored)
│   ├── human-otc/                             ← ~87K ZIPs across 11 subfolders
│   ├── human-prescription/                    ← ~54K ZIPs across 6 subfolders
│   ├── homeopathic/                           ← ~16K ZIPs
│   └── other/                                 ← ~2.5K ZIPs of remainder labels
│
└── analysis/allergens/
    ├── methodology.md                         ← shared methodology, all four allergens
    ├── narrative_draft.md                     ← the journalism piece
    ├── limitations.md                         ← per-allergen limitations
    ├── literature.md                          ← annotated bibliography
    ├── reconciliation_pass.md                 ← cross-workflow consistency tracker
    ├── gluten/
    │   ├── source_paper_critique_gluten.md    ← review of Figueiredo 2025
    │   ├── findings_fullcatalog_gluten.md     ← gluten findings
    │   └── validation_table_review_gluten.md  ← gluten validation table review
    ├── milk/
    │   ├── research_milk.md                   ← milk primary-source brief
    │   └── findings_milk.md                   ← milk findings
    ├── peg/
    │   ├── research_peg.md
    │   └── findings_peg.md
    └── carmine/
        ├── research_carmine.md
        └── findings_carmine.md
```

Filename conventions: `fullcatalog` refers to the April 2026 bulk-download
snapshot — the full 199,961-row catalog before any allergen-specific
filtering. `allergens` in a script name (for example,
`flag_allergens_fullcatalog.py`) refers to the milk + PEG + carmine batch,
which share a pipeline. The `gluten` scripts run separately because the
gluten workflow has its own filter pipeline.

---

## Prerequisites

- **Python 3.9+** with the standard library only — no third-party
  packages required. The pipeline uses `csv`, `re`, `xml.etree`,
  `pathlib`, `zipfile`, and `sys`.
- **DailyMed bulk download** at `bulk-data/{human-otc,human-prescription,
  homeopathic,other}/`. Download from
  <https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm>.
  Roughly 159,431 ZIP files, about 22 GB unzipped.
- **FDA Inactive Ingredient Database snapshot** at the project root as
  `FDA-IID-recent-update.csv`. Download from
  <https://www.fda.gov/drugs/drug-approvals-and-databases/inactive-ingredients-database-download>
  and convert to CSV.

Every script is run from the project root with
`python3 scripts/<name>.py`. Every script resolves its paths with
`Path(__file__).parent.parent`, so paths stay stable regardless of the
working directory.

---

## Workflow

### Phase 1 — Pulling the full DailyMed catalog

`scripts/extract_fullcatalog_raw.py` opens every ZIP in the bulk
download, parses the SPL XML inside, and writes one CSV row per
manufactured product. It extracts 43 fields per row, including drug
name, NDC code, dosage form, route, active ingredients with UNII codes,
inactive ingredients with UNII codes, manufacturer, approval type and
number, marketing status, DEA schedule, document type, and physical
characteristics (color, shape, imprint). A single SPL label can contain
several `<manufacturedProduct>` blocks under different NDC codes — each
NDC becomes its own row.

Two derived fields are worth flagging. `bulk_category` is read from the
download folder name (`human-otc/` → `human_otc`, and so on), which
captures the homeopathic-versus-conventional distinction that the XML
itself loses (homeopathic products carry the same `HUMAN OTC DRUG LABEL`
document type as conventional OTC drugs). `brand_generic` is a hard rule
on the FDA application-number prefix: ANDA → generic, NDA or NDA
Authorized Generic → brand, BLA → brand, anything else → OTC monograph.

Nothing is filtered at this stage. All routes, all dosage forms, all
drug categories, all approval types are kept — filtering belongs in
analysis, not extraction. The final raw dataset has **199,961 rows × 43
columns** with zero parse errors.

**Output:** `data/fullcatalog/dailymed_fullcatalog_raw.csv`.

### Phase 2 — Building the four allergen validation tables

A validation table is a CSV with one row per ingredient string, a flag
decision, a rationale, and a citation URL. The flagging scripts in
Phase 3 use the tables as lookups — nothing in the pipeline is inferred
or guessed. The four tables are anchored to four different primary
sources.

**Gluten — 171 entries.** Seed list from Figueiredo et al. 2025 Table 1
(fourteen gluten-source excipient terms). Extended by a word-boundary
keyword search across all 10,019 unique excipient strings in the
catalog (`scripts/build_gluten_excipient_list.py`) using twenty
keywords: English gluten-grain terms from the source paper (wheat, rye,
barley, semolina, bran, malt, oat / oats, starch, gluten, glucose,
pregelatinized, flour, grain), Latin botanical names for gluten grains
(*avena, triticum, hordeum, secale*), and starch-chemistry terms
(glycolate, dextrin, gum). Each new term is classified using 21 CFR
101.91, the FDA Inactive Ingredient Database, current National Celiac
Association guidance, FDA Compliance Policy Guide 578.100, and — for
the cyclodextrin family — the Gluten Intolerance Group's January 2019
reference list. The gluten table uses four flags
(`gluten_free` / `unknown` / `contains_gluten` / `no_data`); the
`unknown` tier exists because the same excipient name on a US drug
label can be either safe or unsafe depending on a botanical source the
label does not specify. Built by `scripts/build_gluten_validation.py`.
**Output:** `data/fullcatalog/gluten_validation.csv`.

**Milk — 27 rows.** Anchored to FARE's milk-allergen ingredient list.
Three flags (`contains_milk` / `milk_free` / `no_data`). On 2026-05-05
the lactose family and lactulose were reclassified from `contains_milk`
to `milk_free` after pharmacist review — purified milk sugars are not
the protein allergen, and flagging them as such would have overstated
the milk landscape by orders of magnitude. **Output:**
`data/fullcatalog/milk_validation.csv`.

**PEG — four regular expressions.** Anchored to the USP-NF polyethylene
glycol monograph: POLYETHYLENE GLYCOL, POLYETHYLENE OXIDE, MACROGOL,
CARBOWAX. Three flags (`contains_peg` / `peg_free` / `no_data`).
Polysorbates, poloxamers, Cremophor, Kollicoat, and TPGS share chemical
ancestry with PEG but are excluded by name. **Output:**
`data/fullcatalog/peg_validation.csv`.

**Carmine — 24 rows.** Anchored to 21 CFR 73.100 plus the GSRS UNII
synonym records for TZ8Z31B35M and CID8Z8N95N. Three flags
(`contains_carmine` / `carmine_free` / `no_data`). The CARMINE regex
uses word boundaries to avoid the croscarmellose false positive
(croscarmellose sodium is cellulose-based, not a carmine derivative).
**Output:** `data/fullcatalog/carmine_validation.csv`.

The milk, PEG, and carmine tables are all built by
`scripts/build_allergens_validation.py` in a single pass.

### Phase 3 — Applying the flags to the catalog

Two flagging pipelines run side by side because the four allergens do
not share a single relevant slice of the catalog.

**Gluten pipeline.** `scripts/filter_gluten_fullcatalog.py` applies a
six-step deterministic filter to the raw catalog and keeps only
FDA-recognized human medications that reach the GI tract by swallowing:

1. Keep only the four human drug `document_type` values
   (`HUMAN OTC DRUG LABEL`, `HUMAN PRESCRIPTION DRUG LABEL` and its
   variants, `HUMAN COMPOUNDED DRUG LABEL`). This drops vaccines,
   plasma derivatives, allergenic extracts, cellular and gene
   therapies, animal drugs, dietary supplements, medical devices,
   cosmetics, and bulk ingredients.
2. Drop the `homeopathic` `bulk_category` entirely.
3. Keep only rows whose `route = ORAL`. Drops topical, injected,
   inhaled, ophthalmic, dental, sublingual, buccal, transmucosal, and
   transdermal routes.
4. Drop dosage forms that are not swallowed: mouth-only forms
   (lozenge, mouthwash, chewing gum, dentifrice, rinse, pastille,
   troche); wrong-route data errors where the row says ORAL but the
   form is an injection or inhalant; and dissolvable films and orally
   disintegrating tablets, which mostly absorb through the buccal
   mucosa.
5. Keep only the FDA-recognized `approval_type` values (ANDA, NDA,
   NDA Authorized Generic, BLA, OTC Monograph Drug variants). Drops
   `unapproved drug other`, `export only`, `unapproved homeopathic`,
   dietary supplements, cosmetics, medical gases, and Emergency Use
   Authorizations.
6. A final cleanup drops mouthwash products whose `dosage_form` is
   something other than MOUTHWASH (LIQUID, SOLUTION, TABLET
   CHEWABLE) — mouthwashes by name that slipped past step 4.

The six filters are independent AND conditions — running them in any
order produces the same **72,358-row** output.
`scripts/flag_gluten_fullcatalog.py` then walks each row's excipient
list, looks every term up in the 171-entry gluten validation table,
and assigns the flag using the worst-excipient rule: if any one
excipient is `contains_gluten`, the product is `contains_gluten`;
otherwise, if any one is `unknown`, the product is `unknown`; only if
every excipient is clear is the product `gluten_free`; a row with no
inactive ingredients listed at all is `no_data`. **Output:**
`data/fullcatalog/gluten_fullcatalog_flagged.csv`.

**Milk + PEG + carmine pipeline.**
`scripts/flag_allergens_fullcatalog.py` runs the three lookup tables
against the raw 199,961-row catalog in one pass and writes six new
columns (one flag column and one matched-excipients column per
allergen). No pre-filter is applied — the dataset is sliced in the
analysis scripts: DPI inhalers only for milk, oral solids only for
PEG, and the full catalog for carmine. **Output:**
`data/fullcatalog/allergens_fullcatalog_flagged.csv`.

### Phase 4 — Reading the warning sections

Three scripts parse the actual SPL XML warning text for the allergens
with peer-reviewed harm anchors:
`scripts/analyze_dpi_labels.py` (milk in dry-powder inhalers),
`scripts/analyze_peg_labels.py` (PEG in oral solids), and
`scripts/analyze_carmine_labels.py` (carmine across the catalog).

Each script takes the set of SPL labels flagged for the relevant
allergen, parses the SPL XML, finds the warnings / contraindications /
adverse-reactions sections, and classifies the warning level as §4
contraindication, boxed warning, §5 warning, OTC allergy alert, or
silent. A classification of "warning present" requires that the
allergen's name appear within roughly 80 characters of an
allergy-context word — allergy, hypersensitivity, anaphylaxis,
contraindication, or one of their inflections. The 80-character window
prevents false positives where an allergen name turns up inside a
warning section purely as an ingredient-list mention. The pattern is
anchored to 21 CFR 201.22, the AAAAI/ACAAI 2022 Drug Allergy Practice
Parameter, and the Advair Diskus §4 contraindication template. Full
pattern definition is in `analysis/allergens/methodology.md` §5.

**Outputs:** `data/fullcatalog/dpi_label_analysis.csv`,
`data/fullcatalog/peg_label_analysis.csv`, and
`data/fullcatalog/carmine_label_analysis.csv`.

`scripts/build_corpus_tests.py` writes
`data/fullcatalog/corpus_test_{milk,peg,carmine}.csv` — deterministic
regression artefacts that record which DailyMed excipient strings each
validation rule matches under the current snapshot. Re-running on
identical inputs produces byte-identical CSVs.

---

## Flag system

Gluten uses four tiers (`contains_gluten` / `unknown` / `gluten_free` /
`no_data`). Milk, PEG, and carmine use three (`contains_<allergen>` /
`<allergen>_free` / `no_data`). Gluten gets the extra tier because the
same excipient name on a US drug label — starch, sodium starch
glycolate, modified starch, dextrin — can be either safe or unsafe
depending on a botanical source the label does not specify. The other
three allergens do not have the same source-ambiguity problem.

A product flagged `unknown` does not mean it contains gluten. It means
the label does not specify the source. In practice the great majority
of these products almost certainly contain zero gluten, because
pharmaceutical-grade starch in the US is predominantly corn- or
potato-derived — but the label does not confirm it.

The worst-excipient rule applies across all four allergens: if any one
excipient matches `contains_<allergen>`, the product is
`contains_<allergen>`; otherwise, if any one is `unknown` (gluten
only), the product is `unknown`; only if every excipient is clear is
the product `<allergen>_free`; a row with no inactive ingredients
listed at all is `no_data`.

---

## Known limitations

- **Label-based only.** No ELISA or HPLC measurement of actual allergen
  content. A product flagged `unknown` may contain zero allergen.
  Cross-contamination during manufacturing is undetectable from labels.
- **NDC-level unit of analysis.** A single SPL label can contain
  several NDC entries with different excipient profiles. Counts of
  products (NDC-level) and counts of labels (set_id-level) are
  different counts of the same underlying thing and are reported
  separately in the findings files.
- **Snapshot in time.** Data was pulled on April 6, 2026.
  Formulations and labels change.
- **Scope decisions are documented per allergen** in
  `analysis/allergens/limitations.md`: the gluten four-tier system and
  xanthan-gum reclassification (§Gluten); the PEG tight scope
  excluding polysorbates, poloxamers, Cremophor, Kollicoat, and TPGS
  (§PEG); the milk lactose-family and lactulose reclassification
  (§Milk); and the word-boundary CARMINE regex (§Carmine).

---

## Key decisions

| Decision | Choice | Rationale |
|---|---|---|
| Unit of analysis | NDC, not set_id | Two NDCs under the same SPL label can have different excipient profiles; the NDC is what a patient encounters on the shelf. |
| Data source | DailyMed only | The label repository the FDA recommends patients use. OpenFDA was rejected for a ~40% coverage gap. |
| Include OTC and Rx | Both, reported separately | Both populations are relevant to the labeling-transparency question. |
| Include combination products | Yes | Reflects the real OTC landscape. |
| Bare "starch" with no source | `unknown` | FDA CPG 578.100 says it legally means corn starch, but a patient can't know that from the label. |
| Xanthan gum | `gluten_free` | Per National Celiac Association guidance. A departure from the Portuguese source study, which flagged it precautionarily. |
| Milk lactose family + lactulose | `milk_free` (2026-05-05) | Purified milk sugars are not the protein allergen; pharmacist-reviewed. |
| PEG scope | USP-NF monograph names only | Polysorbates, poloxamers, Cremophor, Kollicoat, and TPGS excluded by name. |
| Carmine match | Word-boundary regex | Anchored to 21 CFR 73.100 plus GSRS UNII synonyms; word boundaries prevent the croscarmellose false positive. |

---

## Findings

The journalism draft is at `analysis/allergens/narrative_draft.md`. The
per-allergen findings files — `findings_fullcatalog_gluten.md`,
`findings_milk.md`, `findings_peg.md`, and `findings_carmine.md` — sit
under `analysis/allergens/{gluten,milk,peg,carmine}/`. The shared
methodology document at `analysis/allergens/methodology.md` covers
cross-allergen pipeline architecture and the warning-pattern matcher
in full.
