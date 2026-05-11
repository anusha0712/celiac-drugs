# Methodology — Allergens Workflow (Gluten, Milk, PEG, Carmine)

*Date of writing: 2026-04-21 (milk/PEG/carmine). 2026-04-22 (tight-scope
PEG revision + primary-source table anchoring). 2026-04-23 (reconciliation
pass — Parts 2-4 brought in sync with current scripts and validation
tables; new Parts 5 and 6 added; Part 7 provenance updated).*
*Data snapshot: DailyMed bulk download, April 6, 2026*

This document records every data decision made for the milk, PEG, and
carmine analyses. Gluten methodology is currently documented in
`CLAUDE.md` and will be absorbed into this file by Task #17 (reorg).
Pending hardening / analysis tasks are tracked in `TASKS.md`.

## Relationship to other files

- `research_{milk,peg,carmine}.md` — primary-source briefs; every factual
  claim carries an inline URL (Task #15 rewrite, 2026-04-22).
- `limitations.md` — consolidated per-allergen limitations.
- `literature.md` — annotated bibliography across all four allergens.
- `findings_{milk,peg,carmine}.md` — objective per-allergen findings.
- `narrative_draft.md` — cross-allergen journalism draft.

---

## Part 1 — Shared architecture

### 1.1 Starting point

All three allergens start from the same unfiltered raw catalog:
`data/fullcatalog/dailymed_fullcatalog_raw.csv` — 199,961 rows × 43 columns, produced by
`scripts/extract_fullcatalog_raw.py` from the April 6, 2026 DailyMed bulk SPL download.
One row per `<manufacturedProduct>` block in SPL XML (NDC-level unit of
analysis, same convention as gluten).

**Decision: start from raw, not the 72,358-row gluten-filtered dataset.**
Rationale: the milk harm anchor is dry powder inhalers, and the gluten
filter pipeline drops non-oral routes at Step 3. Filtering happens per
allergen inside analysis, not before flagging.

### 1.2 Three-script pipeline per allergen

1. `scripts/build_allergens_validation.py` — one-shot generator for
   `data/fullcatalog/milk_validation.csv`, `data/fullcatalog/peg_validation.csv`, and
   `data/fullcatalog/carmine_validation.csv`. All excipient decisions are encoded
   in Python lists in the script; the script writes deterministic CSVs.
2. `scripts/flag_allergens_fullcatalog.py` — reads the raw catalog and the three
   validation tables, applies the worst-excipient rule per allergen in
   one pass, writes `data/fullcatalog/allergens_fullcatalog_flagged.csv` with
   6 added columns (3 flags + 3 flagged-excipients lists).
3. `scripts/analyze_allergens_fullcatalog.py` — reads the flagged catalog, applies
   per-allergen slices (route, dosage_form, active_ingredient), prints
   counts to stdout. Not a data product; output is used to populate
   findings docs.

All three scripts are deterministic. No AI inference at any pipeline step.
Re-running the three scripts in sequence produces byte-identical outputs.

### 1.3 Validation-table schema (Task #21 strict)

All three validation CSVs share seven columns:

| Column | Purpose |
| :--- | :--- |
| `fda_term` | Excipient string as stored in DailyMed (uppercase) OR a regex pattern |
| `match_type` | `exact` for literal string match after uppercasing; `regex` for compiled-pattern substring match |
| `flag_decision` | `contains_<allergen>` (absence of row = default `<allergen>_free` via flagger) |
| `source_url` | Primary-source URL supporting the classification claim. Required on every row (Task #21). |
| `iid_status` | `in_iid` or `not_in_iid` — from `FDA-IID-recent-update.csv` |
| `iid_unii` | UNII of the ingredient in FDA IID, or empty if not listed |
| `rationale` | One-line justification tying the row to its primary-source claim |

**Schema anchor.** Task #21 (2026-04-22) required every row to cite a
primary-source URL supporting the classification claim. AI-reasoned
exclusions (rows whose rationale was "not in authority list" without a
URL) were removed. The flagger defaults to `<allergen>_free` on no
match, so explicit exclusion rows are no longer needed.

**Per-allergen match discipline.**
- **Milk** — `exact` only. Every row is a DailyMed raw-string variant of
  a FARE-listed milk-derived ingredient. Lact* false-positive density is
  too high for substring matching.
- **PEG** — `regex` only (4 patterns). Tight-scope polymer names are
  unambiguous enough that regex is safe; enumerating every MW grade as
  an exact row would be brittle.
- **Carmine** — `exact` primarily (21 CFR 73.100 permitted names + GSRS
  synonym record); `regex` word-boundary for standalone CARMINE,
  CARMINIC, COCHINEAL (word-boundary avoids CROSCARMELLOSE SODIUM).

### 1.4 Flag tiers

Three tiers per allergen: `contains_<allergen>`, `<allergen>_free`,
`no_data`. No `unknown` tier is populated in the current run. Rationale
per allergen below in Parts 2-4.

Gluten's four-tier system (gluten_free / unknown / contains_gluten /
no_data) handled source-ambiguous excipients like SODIUM STARCH GLYCOLATE
TYPE A. For the current allergen pass, source-ambiguity cases were not
identified during the keyword scan, so the `unknown` column is empty.
Pending hardening task may reintroduce `unknown` once the FDA IID
cross-reference surfaces source-ambiguous ingredients.

### 1.5 Worst-excipient rule

Per product row, for each allergen independently:
- If `excipients_raw` is empty → `no_data`
- Else split on `; `, uppercase each token, check against the exact
  lookup first, then against compiled regex patterns
- If any token resolves to `contains_<allergen>` → `contains_<allergen>`
  (matching tokens are preserved in `<allergen>_flagged_excipients`)
- Else → `<allergen>_free`

Same logic as `scripts/flag_gluten_fullcatalog.py:59` for gluten.

### 1.6 Post-flag slicing

Category-level prevalence numbers (DPIs, oral solids, azithromycin, etc.)
are computed by `scripts/analyze_allergens_fullcatalog.py` against `route`, `dosage_form`,
and `active_ingredients` columns in the flagged catalog. The flag is a
property of the product, set once by `flag_allergens_fullcatalog.py`. Slicing never
modifies a flag; it just groups rows.

### 1.7 Fact-check log

Every UNII, PMID, and CFR citation in the findings and narrative docs
was independently verified in Phase 1 against primary sources:
- UNIIs → `https://precision.fda.gov/uniisearch/srs/unii/<UNII>`
- PMIDs → `https://pubmed.ncbi.nlm.nih.gov/<PMID>/`
- CFR → eCFR at `https://www.ecfr.gov/current/title-21/...`
- Federal Register final rules → federalregister.gov
- EMA guidance → ema.europa.eu

Verification results are logged in:
- *(factcheck_log CSVs were deleted 2026-04-22 after Task #15 folded
  their content as inline citations into the three research_*.md files.)*

Columns: `claim, source_doc, verified_against, result, notes`.
`result` ∈ {confirmed, corrected, missing, not_found}.

---

## Part 2 — Milk methodology

The lactose family (9 string variants) and LACTULOSE were removed
from the validation table 2026-05-05 per pharmacist review: milk
sugars in purified pharmaceutical form do not themselves contain
allergenic milk proteins, lactose intolerance is distinct from milk
allergy, and theoretical milk-protein contamination is very unlikely.

### 2.1 Input sources used

- Compass-artifact research primer (`compass_artifact_wf-80dd93ff-....md`).
  Treated as starting point, not source of truth.
- Peer-reviewed literature (see `literature.md`).
- FDA GSRS (Global Substance Registration System).
- 21 CFR and FALCPA text on eCFR and FDA.gov.
- EMA/CHMP/302620/2017 Rev. 5 (December 5, 2025).
- Unique excipient strings scanned from
  `data/fullcatalog/dailymed_fullcatalog_raw.csv` (10,019 unique after uppercasing).

### 2.2 UNII verification (Phase 1 activity)

Phase 1 cross-checked the seven primer-named milk UNIIs against FDA GSRS
as a sanity check before building the validation table. The current
validation table does not use UNIIs directly; it matches on DailyMed
raw-string variants of FARE-listed ingredients. UNII values are recorded
in the `iid_unii` column when the ingredient is listed in FDA IID, but
the flag decision is anchored to FARE, not to GSRS.

Verified UNIIs (from primer, confirmed in GSRS): `EWQ57Q8I5X` (lactose
monohydrate), `3SY5LH9PMK` (anhydrous lactose), `J2B2A4N98G` (lactose),
`48268V50D5` (casein), `7473P66J9E` (whey), `6A001Y4M5A` (lactalbumin),
`9U7D5QH5AE` (lactulose — distinct from lactose).

### 2.3 Excipient discovery (FARE-anchored)

The milk validation table enumerates entries from the FARE milk-allergen
list plus DailyMed string variants of those entries (comma-flips,
double-spaces, .ALPHA. prefixes, etc.) to catch labelling
inconsistencies. The list anchor is FARE
(https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens/milk).
Deterministic corpus test: `scripts/build_corpus_tests.py` runs the
final table against all 10,019 unique uppercased DailyMed excipient
strings and writes `data/fullcatalog/corpus_test_milk.csv`. Re-running the
generator produces byte-identical output.

> Corpus tests verify pattern-matching behaviour (rule X matches DailyMed
> string Y) only. They do NOT verify the underlying classification
> correctness (whether rule X correctly classifies the matched compound
> as milk-derived). That evidence comes from the per-row `source_url`
> and `rationale`, not from the corpus test.

### 2.4 Milk validation table structure (post-Task-#21)

37 rows, all `contains_milk`, all `match_type = exact`, all carrying a
FARE source_url, all carrying an `iid_status` flag from
`FDA-IID-recent-update.csv`:

- 9 lactose variants (LACTOSE, LACTOSE MONOHYDRATE, ANHYDROUS LACTOSE,
  "LACTOSE, UNSPECIFIED FORM", "LACTOSE, ANHYDROUS", "ANHYDROUS  LACTOSE"
  double-space, ".ALPHA.-LACTOSE", "ALPHA-LACTOSE", plus raw-string
  comma-flip variants).
- 1 lactulose (`contains_milk` per FARE; reclassified 2026-04-22).
- 6 casein variants (CASEIN, SODIUM/CALCIUM/POTASSIUM CASEINATE,
  HYDROLYZED CASEIN, raw-string ENZYMATIC-variant).
- 2 whey variants (WHEY, WHEY PROTEIN HYDROLYSATE).
- 8 specific milk-protein variants (α-lactalbumin, β-lactoglobulin,
  lactoferrin, lactoperoxidase, plus raw-string BOVINE/.ALPHA.- variants).
- 11 whole-milk / milk-fat / colostrum variants (MILK, SKIM MILK, COW
  MILK, COW MILK FAT, GOAT MILK, BOS TAURUS COLOSTRUM, MILK PROTEIN,
  MILK PROTEIN CONCENTRATE, "AMINO ACIDS, MILK", NONFAT DRY MILK,
  BUTTERMILK).

Source URL coverage: 100%. Every row cites the FARE milk-allergen
ingredient list page as its primary classification source.

IID coverage: 5 of 37 rows match a UNII in `FDA-IID-recent-update.csv`
(LACTOSE MONOHYDRATE, ANHYDROUS LACTOSE, LACTOSE, MILK PROTEIN
CONCENTRATE, and the double-space ANHYDROUS LACTOSE variant). The
remaining 32 rows are not listed in IID; the `iid_status` column makes
this explicit on every row rather than silently dropping them.

**Pre-Task-#21 note.** An earlier version of this table carried 29
explicit `milk_free` exclusion rows (lactic acid, lactobacillus,
plant butters, etc.) whose rationale was AI chemistry/botany knowledge
rather than an external primary source. Task #21 (2026-04-22) removed
those rows: the flagger defaults to `milk_free` on no match, so they
were unnecessary. Historical snapshot preserved in git history.

### 2.5 Decision: all lactose variants → contains_milk

9 lactose-related strings are flagged `contains_milk`, not split into
lactose-intolerance vs milk-protein-allergy tiers. Rationale: the piece
frames label transparency. A milk-allergic patient reading "lactose"
sees the same word in a DPI (documented milk-protein anaphylaxis risk
via carrier contamination) and in an oral tablet (theoretical trace
risk). Splitting the flag would require inferring
degree-of-milk-protein-contamination per product, which is not
available from the label.

Known consequence: this over-calls oral lactose as a milk-protein-harm
excipient for patients who are lactose-intolerant but not milk-allergic.
Documented as a limitation in `limitations.md` §Milk.

### 2.6 Decision: Lactulose classification

Lactulose is flagged `contains_milk` per FARE's milk-derived ingredient
list. Pharmaceutical lactulose is synthesized by isomerizing lactose,
which is itself milk-derived. Reclassified from milk_free to
contains_milk 2026-04-22 as part of the Task #21 strict-rule pass.
Source: https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens/milk

### 2.7 Harm-anchor filter (DPI family)

The DPI filter is defined in `scripts/allergen_filters.py` as the
shared constant `is_dpi(dosage_form, route)`:

- `dosage_form` contains `POWDER, METERED` or `INHALANT, METERED`.
- AND `route` contains `RESPIRATORY` or `INHAL`.

This excludes pMDIs (AEROSOL, METERED — propellant-based, no lactose
carrier) and oral dosage forms that happen to be powders. Shared
across `analyze_dpi_labels.py` and `analyze_allergens_fullcatalog.py` so both
scripts use the same definition.

Spiriva HandiHaler is a documented edge case: DailyMed classifies it
as CAPSULE / ORAL rather than POWDER METERED / RESPIRATORY, so the
filter does not capture it even though the lactose carrier is inhaled.
Documented in `limitations.md` §Milk.

### 2.8 Milk results

All counts reproduce via `python3 scripts/analyze_allergens_fullcatalog.py`.

Full catalog (199,961 rows):
- `contains_milk`: 33,481 (16.74%)
- `milk_free`: 154,972 (77.50%)
- `no_data`: 11,508 (5.76%)

Oral route subset (N=95,602): 32,548 `contains_milk` = 34.05%.

DPI harm-anchor subset (N=29 NDCs, strict filter with pMDIs excluded):
- `contains_milk`: 25 (86.21%)
- `milk_free`: 3 (10.34%) — Afrezza (inhaled insulin, fumaryl
  diketopiperazine carrier) does not use lactose.
- `no_data`: 1 (3.45%)

Label analysis on 19 unique DPI set_ids (from `analyze_dpi_labels.py`):
18 carry a Section 4 milk-protein contraindication (Advair Diskus /
Wixela Inhub family); 1 silent (Afrezza, no milk carrier).

### 2.9 Milk limitations (summary)

1. Label-based only. No ELISA or HPLC measurement of actual
   milk-protein content in flagged products.
2. Lactose variants collapsed into one tier. Over-calls oral lactose
   for lactose-intolerant-but-not-milk-allergic patients.
3. `no_data` rate 5.76% catalog-wide.
4. NDC-level unit of analysis over-counts unique marketed products.
5. DPI filter anchored to DailyMed's own dosage-form vocabulary
   (`POWDER, METERED` / `INHALANT, METERED`). Products mis-classified
   at the DailyMed source (e.g. Spiriva HandiHaler as CAPSULE/ORAL)
   are not captured.
6. FARE's milk-allergen ingredient list is the sole primary source.
   FARE is a patient-advocacy organization; stricter framing would
   require a federal regulator's list (none exists — no FDA-defined
   "milk-derived drug excipients" rule parallel to 21 CFR 101.91 for
   gluten).
7. EMA guidance Rev. 5 (2025-12-05) is the current live revision.
8. Pharmacist spot-check deferred (manual, user-owned).
9. Figueiredo et al. 2024 (Portuguese study) excluded per user
   direction 2026-04-21.

---

## Part 3 — PEG methodology

### 3.1 Input sources used

- Compass-artifact research primer (`compass_artifact_wf-81216a5c-....md`,
  Part 1).
- Peer-reviewed literature (see `literature.md`).
- FDA GSRS and USP compendial references.
- 21 CFR text on eCFR.
- Stone 2019 FAERS cohort (PMID 30557713) and Reker 2019 Pillbox analysis
  (PMID 30867323).
- Unique excipient strings from `data/fullcatalog/dailymed_fullcatalog_raw.csv`.

### 3.2 UNII verification (Phase 1 activity, tight scope does not depend on it)

Phase 1 cross-checked the primer-named PEG UNIIs against FDA GSRS and
corrected 9 of 20 that did not resolve or mapped to the wrong MW grade.
The corrections are preserved inline in `research_peg.md` (§UNII
verification). Under the tight-scope decision (§3.5), the current PEG
validation table uses regex on excipient strings, not UNIIs, so these
pre-tight-scope corrections do not affect flag counts. The `iid_unii`
column in `peg_validation.csv` is populated via exemplar lookup (one
representative MW grade per regex pattern).

### 3.3 Excipient discovery (tight scope)

The tight-scope PEG table does not enumerate individual strings; it
enumerates 4 regex patterns that cover every USP-NF PEG name variant
the flagger should catch (see §3.4). Deterministic corpus test:
`scripts/build_corpus_tests.py` runs the regex patterns against all
10,019 unique uppercased DailyMed excipient strings and writes
`data/fullcatalog/corpus_test_peg.csv`. Every matching string is the expected
kind (POLYETHYLENE GLYCOL + MW grade, POLYETHYLENE OXIDE + MW grade,
a handful of polymer-name variants). Re-running the generator produces
byte-identical output.

> Corpus tests verify pattern-matching behaviour (rule X matches DailyMed
> string Y) only. They do NOT verify the underlying classification
> correctness (whether rule X correctly classifies the matched compound
> as PEG-derived). That evidence comes from the per-row `source_url`
> and `rationale`, not from the corpus test.

**Pre-tight-scope note.** An earlier version scanned all 10,019
DailyMed excipient strings for 443 PEG-adjacent strings covering
polysorbates, poloxamers, polyoxyl derivatives, mPEG, Vitamin E TPGS,
Kollicoat IR, and other PEG-containing families. The 2026-04-22
tight-scope decision (§3.5) restricts the flag to unconjugated PEG
polymer only; the adjacent families are documented in §3.6 with
rationales but are not flagged. Historical snapshot preserved in git
history.

### 3.4 PEG validation table structure (tight scope, 2026-04-22)

4 regex patterns total. All flag `contains_peg`. Scope is unconjugated
PEG polymer per the tight-scope decision. Patterns:

- `\bPOLYETHYLENE\s+GLYCOL` — USP-NF PEG monograph name. Catches all
  MW grades, unspecified, plural.
- `\bPOLYETHYLENE\s+OXIDE` — same polymer at higher MW.
- `\bMACROGOL` — EU/USP-EP name. Catches MACROGOLGLYCEROL.
- `\bCARBOWAX` — Dow trade name (rare in DailyMed; kept as defensive).

Adjacent families that contain a PEG chain but are NOT in the tight
scope — polysorbates, poloxamers, polyoxyl derivatives (Cremophor),
mPEG, PEG-N surfactants, Vitamin E TPGS, Kollicoat IR, stearoyl
polyoxyl glycerides, caprylocaproyl polyoxyl glycerides — are
documented in §3.6 below.

### 3.5 Scope decision — tight scope locked 2026-04-22

`contains_peg` restricted to unconjugated PEG polymer only:
- POLYETHYLENE GLYCOL (USP monograph name; all MW grades)
- POLYETHYLENE OXIDE (same polymer, higher MW)
- MACROGOL (EU/USP-EP name)
- CARBOWAX (Dow trade name)

Rationale for the "floor" scope: data-journalism defensibility. Every
flagged product carries an excipient name that is unambiguously PEG per
the USP-NF PEG monograph
(https://www.uspnf.com/notices/peg-gen-announcement-20230929). Adjacent
families with weaker or mechanism-mismatched cross-reactivity evidence
are out of scope and documented below in §3.6.

Reker 2019 Table 1 lists PEG (36.03% of oral solids) and Poloxamer
(0.76%) as separate categories, establishing the precedent for counting
PEG alone rather than a bundled PEG-family figure. See
https://pubmed.ncbi.nlm.nih.gov/30867323/.

### 3.6 Scope decisions — excluded adjacent families

The following compound families contain or resemble the PEG chain but
are NOT flagged `contains_peg` under the tight scope. Each family's
rationale below with inline primary sources.

**Polysorbates (Tween 20, 40, 60, 80, etc.)**
Chemistry: PEG-sorbitan fatty-acid ester. PEG chain is conjugated to a
sorbitan core via fatty acid linkage.
PEG-chain relationship: yes, contains PEG.
Harm evidence: Stone 2019 (https://pubmed.ncbi.nlm.nih.gov/30557713/)
reported skin-test cross-reactivity between PEG and polysorbate 80 in
both index anaphylaxis patients; Wolfson 2021
(https://pubmed.ncbi.nlm.nih.gov/34166844/) skin-tested 80 post-mRNA
vaccine reactors to both PEG and polysorbate 80. AAAAI/ACAAI 2022 Drug
Allergy Practice Parameter (https://pubmed.ncbi.nlm.nih.gov/36122788/)
states polysorbate cross-reactivity "needs further study."
Why excluded from flag: clinical cross-reactivity has IgE skin-test
evidence but the AAAAI/ACAAI 2022 position is unsettled. Under the
floor-scope rule, not every PEG-allergic patient is polysorbate-
cross-reactive. A bundled count would over-call for polysorbate-tolerant
patients. Polysorbate prevalence in the catalog is non-trivial (several
thousand products) and should be reported separately if the author
wants to address it.

**Poloxamers (Pluronic F-68 = poloxamer 188; Pluronic F-127 = poloxamer 407)**
Chemistry: PEG-PPG-PEG block copolymer.
PEG-chain relationship: yes, contains PEG blocks.
Harm evidence: case reports of IV poloxamer 188 anaphylaxis exist, but
no skin-test cross-reactivity study demonstrating PEG→poloxamer
cross-reactivity in PEG-allergic patients. Reker 2019 Table 1 lists
Poloxamer as a SEPARATE allergen category (0.76% of oral solids).
Why excluded: no demonstrated IgE cross-reactivity with PEG.
Structurally PEG-adjacent, clinically under-studied.

**Polyoxyl derivatives (Cremophor EL = polyoxyl 35 castor oil;
Cremophor RH40; polyoxyl stearates)**
Chemistry: PEG-fatty-acid ester (same as PEG-N naming).
PEG-chain relationship: yes, contains PEG.
Harm evidence: Cremophor EL anaphylactoid reactions in IV paclitaxel
and IV cyclosporine are well documented in the oncology literature.
**Mechanism is complement-activation-related pseudoallergy (CARPA),
not IgE-mediated PEG allergy.** A PEG-allergic patient is not
necessarily Cremophor-reactive; a Cremophor-reactive patient is not
necessarily PEG-allergic.
Why excluded: different disease mechanism. CARPA is IgE-independent.
Flagging Cremophor as "contains PEG" would conflate two distinct
allergic profiles.

**mPEG / methoxy-PEG**
Chemistry: PEG with a methyl end cap.
PEG-chain relationship: yes, core PEG chain.
Harm evidence: Stone 2019 notes methoxy-PEG and PEG-asparaginase in
the "polyether" group but does not quantify cross-reactivity.
Why excluded (borderline): scope tightness. mPEG is chemically very
close to bare PEG. Argument for inclusion is that the PEG chain is
identical; argument for exclusion is that the methyl cap changes
surface behavior and may change epitope presentation. Under the
floor-scope rule, we exclude unless explicitly harm-anchored.

**PEG-N surfactants (PEG-40 stearate family; identical to polyoxyl N
stearate)**
Chemistry: same as polyoxyl derivatives; different naming convention.
PEG-chain relationship: yes.
Why excluded: inherits the polyoxyl rationale. "Polyoxyl 40 stearate"
and "PEG-40 stearate" are the same molecule in different naming
conventions (USP vs cosmetic).

**Vitamin E TPGS (D-alpha-tocopheryl polyethylene glycol 1000 succinate)**
Chemistry: vitamin E succinate linked to PEG 1000.
PEG-chain relationship: yes.
Why excluded: PEG chain is conjugated to a vitamin E carrier. No
published PEG-allergy case specific to TPGS. Small catalog count (78
rows in bulk data).

**Kollicoat IR (polyvinyl alcohol-graft-polyethylene glycol copolymer)**
Chemistry: PVA backbone with PEG graft side chains.
PEG-chain relationship: yes, via graft.
Why excluded: highly processed tablet-coating polymer; PEG graft is
immobilized in the PVA matrix and not freely available as a PEG
epitope. No published PEG-allergy case attributable to Kollicoat IR.

**Propylene glycol (27,136 rows in the catalog)**
Chemistry: single 3-carbon diol (non-polymer).
PEG-chain relationship: NO.
Why excluded: chemically unrelated to PEG. Different allergen profile
(delayed-type hypersensitivity when relevant). If covered, needs a
separate allergen pass.

### 3.7 Harm-anchor note: PEG 3350 bowel preps (out of scope)

PEG 3350 products where PEG is the **active ingredient** (MiraLAX,
GoLYTELY, NuLYTELY, CoLyte, MoviPrep, Plenvu, GaviLyte family) are
out of scope for this analysis. The project rule is allergen matching
on inactive ingredients only (`excipients_raw`), not active
ingredients. The Stone 2019 anaphylaxis signal in that active-ingredient
context is a different story (dose-response to a drug active), not a
labeling-transparency-of-inactives story.

### 3.8 PEG results (tight scope)

Final flag distribution, full catalog (199,961 rows):
- `contains_peg`: 28,551 (14.28%)
- `peg_free`: 159,902 (79.97%)
- `no_data`: 11,508 (5.76%)

**Oral tablets / capsules / granules / pellets (ODT-excluded):
24,187 of 76,427 products contain PEG = 31.65%.** Reker 2019 reported
PEG in 36.03% of 42,052 oral solids (Pillbox v201605). The two figures
are comparable within-reason; the 4.4-point gap likely reflects
differences in catalog (DailyMed 2026 vs Pillbox 2016), dosage-form
filter details, and curated-name unification.

### 3.9 PEG limitations (summary)

1. Label-based only.
2. Tight scope is a documented floor estimate. Adjacent families
   (polysorbates, poloxamers, polyoxyl derivatives, mPEG, PEG-N
   surfactants, TPGS, Kollicoat IR) are excluded by design and may
   undercount real PEG exposure for patients who are cross-reactive.
3. No `unknown` tier populated: POLYETHYLENE GLYCOL and its MW grades
   are unambiguously PEG per the USP-NF monograph.
4. PEG as active ingredient (bowel preps) excluded per the
   inactive-ingredient-only project rule.
5. Propylene glycol excluded (chemically distinct).
6. FDA IID cross-reference uses the local `FDA-IID-recent-update.csv`
   (2026-04-22 snapshot) via `scripts/fda_iid_lookup.py`. Every row
   carries `in_iid` / `not_in_iid` status.
7. Pharmacist spot-check deferred (manual, user-owned).
8. Unit of analysis NDC-level (same as gluten).

---

## Part 4 — Carmine methodology

### 4.1 Input sources used

- Compass-artifact research primer (`compass_artifact_wf-81216a5c-....md`,
  Part 2).
- Peer-reviewed literature (see `literature.md`).
- FDA GSRS.
- 21 CFR 73.100, 73.1100, 70.25, 101.22, 201.100, 201.66 text on eCFR.
- Federal Register final rule 74 FR 207 (2009-01-05, E8-31253).
- CSPI citizen petition docket FDA-1998-P-0032 (regulations.gov).

### 4.2 UNII verification results — corrections

2 of the 4 primer-named carmine UNIIs did not resolve in GSRS:

| Primer claim | Correct UNII | Notes |
| :--- | :--- | :--- |
| CARMINE = CID8SF5SDE | Does not exist in GSRS | No standalone UNII for carmine. Pharmaceutical use is captured via the CARMINIC ACID UNII. |
| CARMINIC ACID = 6T5EM2IMAF | CID8Z8N95N | CAS 1260-17-9. GSRS synonyms include 'C.I. NATURAL RED 4', 'C.I. 75470', 'E 120', 'COCHINEAL CARMINE'. |
| COCHINEAL = TZ8Z31B35M | TZ8Z31B35M | Confirmed. 'Cochineal extract' is a synonym on this record. |

Our flagger uses excipient-string matching, not UNIIs, so these corrections
do not affect the flag counts. Correct values now appear inline in
`research_carmine.md` (§UNII verification).

### 4.3 DailyMed scan (21 CFR + GSRS anchored)

The carmine validation table is derived from two primary sources:
1. **21 CFR 73.100** — FDA permitted-name list for the cochineal-extract
   color additive: `carmine`, `cochineal extract`.
   https://www.law.cornell.edu/cfr/text/21/73.100
2. **FDA GSRS UNII records** — synonym lists on the two carmine-family
   UNIIs:
   - COCHINEAL = TZ8Z31B35M (https://precision.fda.gov/uniisearch/srs/unii/TZ8Z31B35M)
   - CARMINIC ACID = CID8Z8N95N (https://precision.fda.gov/uniisearch/srs/unii/CID8Z8N95N)

Every term in the validation table traces to one of these two primary
sources, not to an AI keyword list. Deterministic corpus test:
`scripts/build_corpus_tests.py` runs the final table against the 10,019
unique DailyMed excipient strings and writes
`data/fullcatalog/corpus_test_carmine.csv`. Of 24 rules, 5 currently match
DailyMed strings (CARMINE, CARMINIC ACID, COCHINEAL, COCHINEAL EXTRACT,
CI 75470); the other 19 are defensive rules for GSRS synonyms that do
not appear in the current catalog. Re-running the generator produces
byte-identical output.

> Corpus tests verify pattern-matching behaviour (rule X matches DailyMed
> string Y) only. They do NOT verify the underlying classification
> correctness (whether rule X correctly classifies the matched compound
> as carmine). That evidence comes from the per-row `source_url` and
> `rationale`, not from the corpus test.

### 4.4 Carmine validation table structure (post-Task-#21)

24 rows, all `contains_carmine`, all carrying primary-source URLs and
`iid_status` flags:

- 21 exact-match rows covering 21 CFR 73.100 permitted names plus
  every GSRS synonym on the two carmine-family UNII records (CARMINE,
  COCHINEAL EXTRACT, COCHINEAL, DACTYLOPIUS COCCUS/CACTI COLORANT,
  COCCUS CACTI COLORANT, CARMINIC ACID, CI 75470, C.I. 75470, NATURAL
  RED 4, C.I. NATURAL RED 4, NATURAL RED 2180, E 120, E-120, E120,
  INS-120, INS 120, COCHINEAL CARMINE, CARMINE 5297, COCHINEAL RED
  PWD, SUN RED NO. 1).
- 3 regex word-boundary rows: `\bCARMINE\b`, `\bCARMINIC\b`,
  `\bCOCHINEAL\b`. Word-boundary anchoring prevents CROSCARMELLOSE
  SODIUM (15,598 rows in the catalog) from false-matching.

Source URL coverage: 100%. Every row cites 21 CFR 73.100, the COCHINEAL
GSRS record, or the CARMINIC ACID GSRS record.

IID coverage: 2 of 24 rows match a UNII in the local IID snapshot
(CARMINE, `\bCARMINE\b`). The other 22 rows are defensive synonym
entries not listed in IID (flagged `not_in_iid` for transparency).

### 4.5 Analysis approach: landscape (no pre-filter)

Task #22 (2026-04-22) rewrote the carmine analysis to be a landscape
view with no pre-filtering. Rationale: the carmine universe is small
(176 products catalog-wide), so the right frame is a descriptive
landscape rather than a narrow slice. Pre-filtering by AI-selected
drug classes (azithromycin / omeprazole / levothyroxine / chewable
tablets — the original approach) was AI judgment, not primary-source
anchored, and has been removed.

`scripts/analyze_allergens_fullcatalog.py` reports carmine counts by `route`,
`dosage_form`, `approval_type`, `bulk_category`, `brand_generic`,
top active ingredients (drug identity only — NOT allergen matching),
and top manufacturers. `findings_carmine.md` surfaces wherever carmine
concentrates in the landscape.

Label analysis: `scripts/analyze_carmine_labels.py` parses SPL XML for
every `contains_carmine` set_id (156 unique) and classifies warning
level per label. Allergy-context anchored patterns (see §5) ensure
warnings are only counted when the label genuinely discusses carmine
allergy, not when carmine is listed as an ingredient inside a warning
section.

### 4.6 Regulatory verification

21 CFR 73.100 (food color-additive labeling) and 21 CFR 73.1100 (drug
color-additive labeling) were read against current eCFR text. Summary:
- 21 CFR 73.100(c)(2), effective January 5, 2011, requires specific
  common-name declaration of "cochineal extract" or "carmine" on food
  labels.
- 21 CFR 73.1100 permits cochineal extract and carmine in ingested and
  externally applied drugs and points to the generic color-additive
  labeling rule at 21 CFR 70.25. No common-name-declaration requirement.

Final rule 74 FR 207 (published 2009-01-05, E8-31253) amended 21 CFR
73.100, 73.2087 (cosmetics), and 101.22 (food labeling) only. The 2009
rule's preamble noted FDA "plans to initiate a separate rulemaking" for
drug inactive-ingredient declaration under FDAMA section 412.

Phase 1 agent searched Federal Register and FDA.gov for a post-2009
drug-specific rulemaking on carmine declaration. No proposed rule,
final rule, or draft guidance was identified for the 2009-2026 period.

Known limitation: regulations.gov blocked programmatic docket access
during fact-check (HTTP 403), so docket FDA-1998-P-0032 filings from
2020-2026 were not fully enumerated. Manual docket spot-check
recommended before publication.

### 4.7 Carmine results

All counts reproduce via `python3 scripts/analyze_allergens_fullcatalog.py` and
`python3 scripts/analyze_carmine_labels.py`.

Full catalog (199,961 rows):
- `contains_carmine`: 176 (0.09%)
- `carmine_free`: 188,277 (94.16%)
- `no_data`: 11,508 (5.76%)

Three units of analysis appear across the carmine docs; all three are
correct at different granularities:
- **176** = NDC-level count (one row per `<manufacturedProduct>` block)
- **156** = unique set_id count (one SPL label may list multiple NDCs)
- **24** = validation-table row count (rules, not products)

Landscape breakdowns (per `analyze_allergens_fullcatalog.py`):
- Route: ORAL 150 (85.2%); TOPICAL 26 (14.8%).
- Dosage_form: TABLET 37, TABLET DELAYED RELEASE 28, TABLET FILM COATED
  25, TABLET CHEWABLE 24, LOZENGE 7, CAPSULE LIQUID FILLED 7, STICK 6,
  others ≤5.
- Approval_type and manufacturer concentration: see
  `findings_carmine.md` §Landscape.

Label analysis (156 unique set_ids, parsed by
`analyze_carmine_labels.py`): 151 silent, 5 set_ids had no
warning-relevant SPL sections. 0 labels carry any carmine-allergy
language under the allergy-context-anchored pattern (see §5).

### 4.8 Carmine limitations (summary)

1. Label-based only.
2. Sadowska year correction: primer said 2020; correct year is 2022
   per PubMed (PMID 35369613). Corrected inline in `research_carmine.md`.
3. Regulations.gov HTTP 403 prevented full 2020-2026 enumeration of
   docket FDA-1998-P-0032 filings. Manual docket spot-check is
   user-owned.
4. 176 is NDC-level; 156 is set_id-level. `findings_carmine.md` uses
   the unit appropriate to each claim.
5. Word-boundary regex on CARMINE prevents CROSCARMELLOSE SODIUM
   false-positive (15,598 catalog rows).
6. Figueiredo 2024 excluded per user direction 2026-04-21.

---

## Part 5 — Warning-pattern vocabulary

Label-analysis scripts (`analyze_dpi_labels.py`, `analyze_peg_labels.py`,
`analyze_carmine_labels.py`) detect whether an SPL warning section
genuinely discusses an allergen's allergic reactions — as opposed to
merely listing the allergen name as an ingredient inside that section.

**Rule.** A warning match requires an allergen name AND an
allergy-context token within 80 characters of each other. Neither
alone is sufficient.

**Allergy-context fragment** (shared from `scripts/spl_label_parser.py`):

```python
ALLERGY_CONTEXT = r"(?:allerg|hypersens|anaphyla|contraindicat)"
```

Fragments (not whole words) catch inflected forms: `allerg` matches
"allergy" / "allergic" / "allergen" / "allergies"; `hypersens` matches
"hypersensitivity" / "hypersensitive"; `anaphyla` matches "anaphylaxis"
/ "anaphylactic"; `contraindicat` matches "contraindicated" /
"contraindication".

### 5.1 Honest framing of the vocabulary choice

The 4-token list is an **editorial selection**, NOT prescribed verbatim
by any single primary source. The selection is **informed by** the
following sources but they do not specify "use exactly these 4 tokens":

1. **21 CFR 201.22 — FDA sulfite labeling mandate.** The only
   FDA-mandated allergen warning rule for drugs. Uses "allergic-type
   reactions including anaphylactic symptoms" (covers `allerg` /
   `anaphyla`). https://www.law.cornell.edu/cfr/text/21/201.22

2. **AAAAI/ACAAI 2022 Drug Allergy Practice Parameter (PMID 36122788).**
   Peer-reviewed vocabulary for drug hypersensitivity / anaphylaxis /
   allergic reactions.

3. **Advair Diskus §4 template (DailyMed).** Real-world DPI milk
   contraindication template: "contraindicated in patients with severe
   hypersensitivity to milk proteins" (covers `contraindicat` /
   `hypersens`).

**Known coverage gaps.** A label warning about an allergen using
vocabulary outside these 4 tokens would not be detected. Examples
the current vocabulary misses:
- "patients with **intolerance** to milk proteins" (no `intoler` token)
- "**adverse reactions** including respiratory distress" (no `adverse`
  / `react` tokens)
- "**sensitivity** to PEG should be considered" (no `sensit` token —
  `hypersens` requires the `hyper-` prefix)
- "**known reactivity**" / "**risk of**" allergen mentions

Vocabulary expansion + AI false-positive review is tracked as Task
#25 in `TASKS.md`.

### 5.2 The 80-character window is a heuristic, not empirically tuned

The 80-character window between allergen name and allergy-context
token was chosen as a heuristic ("roughly one sentence width"), not
empirically validated against a held-out set of confirmed warnings.
Per the project's "process before outcome" rule, we do not measure
window distances on already-matched warnings and back-derive a
"verified" window — that would be circular (the matcher already
filters at 80, so measurements would trivially confirm 80).

If the window is too tight, real warnings get missed (allergen name
in one clause, context word 90 chars away in the next clause —
same warning but not matched). If too loose, ingredient-list mentions
co-occurring with allergy-context words elsewhere in the same section
become false positives. Validation comes from the AI false-positive
sweep (Task #25), not from window-distance measurement.

### 5.3 Warning-text vocabulary vs validation-table vocabulary asymmetries (by design)

Warning detection runs against SPL warning-section TEXT. Flag
classification runs against excipient STRINGS in `excipients_raw`.
Different text domains, different vocabularies are appropriate. Two
specific asymmetries are kept by design:

- **`\bdairy` in milk warning detector but NOT in milk_validation.csv.**
  FARE doesn't list "dairy" as an ingredient (it's a category word).
  But real-world labels use "dairy allergy" as warning vocabulary, so
  the warning detector includes it. Flag classification stays
  FARE-anchored.

- **`\bPEG\b` in PEG warning detector but NOT in peg_validation.csv.**
  "PEG-allergic patient" is real label warning vocabulary. But the
  bare `\bPEG\b` regex matches 264 PEG-N derivative excipient strings
  (polysorbates, polyoxyl, BIS-PEG, mPEG, TPGS, etc.) that the
  tight-scope decision (§3.5 / §3.6) explicitly excludes. Adding it
  to the validation table would re-broaden flag classification past
  the tight scope. Kept in warning detector only.

These asymmetries are not bugs to be fixed; they reflect the
different rigor requirements of the two text domains.

### 5.4 Why bare-name patterns were rejected (warning detector)

An earlier version of `analyze_peg_labels.py` included bare-name
patterns (e.g. `\bpolyethylene\s+glycol`) that fired on any mention
of the allergen. This produced 3 false positives on the PEG
oral-solids slice (PARNATE, Tranylcypromine Sulfate, donepezil), all
of which were ingredient-list mentions embedded inside warning
sections — not warnings about PEG allergy. The
`ALLERGY_CONTEXT`-anchored rule eliminates this false-positive class.
Documented in `reconciliation_pass.md` Fix 1.

### 5.5 Per-allergen name fragments

Defined in each analyzer script (`MILK_NAME`, `PEG_NAME`,
`CARMINE_NAME`). All use word-boundary anchoring where needed to
avoid false substring hits (e.g. CARMINE vs CROSCARMELLOSE).

---

## Part 6 — Artifact dependency graph

Guidance for future changes. When any file in the left column is
modified, the corresponding scripts must be re-run and the listed
downstream docs must be re-checked for stale numbers.

| If you change… | Re-run | Re-check these doc sections |
| :--- | :--- | :--- |
| `data/fullcatalog/{milk,peg,carmine}_validation.csv` (or `build_allergens_validation.py`) | `flag_allergens_fullcatalog.py` → `analyze_allergens_fullcatalog.py` → appropriate label analyzer | `findings_*.md` §Prevalence; `methodology.md` §2.4 / §3.4 / §4.4; `methodology.md` §2.8 / §3.8 / §4.7 |
| `scripts/analyze_peg_labels.py` | `analyze_peg_labels.py` | `findings_peg.md` Layer 2; `limitations.md` §PEG |
| `scripts/analyze_dpi_labels.py` | `analyze_dpi_labels.py` | `findings_milk.md` Layer 2; `limitations.md` §Milk |
| `scripts/analyze_carmine_labels.py` | `analyze_carmine_labels.py` | `findings_carmine.md` Layer 2; `limitations.md` §Carmine |
| `scripts/analyze_allergens_fullcatalog.py` (any slice change) | `analyze_allergens_fullcatalog.py` | every `findings_*.md` §Prevalence and §Slice; `methodology.md` §2.8 / §3.8 / §4.7 |
| `scripts/allergen_filters.py` (shared DPI or oral-solid definitions) | all three label analyzers + `analyze_allergens_fullcatalog.py` | every `findings_*.md` §Slice; `methodology.md` §2.7; `limitations.md` §Filters |
| `scripts/spl_label_parser.py` (SPL section codes or classify_warning_level) | all three label analyzers | `findings_*.md` Layer 2 tables; `methodology.md` §5 |
| `ALLERGY_CONTEXT` or allergen-name fragments in any label analyzer | that analyzer | `findings_*.md` Layer 2; `limitations.md` §allergen; `methodology.md` §5 |
| `data/fullcatalog/dailymed_fullcatalog_raw.csv` (rebuild from new DailyMed snapshot) | entire pipeline | every number in every findings / methodology / narrative doc |
| any `research_{milk,peg,carmine}.md` claim | n/a | `methodology.md` Parts 2/3/4 UNII cross-refs; claim cross-cites in `narrative_draft.md` |

---

## Part 7 — Provenance

All scripts, validation tables, and outputs live in the repository.

**Scripts.**
- Validation-table build: `scripts/build_allergens_validation.py`.
- Flagger: `scripts/flag_allergens_fullcatalog.py`.
- Prevalence slicing: `scripts/analyze_allergens_fullcatalog.py`.
- Shared filters (DPI / oral-solid): `scripts/allergen_filters.py`.
- Shared SPL parser (warning-section extraction): `scripts/spl_label_parser.py`.
- Per-allergen label analyzers: `scripts/analyze_dpi_labels.py`,
  `scripts/analyze_peg_labels.py`, `scripts/analyze_carmine_labels.py`.
- FDA IID lookup: `scripts/fda_iid_lookup.py`.
- Corpus-test generator: `scripts/build_corpus_tests.py`.

**Data.**
- Raw catalog: `data/fullcatalog/dailymed_fullcatalog_raw.csv` (199,961 rows).
- Validation tables: `data/fullcatalog/milk_validation.csv`,
  `data/fullcatalog/peg_validation.csv`, `data/fullcatalog/carmine_validation.csv`.
- Flagged catalog: `data/fullcatalog/allergens_fullcatalog_flagged.csv`
  (199,961 rows × 49 columns).
- Label analyses: `data/fullcatalog/dpi_label_analysis.csv`,
  `data/fullcatalog/peg_label_analysis.csv`,
  `data/fullcatalog/carmine_label_analysis.csv`.
- Corpus tests: `data/fullcatalog/corpus_test_{milk,peg,carmine}.csv`.
- FDA IID snapshot: `FDA-IID-recent-update.csv` (project root,
  2026-04-22 download).

**Analysis docs.**
- Research briefs: `analysis/allergens/research_{milk,peg,carmine}.md`
  (primary-source facts with inline URLs per Task #15 rewrite).
- Findings: `analysis/allergens/findings_{milk,peg,carmine}.md`.
- Narrative draft: `analysis/allergens/narrative_draft.md`.
- Limitations: `analysis/allergens/limitations.md`.
- Literature: `analysis/allergens/literature.md`.
- Methodology: this file.
- Reconciliation pass tracking: `analysis/allergens/reconciliation_pass.md`.

**Logs.**
- Session log: `SESSION_LOG.md`.
- Cross-session task list: `TASKS.md`.
