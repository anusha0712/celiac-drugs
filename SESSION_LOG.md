## Session 2026-03-26

### What was completed
- Installed scientific-critical-thinking and scholar-evaluation skills from K-Dense-AI/claude-scientific-skills repo
- Created project folder structure (data/, analysis/)
- Completed Phase 1: paper analysis of Figueiredo et al. (2025)
  - Full scientific critical thinking assessment (methodology, bias, statistics, evidence quality, claims, logic)
  - Full ScholarEval framework evaluation (8 dimensions, composite score 2.9/5)
  - Answered all three key Phase 1 questions
  - Output saved to analysis/phase1_paper_analysis.md
- Defined story framing: information asymmetry / labeling transparency, NOT allergen contamination
- Built excipient_validation.csv (24 entries) — full EU-to-FDA naming crosswalk
- Built pull_dailymed.py with adaptive rate limiting, disk caching, and resume capability
- Completed DailyMed data pull: 6,636 products in dailymed_raw.csv
  - 4,973 analgesic/antipyretic (acetaminophen-containing)
  - 1,617 NSAID (ibuprofen-containing)
  - 3,257 single-ingredient, 3,333 combo products
  - 6,024 with inactive ingredients listed, 5,514 actively marketed
- Recovered 43 of 44 initial errors through three recovery passes:
  - 29 labels recovered via retry (transient network failures)
  - 10 prescription labels recovered by parsing DESCRIPTION prose (different XML structure)
  - 3 malformed XML labels recovered by scraping DailyMed web pages
  - 2 truly unrecoverable (404 — removed from DailyMed)

### Data decisions made

**Story framing:**
- This is a labeling transparency and regulatory gap story, not a toxicology or allergen contamination story
- The key narrative: celiac patients cannot reliably determine from drug labels whether their medications contain gluten-source excipients
- Key regulatory fact: FALCPA requires wheat disclosure in food but NOT in drugs

**Drug scope:**
- Dropped antiasthmatics/bronchodilators — 0% findings in source study add no journalistic value; story focuses on oral medications patients swallow
- Including combination products (e.g., Tylenol PM, NyQuil, Advil Cold & Sinus) — reflects real OTC landscape celiac patients face. Source study also included all products "containing paracetamol" and "containing ibuprofen"
- Including both OTC and prescription products — matches source study methodology. Whether to report separately or focus on OTC is still an open question

**Excipient classification:**
- Three-tier flagging system: `gluten_free` / `unknown` / `contains_gluten` (replaced source study's binary "non-gluten-free")
- Starch (source unspecified): flagged `unknown` — even though FDA CPG 578.100 says unqualified "starch" in the US legally = corn starch, a celiac patient reading the label wouldn't know this regulatory technicality
- Xanthan gum: flagged `unknown` — fermentation substrate may be wheat-derived, precautionary consistent with source study
- Oats: flagged `unknown` — not classified as gluten grain by FDA but cross-contamination well-documented
- Sodium carboxymethyl starch = sodium starch glycolate (same compound, different EU/US names) — flagged `unknown` unless source specified
- Croscarmellose sodium: flagged `gluten_free` — CRITICAL distinction, this is cellulose-based (wood pulp), NOT starch-based, often confused with sodium starch glycolate
- Maltodextrin: flagged `gluten_free` — despite "malt" in the name, corn-derived hydrolyzed starch product, unrelated to barley malt
- Source-specified starches (pregelatinized corn starch, modified corn starch, potato starch, tapioca starch, SSG Type A potato): all `gluten_free`
- New excipient policy: any excipient found in US data but not on Portuguese list must have documented rationale and source before being added to excipient_validation.csv

**Data source:**
- 100% DailyMed — the tool FDA recommends patients use (narrative integrity)
- OpenFDA rejected: ~40% coverage gap vs DailyMed (2,761 vs 4,685 acetaminophen products)
- DailyMed bulk download rejected: 33GB across 87K files, impractical
- Strategy: DailyMed API for set_id collection → DailyMed XML endpoint for label data → fallback to DESCRIPTION prose parsing → fallback to web page scraping
- DailyMed XML endpoint requires NO Accept header (returns 406 with `Accept: application/xml` — counterintuitive bug discovered and fixed during session)

**Raw data structure:**
- 39 columns capturing all available XML fields — philosophy is "capture everything, filter later"
- Added `active_ingredients`, `single_or_combo`, `active_ingredient_count` columns beyond CLAUDE.md spec
- Added UNII codes for both active and inactive ingredients
- Some SPL labels contain multiple `manufacturedProduct` blocks (different strengths/NDCs) — each becomes its own row. Deduplication strategy is an OPEN QUESTION

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The 44.4% "non-gluten-free" figure from the source study represents labeling ambiguity, not confirmed gluten presence. Based on Table 3 showing zero confirmed gluten grains. If any starches are wheat-derived, could represent real exposure. Journalist should present both interpretations.
- ⚠️ ASSUMPTION: DailyMed excipient data will be more specific about starch sources than INFOMED SmPCs. Needs verification when analyzing the pulled data.
- ⚠️ ASSUMPTION: Pre-gelatinized starch and sodium carboxymethyl starch in pharmaceutical products are predominantly corn/potato-derived. Consistent with industry practice but not verified for specific products.
- ⚠️ ASSUMPTION: DailyMed API search index is reasonably complete. Two 404s confirm it can list removed products; the reverse (missing recently added products) is unquantifiable. Could cross-reference against FDA NDC Directory but haven't done so.

### Methodological limitations identified
1. **Label-based only** — actual gluten protein levels are not measured. A product flagged `unknown` may contain zero gluten.
2. **Cross-contamination undetectable** — manufacturing cross-contamination cannot be identified from labels.
3. **DailyMed index completeness** — search API may not capture every product. Recently added or unusually indexed products could be missing.
4. **DailyMed index staleness** — 2 products appeared in search results but returned 404 on XML fetch (removed between indexing and retrieval).
5. **Multiple rows per label** — one SPL can produce multiple CSV rows for different strengths/NDCs. Deduplication strategy not yet decided — affects denominator for all percentages.
6. **Prescription label XML structure** — 10 prescription drugs used a different SPL format without structured `<ingredient>` elements. Recovered by parsing DESCRIPTION prose, but ingredient extraction from prose is less reliable than structured XML.
7. **3 malformed XML labels** — data recovered from web page scraping. Less structured than XML extraction.
8. **Combination products included** — some products contain acetaminophen or ibuprofen plus opioids, decongestants, etc. Different excipient profiles than single-ingredient OTC products. Whether to separate in analysis is an open question.
9. **Only 2 drug categories** — acetaminophen and ibuprofen. Not representative of full pharmaceutical market.
10. **Snapshot in time** — data pulled March 26, 2026. Formulations change; labels are updated. Results reflect this date only.

### Open questions for next session
1. **Deduplication strategy:** How to handle multiple rows from same SPL label? Options: deduplicate by set_id, by NDC, or keep all and report both counts.
2. **OTC vs prescription scope:** Report separately? Focus on OTC? Include both in totals?
3. **Index completeness:** Worth cross-referencing against FDA NDC Directory, or acknowledge as limitation?
4. **Second-pass excipient audit:** Need to extract all unique inactive ingredients from raw data and check for any gluten-adjacent excipients not on the Portuguese list.
5. **566 products with no inactive ingredients listed:** How to handle? Exclude from denominator, or count as a separate finding (labels that don't disclose excipients at all)?

### Where to pick up
Resolve open questions (deduplication, OTC/Rx scope, products with no ingredients). Then run second-pass excipient audit and build dailymed_flagged.csv.

---

## Session 2026-03-27

### What was completed
- Resolved all 5 open questions from previous session:
  1. Unit of analysis: NDC level (not set_id) — different NDCs under same label can have different excipients
  2. Reporting scope: OTC, Rx, and combined — all three views
  3. Index completeness: acknowledged as limitation, no spot-check against NDC Directory
  4. Second-pass excipient audit: extracted 511 unique excipient strings, built comprehensive 48-entry validation table
  5. No-data products: assigned `no_data` flag, analysis run with and without in denominator
- Misspelling sweep: searched DailyMed for common misspellings of both drugs
  - Found 5 "acetominophen" products; added 2 Scot-Tussin, excluded 2 withdrawn propoxyphene, 1 already captured
  - Zero ibuprofen misspellings found
- Rebuilt excipient_validation.csv from scratch — 48 entries from 3 sources (Portuguese study, FDA IIG, DailyMed data) with new column structure: fda_term, source, flag_decision, rationale, source_url, eu_equivalent
- Reclassified xanthan gum from `unknown` to `gluten_free` per National Celiac Association guidance
- Removed 33 injectable products from dataset (6,638 → 6,605)
- Built dailymed_flagged.csv — all 6,605 products flagged
- Completed Phase 3 analysis: all cuts of data (category, OTC/Rx, dosage form, cross-tabs, single/combo, sources of uncertainty, Portugal comparison)
- Created analysis/findings.md — objective data reporting (Sections 1–11) plus interpretation with scientific critical thinking (Section 12) plus collected assumptions (Section 13)
- Created analysis/limitations.md — full flagging methodology + 11 data collection limitations + 6 analytical limitations
- Removed standalone analysis/flagging_methodology.md (folded into limitations.md)
- Updated CLAUDE.md — Phase 2 and Phase 3 marked complete

### Decisions made
- **Unit of analysis: NDC** — two NDCs under same SPL label can have different excipient profiles (verified with Tylenol PM CVP HEALTH example)
- **Xanthan gum → gluten_free** — per National Celiac Association. Methodological departure from Portuguese study. Reduced unknown from 893 to 166 products. Source: https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/
- **Rice bran → gluten_free** — rice is not a gluten-containing grain (21 CFR 101.91). Source-specified bran evaluated independently from unspecified "bran" (which remains contains_gluten)
- **Maltitol, ethyl maltol, isomalt excluded from validation table** — chemically distinct from malt, not gluten-related. Substring "malt" is not sufficient to flag.
- **OTC/Rx determined by document_type field** — "HUMAN OTC DRUG LABEL" vs "HUMAN PRESCRIPTION DRUG LABEL" in DailyMed SPL XML
- **Injectables strictly excluded** — removed from both raw and flagged CSVs per user instruction
- **Findings.md must be objective** — data sections report numbers without editorializing; interpretation is in a clearly separated section with assumptions flagged and claims cited
- **Do not assert facts to fill in gaps** — corrected claim that unspecified SSG products are "pharmaceutically equivalent" to specified ones. The whole point of the unknown flag is that we don't know.

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The comparison to Portugal uses our `unknown` + `contains_gluten` as equivalent to their "non-gluten-free." Not perfectly equivalent — we reclassified xanthan gum and added a no_data category.
- ⚠️ ASSUMPTION: DailyMed labels accurately reflect current product formulations. Labels can lag behind reformulations. Snapshot as of March 26, 2026.
- ⚠️ ASSUMPTION: Products with no inactive ingredients listed (no_data) are not systematically different in gluten risk from products with data.
- ⚠️ ASSUMPTION: The source of SSG in the 154 unspecified products is unknown. Wheat-derived SSG exists in pharmaceutical manufacturing (Handbook of Pharmaceutical Excipients, 9th ed.).
- ⚠️ ASSUMPTION: High starch source disclosure rates reflect voluntary manufacturer practice, not regulatory mandate. Unverified whether FDA guidance recommends source disclosure.
- ⚠️ ASSUMPTION: OTC/Rx uncertainty difference reflects labeling pathway differences, not formulation differences.
- ⚠️ ASSUMPTION: KIT-level no_data is structural — individual components likely have their own excipient-bearing labels. Unverified. Patient-facing experience is still that KIT label provides no excipient info.
- ⚠️ ASSUMPTION: The wheat starch product's DailyMed label (NDC 70677-1244) reflects current formulation. Physical label not verified.
- ⚠️ ASSUMPTION: National Celiac Association guidance on xanthan gum is appropriate for this analysis. If incorrect for pharmaceutical-grade xanthan gum, 727 products would shift from gluten_free to unknown.

### Key findings
- **6,605 products** in final dataset (4,986 acetaminophen, 1,619 ibuprofen)
- **97.2% gluten_free** (excluding no_data), **2.7% unknown**, **0.02% contains_gluten**
- **1 product** with confirmed wheat starch: OTC ibuprofen tablet, NDC 70677-1244, Strategic Sourcing Services
- **92.8% of all uncertainty** from single excipient: SODIUM STARCH GLYCOLATE TYPE A (no source)
- **0% uncertainty** in liquid dosage forms (suspensions, solutions, liquids, liquid-filled capsules)
- **29.7% uncertainty** in extended-release tablets (highest dosage form) — spread across 16 store-brand manufacturers
- **OTC uncertainty (3.4%) > Rx uncertainty (0.6%)** — different excipients drive each
- **566 no_data products** — 428 are KITs (413 OTC), 138 are individual products with no excipient info

### Open questions for next session
- None blocking. All phases complete. Next step is writing the journalism piece using findings.md as the data backbone.

### Where to pick up
Phase 1–3 complete. All data, analysis, and methodology documented. Ready to begin writing the journalism piece or any additional analysis the journalist wants to explore.

---

## Session 2026-03-27 (afternoon)

### What was completed
- Conducted deep research for BBC Health pitch across three parallel workstreams:
  1. **BBC clip search:** Searched bbc.com and bbc.co.uk across 7 query variations for coverage of gluten in medications, celiac medication safety, and FDA drug allergen labeling. Zero results found. BBC domains block Anthropic web crawler (caveat noted), but niche specificity of topic strongly suggests genuine coverage gap.
  2. **World context research:** Verified regulatory landscape (FALCPA excludes drugs, FDA CPG 578.100 starch rule, 2017 draft guidance never finalized, ADINA Act H.R. 3821 reintroduced June 2025), celiac prevalence (~2M Americans per NIDDK), clinical thresholds (Catassi 2007: 50mg/day causes damage), and recent policy developments.
  3. **Hook research:** Found peer-reviewed case report (PMC10958639, 2024) of celiac patient harmed by wheat starch in prednisone. Found Beyond Celiac FDA-funded survey (5,623 patients, 24.9% suspected medication reactions). Found pharmacist knowledge study (52% identification rate). Found Walgreens policy declining to counsel on gluten-free status.
- Compiled 16-source master source list with URLs verified via WebFetch/WebSearch
- Wrote 298-word BBC Health pitch (3 paragraphs, every claim annotated with source references)
- Saved pitch to `analysis/bbc_pitch.md`
- Created `pitch-info/` folder with three documents for handoff to another agent:
  1. `pitch.md` — current pitch draft with source annotations
  2. `deep-research.md` — full background research including problem landscape for celiac patients, regulatory gap, source study context, BBC coverage search, academic sources, and numbered master source list
  3. `project-summary.md` — objective summary of entire project workflow, all three phases, key data results with tables, methodology, file map, assumptions, and limitations

### Decisions made
- **Pitch framing:** Patient scenario opening (celiac patient with acetaminophen bottle, SSG with no source), grounded in CDF guidance and 2024 case report. Regulatory reality before statistics.
- **"Nearly 30%" figure in pitch:** From findings.md Section 6.3 — 22 of 74 extended-release acetaminophen tablets (29.7%) list SSG Type A without source specified.
- **BBC coverage gap claim:** Stated as definitive in pitch, with caveat about crawler block noted in editor's note and deep-research.md. Recommended journalist verify by searching bbc.com directly.
- **Pitch style:** No em-dashes, no colons, no sensationalist language. BBC Health register. Findings described as "preliminary."

### Assumptions flagged this session
- ⚠️ ASSUMPTION: BBC has not covered gluten in medications. Based on zero results across 7 search queries. Caveat: BBC blocks Anthropic web crawler, which may suppress results. General celiac coverage almost certainly exists on BBC but medication-specific angle is likely a genuine gap. Should be verified manually.
- ⚠️ ASSUMPTION: The ADINA Act (H.R. 3821) status as described in January 2026 Allergic Living article is current as of March 2026. Legislative status may have changed.
- ⚠️ ASSUMPTION: The Catassi 2007 threshold of 50mg/day causing intestinal damage is still the consensus clinical reference point. More recent studies may have refined this.

### Open questions for next session
- Pitch needs journalist review and possible revision before submission
- BBC coverage gap should be manually verified by searching bbc.com directly
- ADINA Act legislative status should be checked for any updates since January 2026

### Where to pick up
Pitch draft and all supporting materials in `pitch-info/` folder, ready for handoff to another Claude agent or for journalist review and revision.

---

## Session 2026-04-07

### What was completed
- Expanded project scope from acetaminophen/ibuprofen pilot to full DailyMed catalog
- Explored bulk-data/ directory structure: 159,431 ZIP files across 4 DailyMed download
  categories (human-otc: ~87K, human-prescription: ~54K, homeopathic: ~16K, other: ~2.5K)
- Investigated ZIP/XML structure: each ZIP = 1 SPL XML + images, ZIP filename = {date}_{set_id}.zip,
  XML filename = document_id
- Researched homeopathic regulation: homeopathic products use `HUMAN OTC DRUG LABEL` as
  document_type in XML (same LOINC code as regular OTC). Distinction is via marketing_status
  ("unapproved homeopathic") and DailyMed's download categorization
- Researched "other" category: DailyMed's "Remainder Labels" — vaccines, medical devices,
  bulk ingredients, dietary supplements, allergenics, plasma derivatives, animal drugs
- Created `extract_bulk.py` — adapted XML parsing from `pull_dailymed.py`, added:
  - `bulk_category` (from folder), `source_zip` (from filename), `dea_schedule` (from XML)
  - Removed injectable filtering, removed drug-specific category logic
  - No network calls, no AI inference — pure mechanical extraction
- Ran full extraction: 159,431 ZIPs → 199,961 product rows, 0 errors, 3.5 minutes
- Validated output: all 4 bulk_category values present, document_type distribution sensible,
  DEA schedules captured (7,984 controlled substance products), case inconsistency noted
  in document_type values
- Documented all data decisions in CLAUDE.md under "Bulk Extraction Decisions (2026-04-07)"

### Decisions made
- **All decisions documented in CLAUDE.md** — see "Bulk Extraction Decisions (2026-04-07)"
  section for full details with rationale and sources
- Key decisions: no filtering at extraction, all fields from XML/folder/filename only,
  brand_generic from FDA application number convention (ANDA/NDA/BLA), bulk_category from
  folder not XML, old category column dropped, DEA schedule added as new field

### Assumptions flagged this session
- No assumptions were made. All extraction is mechanical (XML parsing + folder/filename
  string parsing). The only logic-based field is brand_generic, which uses a documented
  FDA convention with source cited.

### Open questions for next session
- **document_type case inconsistency:** DailyMed data has mixed casing (e.g. "HUMAN
  PRESCRIPTION DRUG LABEL" vs "Human Prescription Drug Label"). Should be normalized
  in analysis — decide on uppercase or as-is.
- **What analysis to run on the full catalog?** The pilot focused on gluten excipients
  in acetaminophen/ibuprofen. The full catalog opens up broader questions.
- **Update output file structure in CLAUDE.md** to reflect new files (extract_bulk.py,
  dailymed_bulk_raw.csv).

### Where to pick up
Full catalog extracted to `data/dailymed_bulk_raw.csv` (199,961 rows, 43 columns).
Pilot data moved to `data/eda/`. Next step: **build the excipient list** for the full catalog.

---

## Session 2026-04-09

### What was completed
- Built complete excipient validation table for the full DailyMed catalog
- Created `build_excipient_list.py` — extracts unique excipient strings from the bulk CSV,
  runs word-boundary keyword search, subtracts terms already in the pilot table, outputs
  a research worklist
- Ran extraction on `data/dailymed_bulk_raw.csv`:
  - 199,961 rows, 11,508 with no excipients
  - 10,019 unique excipient strings (case-normalized to uppercase)
  - 130 keyword matches; 23 already in pilot table; 107 new terms
- Looked up UNII codes for key new terms via the bulk data's `excipient_uniis` column
- Researched and classified all 107 new terms:
  - 36 → `gluten_free` (15 source-specified non-gluten starches/derivatives + 21 gums)
  - 23 → `contains_gluten` (16 wheat derivatives + 7 barley derivatives)
  - 26 → `unknown` (9 source-unspecified starches + 17 oat-related entries)
  - 22 → false positives, excluded from table
- Created `build_validation_table.py` — one-shot generator that copies pilot entries
  (with bulk catalog counts appended), adds 85 new entries, and writes the combined CSV
- Generated `data/bulk/excipient_validation.csv` — 133 entries total
  (48 pilot + 85 new). Final flag distribution: gluten_free=64, unknown=38, contains_gluten=31
- Documented all decisions in CLAUDE.md under new "Bulk Excipient Validation Decisions" section

### Decisions made
- **Keyword sources for the search:** combined the Portuguese study's Table 1 excipient list
  (wheat, rye, barley, semolina, bran, malt, oats, starch, glucose, pregelatinized, etc.),
  Latin botanical names for gluten grains (avena, triticum, hordeum, secale — needed for
  homeopathic and cosmetic-style naming), and starch chemistry terms (glycolate, dextrin,
  gum) — 20 keywords total
- **Word-boundary regex (`\b...\b`)** instead of substring matching, to avoid catching
  "oat" inside "coated", etc.
- **All wheat/barley/rye derivatives → contains_gluten** regardless of plant part or
  processing. Rationale: project framing is labeling transparency, not toxicology. If the
  label says "wheat," a celiac patient sees wheat. Whether actual gluten content is below
  20 ppm is a separate question. Affects: WHEAT GERM, WHEAT BRAN, WHEAT GERM OIL,
  HYDROLYZED WHEAT PROTEIN (143+25 products), CETEARYL WHEAT STRAW GLYCOSIDES,
  HORDEUM VULGARE TOP/ROOT, BARLEY MALT, etc.
- **All oat derivatives → unknown** consistent with pilot's OATS classification. Oats are
  not a gluten grain per FDA but cross-contamination is documented. Affects 17 entries.
- **AMINO ACIDS, CORN GLUTEN → gluten_free.** "Corn gluten" (zein) is NOT wheat gluten.
  Corn is not a gluten-containing grain per FDA 21 CFR 101.91.
- **ALUMINUM STARCH OCTENYLSUCCINATE → unknown** (861 products) — modified starch with
  source not specified on label. Highest-impact new entry — larger than the pilot's
  entire `unknown` category (166 products).
- **HYDROXYETHYL STARCH 130/0.4 → unknown** despite being invariably waxy maize-derived
  in pharmaceutical practice. Project rule is label-based, not industry-knowledge-based.
- **GLUCOSE (standalone) → unknown** consistent with pilot's GLUCOSE SYRUP / LIQUID GLUCOSE.
- **SODIUM POLYACRYLATE STARCH variants → unknown** despite being highly processed
  superabsorbent polymers. Consistent with project rule: starch with no source = unknown.
- **All gums → gluten_free** including dehydroxanthan gum (follows xanthan reasoning)
- **22 false positives excluded from table:** glycolate esters (5), methyl glucose esters (6),
  glucose biochemicals (8), cyclodextrin (1), DIMETHICONOL GUM (silicone polymer)
- **Pilot entries preserved with bulk count annotation.** Each rationale gets
  `Bulk catalog: N products.` appended; original text unchanged. Source field gets
  `|dailymed_bulk` appended where applicable.
- **File location:** `data/bulk/` directory mirrors `data/eda/` (pilot). Pilot files
  untouched.

### Key findings (notable count changes from pilot to bulk)
- SODIUM STARCH GLYCOLATE TYPE A (no source): pilot 154 → bulk **1,123** products
- XANTHAN GUM: pilot 727 → bulk **9,268** products
- STARCH, CORN: pilot 2,801 → bulk **26,409** products
- WHEAT (standalone): pilot 0 → bulk **22** products (likely homeopathic)
- BARLEY (standalone): pilot 0 → bulk **89** products
- RYE (standalone): pilot 0 → bulk **4** products
- New high-impact entry: ALUMINUM STARCH OCTENYLSUCCINATE = **861** products

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The 20 keywords used in the gluten-adjacent search are comprehensive.
  If a gluten-related excipient uses naming with no overlap to these keywords, it would
  be missed. Mitigation: cross-reference against pilot's 48-entry table caught all
  previously-known gluten terms; the new search added 85 more.
- ⚠️ ASSUMPTION: All 22 false positive exclusions are truly not grain-derived. The methyl
  glucose esters use glucose as a synthetic feedstock that is itself derived from corn
  starch in industry practice — but the resulting compounds are highly processed
  cosmetic emulsifiers with no protein content. The 8 glucose biochemicals are
  laboratory/biochemical reagents.
- ⚠️ ASSUMPTION: SODIUM POLYACRYLATE STARCH variants should be flagged unknown.
  These are highly cross-linked superabsorbent polymers where any starch protein is
  likely destroyed during synthesis. Following the project's strict label-based approach
  (consistent with how unspecified pregelatinized starch is handled).
- ⚠️ ASSUMPTION: Wheat-derived oils, hydrolyzed proteins, and straw glycosides should all
  be flagged contains_gluten despite processing that may reduce gluten content. Rationale
  is labeling transparency, not toxicology. Some celiac organizations consider highly
  refined wheat oils safe for celiac patients, but the label still identifies wheat.
- ⚠️ ASSUMPTION: HORDEUM VULGARE TOP, ROOT, and other non-grain barley plant parts should
  be flagged contains_gluten. The grain (seed) is where gluten resides, but the label
  identifies barley. A celiac patient seeing "Hordeum vulgare" would not parse anatomy.
- ⚠️ ASSUMPTION: Flagging is exact-match string lookup with case normalization (`.upper()`)
  applied at lookup time. Mixed-case orphan strings in the bulk data (113 of them) contain
  zero gluten-adjacent terms, so no information loss expected.

### Open questions for next session
- Apply the validation table to the full bulk catalog (write `flag_bulk.py` to produce
  `data/bulk/dailymed_bulk_flagged.csv`)
- Run analysis on the flagged full catalog: by drug category, dosage form, OTC/Rx,
  manufacturer, etc. The pilot was acetaminophen + ibuprofen only; the full catalog will
  reveal whether the labeling transparency gap is similar across other drug classes.
- Decide whether to filter routes (the bulk extraction includes all routes; topicals,
  injectables, etc.). Per CLAUDE.md, filtering is an analysis-step concern.

### Where to pick up
Validation table complete. Next: write `flag_bulk.py` to apply gluten flags to all
199,961 rows of `data/dailymed_bulk_raw.csv` using `data/bulk/excipient_validation.csv`.

---

## Session 2026-04-09 (afternoon)

### What was completed
- Reorganized scripts: created `scripts/` folder and moved all 4 Python files
  (`extract_bulk.py`, `pull_dailymed.py`, `build_excipient_list.py`,
  `build_validation_table.py`) into it. Updated path constants in 3 scripts to use
  `Path(__file__).parent.parent` so they still resolve to project root.
- Cross-checked the bulk validation table against an external celiac reference
  (Gluten Intolerance Group "Medications and the Gluten-Free Diet" PDF, found by user
  in Downloads). Identified the source as GIG, January 2019 — flagged as STALE per
  the project's 5-year rule.
- Cross-checked against National Celiac Association "Ingredients People Question" page
  (https://nationalceliac.org/ingredients-people-question/) — current source.
- Identified 2 conflicts (GLUCOSE, GLUCOSE family flagged unknown but NCA says
  gluten_free) and 1 confirmation (MALTODEXTRIN matches NCA gluten_free).
- Discovered cyclodextrins as a major gap (15 string variants, 559 product appearances,
  381 unique products) — none matched the original 20 keywords, missed by keyword search.
  Routes: 195 topical, 103 oral, 49 IV, plus IM/ophthalmic/etc.
- Discovered 2 additional gaps: ICODEXTRIN (186 products, peritoneal dialysis polymer
  derived from maltodextrin) and MALTODEXTRIN/VP COPOLYMER (1000 MPA.S) (2 products).
- Created `analysis/validation_table_review.md` to rigorously catalogue all pending
  changes with source provenance for each decision.
- Created "Open Questions for Pharmacist Consultation" section with 8 questions
  (Q1: ASO, Q2: SSG, Q3: cyclodextrins, Q4: maltodextrin, Q5: HES 130/0.4, Q6: HSH,
  Q7: source-unspecified starches, Q8: oats).
- Applied all changes to `scripts/build_validation_table.py`:
  - Added PILOT_OVERRIDES dict for bulk-table revisions to pilot entries (keeps pilot
    CSV pristine as historical record).
  - Added 15 cyclodextrin entries flagged gluten_free.
  - Added ICODEXTRIN and MALTODEXTRIN/VP COPOLYMER as gluten_free.
  - Added 21 false-positive entries as gluten_free with rationale "Keyword false
    positive — not grain-derived" (Option A: validation table = single source of truth).
  - Updated GLUCOSE entry from unknown → gluten_free.
  - Updated GLUCOSE SYRUP, LIQUID GLUCOSE, MALTODEXTRIN via PILOT_OVERRIDES dict.
  - Fixed: HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE) was previously
    excluded as a false positive but is actually a cyclodextrin variant — moved to
    cyclodextrin group.
- Re-ran `build_validation_table.py` → regenerated `data/bulk/excipient_validation.csv`
  with 171 entries (was 133): 105 gluten_free, 35 unknown, 31 contains_gluten.
- Verified all overrides applied correctly via spot-check (14/14 pass).
- Updated CLAUDE.md "Bulk Excipient Validation Decisions" section to reflect:
  - Total entry count revised to 171
  - False-positive section rewritten to note Option A (now in table, not excluded)
  - GLUCOSE family decision updated to gluten_free with NCA citation
  - New entries documented: cyclodextrins (interim, stale source), ICODEXTRIN, VP copolymer
  - New "Source provenance rule" subsection (5-year cutoff, current vs stale)

### Decisions made
- **Source provenance rule:** All classification decisions cite sources. Sources are
  flagged current (≤5 years) or stale (>5 years). Decisions on stale sources only
  are flagged for re-evaluation. Rule applies because celiac science and pharmaceutical
  labeling guidance evolve quickly.
- **GLUCOSE family → gluten_free** per NCA "Ingredients People Question" current
  guidance: glucose syrup processing reduces gluten below 20 ppm regardless of
  starting material. Affects GLUCOSE (42 products), GLUCOSE SYRUP (0), LIQUID GLUCOSE (0).
- **MALTODEXTRIN keep gluten_free**, add NCA URL as supporting source. Maltodextrin is
  a LINEAR starch hydrolysate, distinct from cyclodextrin (cyclic). Decisions NOT chained.
- **Cyclodextrins → interim gluten_free** (15 string variants, 381 products) per GIG
  2019 PDF. ⚠️ Source is stale. Pending pharmacist consultation (Q3).
- **ICODEXTRIN → gluten_free**. Chains from maltodextrin (current NCA source).
- **MALTODEXTRIN/VP COPOLYMER → gluten_free**. Chains from maltodextrin.
- **Oats → keep `unknown`** for now per user instruction. Added to pharmacist
  consultation list (Q8). 525 products affected, 98.5% topical/cutaneous, only 4 oral.
- **ASO → keep `unknown`** for now. 859/861 are topical. Added to pharmacist list (Q1).
- **SSG (no source) → keep `unknown`** for now. Added to pharmacist list (Q2).
- **False positives (21) → add to validation table as gluten_free with "Keyword false
  positive" rationale (Option A).** Makes validation table the single source of truth.
- **Pilot CSV preserved untouched.** Bulk-table revisions to pilot entries are applied
  via PILOT_OVERRIDES dict in `build_validation_table.py`. Pilot CSV remains the
  historical snapshot of pilot-era decisions.

### Errors corrected during session
- I fabricated that the NCA "Ingredients People Question" page lists cyclodextrins.
  It does not. Removed the false claim. Cyclodextrins are only listed in the screenshot
  the user provided (later identified as GIG 2019 PDF).
- I cited Plogsted 2007 ("Medications and Celiac Disease," Practical Gastroenterology)
  when researching cyclodextrins. The article is 19 years old, exceeds the 5-year rule.
  Removed from citation list.
- I conflated maltodextrin and cyclodextrin reasoning, suggesting that revisiting
  cyclodextrin classification might also affect maltodextrin. Corrected: maltodextrin
  is a linear polysaccharide; cyclodextrin is a cyclic oligosaccharide. They are
  chemically distinct and their classifications are not chained. Maltodextrin's
  gluten_free flag rests on current NCA guidance, not on the GIG 2019 PDF.
- HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE) was previously
  excluded as a "false positive" — it is actually a cyclodextrin variant. Moved to
  the cyclodextrin group.

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The Gluten Intolerance Group's January 2019 classification of
  cyclodextrins as "could be derived from wheat or barley" is the basis for our
  interim cyclodextrin = gluten_free flag. The GIG document is >5 years old. No
  current source explicitly addresses cyclodextrin source labeling in pharmaceuticals.
  Pending pharmacist consultation.
- ⚠️ ASSUMPTION: ICODEXTRIN and MALTODEXTRIN/VP COPOLYMER follow MALTODEXTRIN's
  classification because they share the linear maltodextrin polysaccharide as a
  building block. Not independently sourced.
- ⚠️ ASSUMPTION: SODIUM POLYACRYLATE STARCH variants are flagged unknown despite
  being highly processed superabsorbent polymers. Decision is consistent with the
  project's strict label-based rule but may overstate concern in practice.

### Open questions for next session
- Resolve cyclodextrin classification with a current source or pharmacist input
- Apply the validation table to the full bulk catalog (write `flag_bulk.py` →
  `data/bulk/dailymed_bulk_flagged.csv`)
- Decide whether to filter analysis to oral routes only (user mentioned this)
- Pharmacist consultation list (Q1-Q8) ready when contact is possible

### Where to pick up
Validation table at 171 entries. CLAUDE.md and SESSION_LOG.md updated. Pilot CSV
preserved. Pending changes catalogued in `analysis/validation_table_review.md`.
Next: write `flag_bulk.py` to apply gluten flags to all 199,961 rows.

---

## Session 2026-04-10

### What was completed
- Designed and locked the 6-step bulk filter pipeline restricting the 199,961-row
  raw catalog to 72,358 rows of FDA-recognized human medications delivered to the
  GI tract by swallowing
- Wrote `scripts/filter_bulk.py` implementing the pipeline (deterministic pandas;
  no AI / LLM / inference)
- Wrote `scripts/flag_bulk.py` applying the 171-entry validation table to the
  filtered output via the worst-excipient rule
- Generated `data/bulk/dailymed_bulk_filtered.csv` (72,358 rows × 43 columns)
- Generated `data/bulk/dailymed_bulk_flagged.csv` (72,358 rows × 45 columns):
  68,277 gluten_free (94.36%), 3,041 no_data (4.20%), 1,028 unknown (1.42%),
  12 contains_gluten (0.02%)
- Documented the entire pipeline in CLAUDE.md "Bulk Filtering Decisions (2026-04-10)"
  subsection
- Documented limitations in `analysis/limitations.md` Part 4 (loss of grandfathered
  drugs, OTC monograph included without individual NDA review, possible
  approval_type misclassifications, SPL inconsistencies, KIT cross-reference,
  homeopathic false-negative risk, methodology departure from pilot)
- Added "Final Verification" subsection to README.md (manual excipient table
  check with pharmacist; verify human drugs in animal bulk downloads)
- Resolved Tasks #1 (homeopathic regulations — moot since homeopathics excluded)
  and #2 (oral-adjacent routes — locked to ORAL only)

### Decisions made
- **Methodology statement:** "FDA-recognized human medications directly delivered
  to the GI tract by swallowing." Excludes biologics, animal products, dietary
  supplements, devices, cosmetics, bulk ingredients, mouth-only delivery, inhaled,
  injected, topical, transdermal, homeopathic, herbal/traditional supplements,
  foreign-imported unapproved products, and grandfathered marketed-unapproved drugs.
- **6-step filter pipeline (locked order, though order doesn't change result):**
  1. document_type — keep only HUMAN OTC / HUMAN RX / HUMAN RX WITH HIGHLIGHTS / HUMAN COMPOUNDED
  2. bulk_category — drop homeopathic
  3. route — keep only ORAL
  4. dosage_form — drop mouth-only forms (lozenges, mouthwash, dental, etc.),
     wrong-route data errors (injection, aerosol, cream, etc.), and other
     not-swallowed forms (spray, gel, film, strip, ODT)
  5. approval_type — keep only ANDA / NDA / NDA AG / BLA / OTC monograph
  6. mouthwash-by-name slip cleanup
- **ODTs and dissolvable films are dropped** under the swallowing criterion despite
  being borderline (they dissolve in the mouth and are partly absorbed via mucosa,
  not GI). User explicitly accepted this.
- **KITs and Pellets (non-homeopathic) and Crystal (Epsom salt) are kept** because
  their contents are swallowed.
- **Grandfathered marketed-unapproved drugs explicitly excluded** as documented trade-off.
  Loses ~600 rows of legitimate medications (Phenobarbital, Armour Thyroid, Donnatal,
  Salsalate, etc.) in exchange for a clean defensible "FDA-recognized" cut.
  Manual classification of the 400 unique active ingredients in `unapproved drug other`
  bucket was considered as alternative but rejected to keep methodology simple.
- **Two-script split:** `filter_bulk.py` produces filtered raw, `flag_bulk.py` reads
  filtered raw and writes flagged. Cleaner separation than a single combined script.
- **No audit file** (`dailymed_bulk_excluded.csv`) per user decision.

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The `approval_type` field in DailyMed accurately reflects each
  product's FDA regulatory status. The field is manufacturer-supplied, not
  independently verified by FDA. Spot-checks suggest reliability for major
  categories but rare misclassifications cannot be ruled out.
- ⚠️ ASSUMPTION: Dropping the entire `unapproved drug other` bucket is acceptable
  for the celiac journalism story even though it loses real grandfathered medications
  (Phenobarbital, Armour Thyroid, Donnatal, etc.). A celiac patient on these drugs
  would not benefit from this analysis.
- ⚠️ ASSUMPTION: Homeopathic-style products that are tagged as ordinary OTC monograph
  or NDA in `approval_type` would slip through both Step 2 (bulk_category) and
  Step 5 (approval_type) filters. Spot-checks during pipeline development found this
  is rare, but Schwabe-type mixed manufacturers may produce edge cases.
- ⚠️ ASSUMPTION: Filter step 6 (mouthwash-by-name slip) catches all relevant
  mouthwash products that bypassed Step 4. Other inconsistencies between drug_name,
  dosage_form, and route columns likely exist that we did not detect.
- ⚠️ ASSUMPTION: ODTs and dissolvable films should be dropped because their active
  ingredient is mostly absorbed via buccal/sublingual mucosa rather than the GI tract.
  Some ODTs (Zofran ODT, Claritin RediTabs) are designed for convenience rather than
  buccal absorption, and the active ingredient may largely reach the GI tract via
  saliva swallowing — but the line is drawn here for consistency.

### Key results
- **Final filtered dataset:** 72,358 rows (199,961 → 72,358, 63.81% drop)
- **Per-step drops:**
  - Step 1 document_type: −6,507 (3.25%)
  - Step 2 bulk_category homeopathic: −19,940 (10.31%)
  - Step 3 route not ORAL: −96,334 (55.52%)
  - Step 4 dosage form: −3,174 (4.11%)
  - Step 5 approval_type: −1,619 (2.19%)
  - Step 6 mouthwash slip: −29 (0.04%)
- **Bulk_category breakdown (final):** 56,400 human_prescription + 15,958 human_otc
- **Gluten flag distribution:** 68,277 gluten_free / 3,041 no_data / 1,028 unknown / 12 contains_gluten
- **Pilot wheat-starch product confirmed** in flagged output: NDC 70677-1244 Strategic
  Sourcing Services Ibuprofen, flagged contains_gluten with `STARCH, WHEAT` as the
  triggering excipient

### Open questions for next session
- Run analysis on the flagged bulk dataset (by drug class, manufacturer, dosage form,
  etc.) — same cuts as the pilot but on the broader dataset
- Final Verification items in README.md remain pending: manual pharmacist review of
  validation table, verification against animal bulk downloads
- Cyclodextrin classification still rests on a stale (GIG 2019) source pending
  pharmacist consultation (Q3 in `analysis/validation_table_review.md`)

### Where to pick up
Filtered dataset (72,358 rows) and flagged dataset are ready at
`data/bulk/dailymed_bulk_filtered.csv` and `data/bulk/dailymed_bulk_flagged.csv`.
Next: run analytical cuts on the flagged dataset and compare to pilot results.

---

## Session 2026-04-10 (afternoon — bulk analysis)

### What was completed
- Wrote `scripts/analyze_bulk.py` — deterministic pandas script that reads
  `data/bulk/dailymed_bulk_flagged.csv` and generates `analysis/bulk_findings.md`
  in one pass. Every table in the findings document comes from the same
  in-memory dataframe. Rerunning the script produces a byte-identical file.
- Generated `analysis/bulk_findings.md` — 10 objective data sections, no
  interpretation section. Strict no-editorializing rule applied.
- Verified output: zero banned interpretive words in the generated document
  (grep pass for notably/remarkably/suggests/indicates/reveals/etc. returned
  only the false positive "with highlights" which is the literal document_type
  name "HUMAN PRESCRIPTION DRUG LABEL WITH HIGHLIGHTS").

### Decisions made
- **Interpretation section deliberately omitted** from bulk_findings.md.
  Per the user's explicit instruction ("findings not be editorialized"),
  the entire document is objective data reporting. Interpretation is deferred
  to the journalist, who can write a separate interpretive document using
  bulk_findings.md as the data backbone.
- **Analysis structure reorganized** vs pilot findings.md, which the user
  characterized as "quite bad." Specific improvements:
  - Added an Executive Summary block with headline numbers at the top
  - Consolidated 15+ small tables from the pilot into fewer richer ones
  - Enforced a single denominator convention (all percentages exclude no_data
    unless column header says otherwise)
  - Moved "confirmed gluten products" to Section 3 (was Section 8 in pilot —
    buried lead)
  - Single consolidated "Sources of uncertainty" section with one table
    (pilot scattered this across 4+ sections)
  - No separate "All Assumptions" appendix (pilot Section 13 duplicated
    Section 12 flags)
- **Code-generated markdown** instead of hand-written. Eliminates transcription
  errors. Script owns the numbers; markdown is a render artifact.
- **Breakdowns consolidated** into Section 4 with 6 subsections (regulatory
  category, dosage form, single/combo, DEA schedule, active ingredient,
  manufacturer). One table per subsection, all with the same column layout
  (n / gluten_free% / unknown% / contains_gluten% / no_data%).
- **Pilot subset comparison (Section 7)** extracts acetaminophen + ibuprofen
  from bulk data and compares to pilot numbers, noting that row counts and
  percentages will differ because of stricter bulk filters.

### Assumptions flagged this session
- ⚠️ ASSUMPTION: The bulk analysis report contains zero interpretation. If
  the journalist wants analytical framing they must write it separately.
  This is a deliberate methodological stance, not an oversight.
- ⚠️ ASSUMPTION: The pilot subset comparison assumes all bulk rows with
  ACETAMINOPHEN or IBUPROFEN in `active_ingredients` are comparable to the
  pilot dataset, even though the pilot also included products the bulk
  pipeline drops (lozenges, films, ODTs, grandfathered Armour Thyroid
  combinations, etc.). Row counts will differ.
- ⚠️ ASSUMPTION: Active ingredient grouping in Section 4.5 uses the raw
  label string without consolidating salt forms or ingredient ordering.
  Different orderings of the same combination show as separate rows.
- ⚠️ ASSUMPTION: Manufacturer grouping in Section 4.6 uses the raw label
  string. Variant spellings of the same company appear as separate rows.

### Key outputs
- `scripts/analyze_bulk.py` — 450+ lines, deterministic, no AI/LLM
- `analysis/bulk_findings.md` — 16,796 bytes, 10 sections, covers 72,358 rows

### Open questions for next session
- Does the journalist want an interpretive companion document to
  `bulk_findings.md`? If so, that is a separate writing task.
- Should the `bulk_findings.md` script be rerun periodically as DailyMed
  updates, or is this a one-time snapshot for the journalism piece?
- Final Verification items in README.md remain pending: manual pharmacist
  review of validation table, verification against animal bulk downloads.

### Where to pick up
Bulk findings document generated. All objective data cuts complete. Next:
journalist review of `analysis/bulk_findings.md` and decision on whether
to write an interpretive companion document or integrate findings directly
into the journalism piece.

## Session 2026-04-10 (addendum)

### What was completed
- Added `.gitignore` at project root covering macOS `.DS_Store`, Python
  caches/venvs, `bulk-data/`, `data/dailymed_bulk_raw.csv`, and editor
  files (`.vscode/`, `.idea/`, `*.swp`).

### Decisions made
- Only `data/dailymed_bulk_raw.csv` is ignored under `data/` — all other
  files in `data/` (including the ~60M filtered and flagged bulk CSVs and
  everything in `data/eda/` and `data/bulk/`) remain tracked. Rationale:
  `dailymed_bulk_raw.csv` is 165M and exceeds GitHub's 100MB per-file limit.
  The two ~60M derived CSVs are under the limit and kept in-repo.
- Broader wildcard patterns under `data/` were considered and rejected —
  user wants every non-raw file in `data/` tracked.

### Open questions for next session
- If the repo is pushed to GitHub, the two ~60M bulk CSVs
  (`dailymed_bulk_filtered.csv`, `dailymed_bulk_flagged.csv`) will bloat
  the repo permanently. Consider Git LFS if this becomes a concern.

### Where to pick up
`.gitignore` in place. Project ready for `git init` / first commit.

