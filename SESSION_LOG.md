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


## Session 2026-04-21

### What was completed
- Extended the gluten workflow to three additional allergens: milk
  proteins / lactose, polyethylene glycol (PEG), and carmine / cochineal.
- Phase 1: three parallel Explore agents produced per-allergen research
  briefs + UNII/PMID/CFR fact-check logs. Outputs in `analysis/allergens/`:
  `research_{milk,peg,carmine}.md`, `factcheck_log_{milk,peg,carmine}.csv`,
  `carmine_dailymed_hits.csv` (168 unique carmine products).
- Phase 2: `scripts/build_allergen_validation_tables.py` generates three
  per-allergen validation tables under `data/bulk/`:
  `milk_validation.csv` (63 entries: 34 contains_milk + 29 milk_free
  false-positive exclusions), `peg_validation.csv` (21 regex patterns),
  `carmine_validation.csv` (11 exact + 1 regex).
- Phase 3: `scripts/flag_allergens.py` applies all three flags in one pass
  over the RAW `data/dailymed_bulk_raw.csv` (199,961 rows, unfiltered),
  writing `data/bulk/dailymed_allergens_flagged.csv` with six new columns
  (milk_flag, milk_flagged_excipients, peg_flag, peg_flagged_excipients,
  carmine_flag, carmine_flagged_excipients) plus the full original schema
  (49 total columns).
- Phase 3 supporting: `scripts/analyze_allergens.py` computes
  category-sliced prevalence used in the findings docs.
- Phase 4: three findings docs under `analysis/allergens/`:
  `findings_milk.md`, `findings_peg.md`, `findings_carmine.md`.
- Phase 5: `analysis/allergens/narrative_draft.md` — three-paragraph
  journalism draft, one paragraph per allergen + one framing graf.

### Key numbers (DailyMed bulk, April 6 2026)
- MILK: 97/102 labeled-DPI products with known excipient data contain
  lactose (95.1%); 100% once Afrezza insulin and smelling-salt products
  are excluded. 34% of all oral products contain lactose (independent
  derivation matches Reker 2019's 44.8% on oral solids).
- PEG: 35.22% of 77,173 oral tablets/capsules/granules/pellets list a
  PEG-family excipient (matches Reker 2019's 36.03% figure within 1 pp).
- CARMINE: 176 of 199,961 products list carmine/cochineal/carminic acid
  (0.09%). 8 of 353 current generic azithromycin tablets carry it — the
  exact exposure path from Greenhawt 2009's landmark US anaphylaxis case.

### Decisions made
- Dataset scope: start from RAW 199,961-row catalog (not the 72,358 oral
  filter) because milk's harm anchor (DPIs) would be dropped by the oral
  filter. Filter by route + dosage_form inside the analysis step.
- Validation-table schema: same fields as gluten table (fda_term, source,
  flag_decision, rationale, source_url) plus one new column `match_type`
  with values `exact` or `regex`. Needed because the PEG family is too
  large to enumerate as exact strings (443 unique PEG-adjacent strings in
  the bulk catalog); regex substring matching is robust against future
  DailyMed additions.
- 3-tier flag scheme (contains / free / no_data) per allergen — simpler
  than the 4-tier gluten scheme. No `unknown` tier populated because (a)
  milk's "lactose unspecified form" is treated as contains_milk under the
  labeling-transparency frame; (b) PEG cross-reactivity means all
  PEG-family matches are contains_peg; (c) carmine synonyms are all
  definitive.
- Milk: all lactose raw-string variants → contains_milk. Rationale: for
  the labeling-transparency frame of the piece, lactose intolerance and
  milk-protein IgE are collapsed — the patient sees "lactose" in both
  cases. Over-calls oral lactose as a milk-protein-harm excipient, but
  matches the Figueiredo 2024 + Reker 2019 journalism methodology.
- Milk false-positive exclusions: 29 explicit entries (lactic acid, all
  *-lactate esters, LACTOBACILLUS / LACTOCOCCUS species, GALACTOSE,
  SHEA BUTTER, COCOA BUTTER, etc.) included in the validation table as
  `milk_free` rows. These aren't strictly needed given exact-string
  matching but document the false-positive surface for future reviewers.
- PEG regex patterns are specific to PEG family (POLYETHYLENE GLYCOL,
  not bare GLYCOL; POLYSORBATE, not bare SORBITAN). Propylene glycol
  (27,136 rows) is NOT flagged — chemically distinct, does not
  cross-react with PEG in the IgE sense.
- PEG bowel preps reported separately: 151 products list PEG 3350 as an
  active ingredient; all show 0 contains_peg at the excipient level
  because active ingredients aren't in excipients_raw. The Stone 2019
  anaphylaxis signal is in this active-ingredient context; the 35.22%
  oral-solids finding is the complementary "PEG as hidden inactive"
  story.
- Carmine `\bCARMINE\b` uses word-boundary regex to avoid false-matching
  CROSCARMELLOSE SODIUM (15,598 rows).

### Compass-artifact primer corrections surfaced in Phase 1
- MILK primer was largely clean. Only fixes: (a) EMA/CHMP/302620/2017
  current revision is **Rev. 5 (2025-12-05)**, primer cited Rev. 2 (stale
  3 revisions); (b) Spiriva HandiHaler's milk-protein language is a
  Section 5.2 "use with caution" warning, NOT a Section 4 contraindication
  as the primer implied.
- PEG primer had 9 of 20 UNIIs wrong or mapped to the wrong MW grade. Full
  corrections in `factcheck_log_peg.csv`. Our flagger uses regex on the
  excipient string, not UNIIs, so corrections do not affect counts but are
  preserved for downstream work.
- CARMINE primer had 2 of 4 UNIIs wrong: CARMINE=CID8SF5SDE (does not
  exist in GSRS — no standalone UNII for carmine) and
  CARMINIC ACID=6T5EM2IMAF (does not exist; correct UNII is CID8Z8N95N).
  Confirmed correct: COCHINEAL=TZ8Z31B35M.

### Assumptions flagged this session
- ⚠️ ASSUMPTION: Lactose (all forms) → contains_milk. Collapses lactose
  intolerance, IgE anaphylaxis risk from milk-protein contamination, and
  negligible clinical impact at therapeutic oral doses into one tier.
  Rationale: labeling-transparency frame. Limitation documented in
  findings_milk.md §5.
- ⚠️ ASSUMPTION: All PEG-family matches → contains_peg, including
  polysorbates. Rests on Stone 2019's skin-test cross-reactivity finding.
  A patient with pure PEG sensitivity and no polysorbate cross-reactivity
  would see this as an over-call. Limitation documented in findings_peg.md §5.
- ⚠️ ASSUMPTION: Absence of a post-2009 drug-carmine rulemaking confirmed
  by Federal Register + FDA.gov search. regulations.gov blocked
  programmatic access (HTTP 403) during the Phase 1 fact-check, so docket
  FDA-1998-P-0032 activity 2020–2026 was not fully enumerated. Manual
  docket spot-check recommended before publication.
- ⚠️ ASSUMPTION: The primer's claim that Stone 2019 caused FDA label
  updates to MiraLAX / GoLYTELY / NuLYTELY / CoLyte could not be verified.
  No Dear-Healthcare-Provider letter or MedWatch action attributable to
  the 2019 paper was located. Do NOT attribute to Stone 2019 in published
  copy without a primary source.

### Open questions for next session
- Spot-check docket FDA-1998-P-0032 on regulations.gov manually for any
  post-2009 drug-carmine filings.
- Verify whether any PEG 3350 bowel-prep Rx label (MiraLAX, GoLYTELY,
  NuLYTELY, CoLyte) revision can be traced to Stone 2019 via FDA's
  approval-letter or Orange Book change-log pages.
- Decide if the journalism piece wants a separate `propylene glycol /
  delayed-type hypersensitivity` allergen pass. Propylene glycol is
  27,136 rows in the bulk catalog; chemically distinct from PEG; can be
  added as a fourth allergen if useful.
- Author review of `narrative_draft.md`: three paragraphs versus one
  unified paragraph with three allergen examples.

### Where to pick up
Per-allergen workflow complete through narrative draft. Journalist review
of `analysis/allergens/narrative_draft.md` against the gluten findings
narrative is the immediate next step.

---

## Session 2026-04-22

### What was completed

**Phase A — Foundation**
- Rewrote `research_{milk,peg,carmine}.md` to contain only fact-check-
  verified claims with inline primary-source URLs. Deleted the three
  factcheck_log CSVs as redundant.
- Rebuilt all three validation tables under strict Task #21 rules:
  every row has `fda_term`, `match_type`, `flag_decision`, `source_url`,
  `iid_status`, `iid_unii`, `rationale`.
  - Milk table: 37 entries (down from 62 — removed 25 AI-reasoned
    `milk_free` exclusions that had no primary-source support for the
    "not milk-derived" claim).
  - PEG table: 4 regex patterns (tight scope — POLYETHYLENE GLYCOL,
    POLYETHYLENE OXIDE, MACROGOL, CARBOWAX).
  - Carmine table: 24 entries (21 exact + 3 regex, all GSRS synonyms
    and 21 CFR 73.100 permitted names).
- Ran empirical corpus tests: `corpus_test_{milk,peg,carmine}.csv`
  produced. Zero false positives on PEG; 1 review item on milk
  (MILK THISTLE — correctly excluded).

**Phase B — Allergen hardening**
- Applied six-step standard hardening to all three allergens (steps 1–5
  via primary-source lookups; step 6 pharmacist deferred as user-owned).
- Hidden-derivative sweeps surfaced no new real additions: CREAM (milk)
  was a topical-anesthetic-cream dosage-form artifact, not dairy;
  KOLLICOAT SR 30D (PEG) is out-of-scope per tight-scope decision;
  NATURAL RED 26 (carmine) is a different colorant.

**Phase C — Per-allergen follow-on artifacts**
- Created `scripts/spl_label_parser.py` with OTC Drug Facts support
  (added codes 42229-5 title-gated for allergy-alert, 50570-1 do-not-
  use, 50568-5/50569-3 ask-doctor, 50566-9 stop-use, 50567-7 when
  using, alongside the original Rx codes 34066-1/34070-3/34071-1/
  43685-7/34077-9).
- DPI contraindication analysis (`analyze_dpi_labels.py`): strict DPI
  filter yields 19 unique set_ids. 18 carry Section 4 milk-protein
  contraindication (Advair / Wixela family). 1 silent (Afrezza inhaled
  insulin — legitimately no milk carrier).
- Carmine contraindication analysis (`analyze_carmine_labels.py`): 156
  unique set_ids; 151 had parseable warning sections; 0 carry any
  carmine warning in any SPL section; 5 unparseable.
- PEG contraindication analysis (`analyze_peg_labels.py`): 16,760
  unique set_ids in oral-solids slice; 16,585 had parseable warning
  sections; 3 carry any PEG warning (2 boxed + 1 Section 5); 16,582
  silent; 175 unparseable.
- Carmine landscape analysis (`analyze_allergens.py` carmine section
  rewritten): no pre-filtering. Reports by route, dosage_form,
  approval_type, bulk_category, brand/generic, top active ingredients
  (drug-identity only), top manufacturers.

**Phase D — Cross-cutting documentation**
- Expanded `methodology.md` header; updated §3 PEG sections for tight
  scope; added §3.6 "Scope decisions — excluded adjacent families."
- Created `analysis/allergens/limitations.md` with per-allergen sections
  (Milk, PEG, Carmine) and a placeholder for gluten (absorbed by Task
  #17 reorg).
- Added gluten section to `literature.md` (§3.5).
- Rewrote `findings_{milk,peg,carmine}.md` and `narrative_draft.md`
  with tight-scope numbers, three-layer regulatory-gap framing, and
  objective (non-editorializing) language.

**Post-Phase-D quality audit + fixes (7 issues)**
- Spiriva HandiHaler mis-classification root-caused: DailyMed classifies
  it as CAPSULE / ORAL rather than POWDER, METERED / RESPIRATORY. Our
  DPI filter uses DailyMed's own fields; Spiriva falls outside. Logged
  as limitation, not patched in code.
- Narrowed DPI filter to exclude pMDIs (AEROSOL, METERED): DPI count
  126 → 19. Shared constant in new `scripts/allergen_filters.py` so
  both `analyze_dpi_labels.py` and `analyze_allergens.py` use the
  same definition.
- Rebuilt SPL parser with OTC Drug Facts section codes — eliminates
  the ~41 carmine + ~3,100 PEG "not found" OTC labels that had no Rx
  Section 4 / Section 5 structure.
- Expanded milk findings prevalence slices (full catalog, oral route,
  respiratory, DPI harm anchor).
- Reclassified lactulose from `milk_free` → `contains_milk` per FARE.
- Strict Task #21 do-over: removed AI-reasoned exclusions from milk
  table; integrated local `FDA-IID-recent-update.csv` via new
  `scripts/fda_iid_lookup.py` helper. Every row now has real
  `in_iid` / `not_in_iid` status instead of `unverified_pending_
  manual_check`.
- Audited `methodology.md` §2 / §4 for stale references; updated §3.4
  PEG table description from 21 patterns → 4 tight-scope patterns;
  removed dangling `factcheck_log_*.csv` references.

### Decisions made

- **PEG scope locked tight:** POLYETHYLENE GLYCOL / OXIDE / MACROGOL /
  CARBOWAX only. Adjacent families (polysorbates, poloxamers, polyoxyl
  derivatives, mPEG, PEG-N surfactants, TPGS, Kollicoat IR) excluded
  under the floor-scope rule and documented separately in
  `methodology.md` §3.6. Rationale: data-journalism defensibility —
  every flagged product carries an excipient name that is unambiguously
  PEG per the USP-NF PEG monograph. Reker 2019 Table 1 treats PEG
  (36.03%) and Poloxamer (0.76%) as separate categories; this analysis
  follows that convention.
- **Task #21 strict rule (2026-04-22):** every validation-table row
  must have a primary-source URL supporting the classification claim.
  AI reasoning alone is not sufficient. Rows that can only be defended
  by reasoning are either (a) backed by a primary source, (b) converted
  to `unknown`, or (c) removed (default flag behaviour handles the
  case anyway). Applied uniformly across all three allergen tables.
- **Lactulose → `contains_milk`:** FARE lists it as milk-derived;
  pharmaceutical lactulose is made by isomerizing milk-derived lactose.
  No primary source supports the alternative `milk_free` reasoning.
- **Milk false-positive exclusions dropped:** 25 previously-listed
  `milk_free` rows (lactic acid, lactate esters, lactobacillus species,
  plant butters, etc.) were removed. They had no primary-source claim
  "not milk-derived"; the flagger defaults to `milk_free` on no-match
  anyway, so the explicit rows were unnecessary and in violation of
  strict Task #21.
- **DPI harm-anchor filter excludes pMDIs** (AEROSOL, METERED). pMDIs
  are propellant-based and do not use lactose carriers — they are not
  part of the CMPA harm anchor.
- **FDA IID cross-reference via local CSV.** FDA's web interface
  returned 404 for programmatic access during this session. User
  downloaded `FDA-IID-recent-update.csv` (9,068 rows) locally;
  `scripts/fda_iid_lookup.py` loads it and provides `iid_status` /
  `iid_unii` lookups at validation-table-build time. Pharmacist
  spot-check remains deferred as a separate manual audit.
- **Active-ingredient PEG explicitly out of scope.** PEG 3350 bowel
  preps (MiraLAX family, 151 products) are PEG drugs, not products
  that happen to contain PEG as an inactive ingredient. The project
  rule is allergen matching on inactives only.

### Assumptions flagged this session

- ⚠️ ASSUMPTION: FARE's milk-derived ingredient list is authoritative
  enough to serve as the single primary source for milk classification.
  FARE is a patient-advocacy organization, not a federal regulator.
  If stricter primary-source standards are applied later (e.g. require
  a CFSAN regulatory list), the milk table would need re-sourcing.
- ⚠️ ASSUMPTION: Spiriva HandiHaler's Section 5.2 milk-protein warning
  language is real (per primer research), but our DPI filter does not
  capture Spiriva because DailyMed's dosage_form/route fields classify
  it as CAPSULE/ORAL. If Spiriva's real harm-anchor status matters to
  the story, it needs a product-name inclusion rule.
- ⚠️ ASSUMPTION: The FDA IID CSV the user downloaded is the current
  FDA-authoritative snapshot. If IID updates between this session and
  the next manual pharmacist review, some `iid_status` flags may
  become stale.
- ⚠️ ASSUMPTION: The LOINC section codes I included for warning
  analysis (42229-5 title-gated, 50570-1, 50569-3, 50568-5, 50567-7,
  50566-9, plus Rx codes) are the complete OTC Drug Facts warning
  surface. Other OTC-specific codes may exist; the parser extension
  was based on HL7 SPL Implementation Guide understanding, not an
  exhaustive LOINC-by-LOINC definition lookup.

### Key numbers (post-fixes)

- Milk: 33,481 `contains_milk` (16.74% of catalog; 35.29% of oral route).
  DPI harm-anchor slice (strict): 29 NDCs / 19 set_ids; 18 Section 4
  contraindication + 1 silent.
- PEG: 28,551 `contains_peg` (14.28% of catalog). Oral solids slice
  (ODT-excluded): 24,187 / 76,427 = 32.34%. Of 16,585 parseable oral-
  solids labels, 3 carry PEG warning (0.018%); 16,582 silent.
- Carmine: 176 `contains_carmine` (0.09% of catalog). Of 151 parseable
  labels across Rx + OTC, 0 carry carmine warning (100% silent).

### Open questions for next session

- **Phase E approval gate:** Tasks #16 (gitignore policy), #17 (full
  reorg), #18 (README rewrite) are pending explicit user approval.
  Discussed in plan file
  `~/.claude/plans/concurrent-riding-thimble.md`.
- Propylene glycol as a fourth allergen pass — open decision from
  2026-04-21, still unresolved.
- Pharmacist spot-check (user-owned, external).
- regulations.gov docket FDA-1998-P-0032 manual check for post-2009
  drug-carmine filings (user-owned; regulations.gov 403'd programmatic
  access).

### Where to pick up

Phases A–D complete with all seven post-audit fixes applied. Awaiting
explicit user approval before starting Phase E (gitignore policy → full
project reorg → README rewrite).

Today's work is saved in the working tree (git has not been committed
yet — the user may commit via GitHub Desktop or ask Claude to batch
the commit in a subsequent session). FDA IID CSV is tracked locally
at `FDA-IID-recent-update.csv`.

## Session 2026-04-23

### What was completed

**Phase E gate — Task #16 resolved (gitignore policy)**
- User chose option (a): gitignore all three large derived CSVs
  (`dailymed_allergens_flagged.csv` 174 MB, `dailymed_bulk_filtered.csv`
  60 MB, `dailymed_bulk_flagged.csv` 61 MB).
- Applied in `.gitignore` under current paths; `git rm --cached`
  executed for the two tracked files (files remain on disk).
- TASKS.md updated: Task #16 marked resolved; pharmacist spot-check
  folded into Task #18 (README manual-verifications section) per
  user direction; deferred-items pharmacist entry removed.

**Cross-workflow rigor audit — 4 issues surfaced**
- Audited Phase A–D artifacts for (a) stale numbers in published
  findings, (b) AI-judgment residue, (c) dead methodology sections,
  (d) cross-doc contradictions. Four issues flagged:
  1. `findings_peg.md` reports 3 PEG-allergy warnings; inspection
     of trigger snippets shows all 3 are ingredient-list mentions
     embedded in warning sections — not actual warnings.
  2. `corpus_test_{milk,peg,carmine}.csv` do not reflect final
     validation tables (milk test uses regex patterns the final
     exact-only table doesn't have; carmine test has 3 of 24 rules).
  3. `methodology.md` Parts 2–4 describe pre-Task-#21/#22 state in
     many places (63-row milk table with 29 unsourced exclusions,
     carmine 12 rows vs actual 24, removed azithromycin slice, old
     DPI filter, OLD 6-column validation schema).
  4. `analyze_allergens.py` duplicates `is_oral_solid` inline
     instead of importing from `allergen_filters.py`.
- Additional findings from parallel doc audit: `research_milk.md`
  still cites Figueiredo 2024 despite `literature.md` §7 excluding
  it; milk oral-count off-by-one (32,547 vs 32,548) across
  narrative/methodology; unsourced editorial language in narrative;
  stale row/route counts in `findings_carmine.md`.

**Tracking doc + permanent prevention mechanism**
- Created `analysis/allergens/reconciliation_pass.md` — 7 fix
  blocks listing source change + downstream artifacts per issue.
- Designed permanent prevention: `methodology.md` Part 6
  "Artifact dependency graph" keyed on scripts / validation tables
  and listing every downstream doc/section that cites their numbers.
  Consulted before merge on any future change.

**Reconciliation pass — 7 fixes executed in one batch**
- **Fix 4 (code cleanup):** `analyze_allergens.py` now imports
  `is_oral_solid` from `allergen_filters`; docstring rewritten.
  Re-ran; every number reproduces identically.
- **Fix 1 (warning patterns):** All three label analyzers
  (`analyze_{dpi,peg,carmine}_labels.py`) rewritten to require an
  allergy-context token (`allerg` / `hypersens` / `anaphyla` /
  `contraindicat`) within 80 chars of the allergen name. Bare-name
  patterns removed. Re-ran all three.
  - PEG: 3 false-positive warnings → **0**. 100% silent across
    16,585 parseable set_ids. Published-number bug corrected.
  - DPI milk: 18 contraindication / 1 silent — identical to prior
    (all 18 use "hypersensitivity to milk proteins"; change was
    methodological anchoring, not numerical).
  - Carmine: 0 / 151 silent / 5 not found — identical to prior.
- **Fix 2 (corpus tests):** New `scripts/build_corpus_tests.py`
  reuses `flag_allergens.load_validation()` and writes the
  corpus test files deterministically. Byte-stable on re-run
  (MD5-verified). Replaces the Phase-A discovery tests.
- **Fix 3 (methodology rewrite):** `methodology.md` §1.3 schema
  updated (7-column Task #21 strict schema); §2.2–§2.9 milk
  rewritten post-Task-#21; §3.2–§3.3 PEG rewritten post-tight-scope;
  §4.3–§4.7 carmine rewritten post-Task-#22. Added new Part 5
  "Warning-pattern vocabulary" (primary-source anchor documentation),
  new Part 6 "Artifact dependency graph", expanded Part 7
  "Provenance" to list every script including shared filters, SPL
  parser, IID lookup, and corpus-test generator.
- **Fix 5 (cross-doc sweep):** Removed Figueiredo 2024 from
  `research_milk.md` "Primary literature" (contradicted
  `literature.md` §7 exclusion). Resolved milk oral-count
  off-by-one — canonical 32,548 across all docs. Rewrote
  narrative three-layer framing to remove "inconsistent" and
  "overwhelming majority" editorial. Fixed `limitations.md`
  §Milk/Lactulose (was stale `milk_free` claim; now documents
  the 2026-04-22 FARE reclassification to `contains_milk`).
  Added warning-pattern anchor paragraphs to all three
  `limitations.md` allergen sections. Added NDC/set_id/row
  glossary to `findings_carmine.md`. Synced carmine landscape
  counts (route, approval_type, active ingredients) to match
  current analyzer output. Updated `literature.md` references
  to Task #8 (milk hardening is complete).
- **Fix 6 (cover-to-cover read):** executed; caught the
  findings_carmine stale route counts (142→150) and the
  literature.md task-#8 references.
- **Fix 7 (dependency graph):** added as Part 6 of methodology.md.

### Decisions made

- **Option (a) for Task #16 (gitignore all three large CSVs).**
  Symmetric with raw data (already gitignored); all three are
  deterministic outputs of scripts in the repo; one (174 MB) exceeds
  GitHub's 100 MB per-file hard limit so a push would be blocked
  anyway. Paths will be updated to `data/fullcatalog/` during the
  Task #17 reorg.

- **Warning-pattern vocabulary anchored to three primary sources.**
  `ALLERGY_CONTEXT = r"(?:allerg|hypersens|anaphyla|contraindicat)"`
  — derivation anchored to 21 CFR 201.22 (FDA sulfite warning mandate;
  the only FDA-mandated drug-allergy warning), AAAAI/ACAAI 2022 Drug
  Allergy Practice Parameter (PMID 36122788; peer-reviewed clinical
  vocabulary), and the Advair Diskus §4 contraindication template
  ("contraindicated in patients with severe hypersensitivity to milk
  proteins"). `contraindicat` was explicitly included because the
  Advair phrasing places `contraindicated` before `hypersensitivity`
  and a pure allergen-name-plus-allergy-fragment rule would miss
  labels whose warnings start with "contraindicated in…" without a
  nearby `hypersens` token.

- **80-character window for allergy-context anchor.** Spot-verified
  against the 18 DPI contraindication snippets (all within 60 chars
  of a milk-family name to a `hypersens` or `contraindicat` token).
  80 gives buffer without introducing cross-paragraph false matches
  in practice. LOINC-section scoping (`classify_warning_level`
  groups texts by section code, not across sections) further limits
  false matches.

- **Inactive corpus-test rules are kept, not deleted.** 32 of 119
  total rules across the three tables are currently inactive
  (no match in April 2026 DailyMed snapshot). Every inactive rule
  traces to a primary source (GSRS synonym, 21 CFR permitted name,
  FARE list entry, or USP monograph name). They're defensive and
  zero-cost. Deletion would require affirmative evidence of
  speculative origin — none found.

- **Single reconciliation pass executed as a batch, not stepwise.**
  Per user direction: "we will do it in one pass before E." Avoids
  partial-fix states where numbers in one doc have moved but the
  cross-cites haven't caught up.

### Assumptions flagged this session

- ⚠️ ASSUMPTION: The four tokens (`allerg`, `hypersens`, `anaphyla`,
  `contraindicat`) are sufficient primary-source-anchored vocabulary
  for detecting genuine drug-allergy warning language in SPL sections.
  Anchors are strong (21 CFR 201.22, AAAAI/ACAAI 2022, Advair §4),
  but if a label uses different phrasing (e.g. "adverse reactions
  have been reported including…" without an allergy token), it
  would not match. Consequence: possibly under-reported warnings if
  manufacturers write PEG/milk/carmine warnings using FDA-style
  adverse-reaction language without using one of the four token
  roots. Cross-checked against 18 Advair-family labels — all match;
  open question for non-DPI allergen families.

- ⚠️ ASSUMPTION: 80-character window between allergen name and
  allergy-context token is tight enough to prevent cross-paragraph
  false matches but loose enough to catch real warning phrasing.
  Verified against DPI contraindication snippets (all within 60
  chars). Not independently tested for broader dataset; relies on
  SPL section-code scoping preventing cross-section false matches.

- ⚠️ ASSUMPTION: Every "inactive" rule in the corpus tests is
  defensive (primary-source-derived, just not appearing in the
  April 2026 snapshot) rather than speculative. Verified by
  inspecting origin of each inactive rule — all trace to 21 CFR
  73.100, GSRS UNII synonym records, FARE milk list, or USP-NF PEG
  monograph. No speculative rules found.

### Key numbers (post-reconciliation)

- **Milk.** 33,481 `contains_milk` catalog-wide (16.74%); 32,548
  oral-route (35.29% excluding no_data); DPI harm anchor 25 of 29
  NDCs. Label analysis: 18 of 19 set_ids carry Section 4
  contraindication; 1 silent (Afrezza, no lactose carrier).
- **PEG.** 28,551 `contains_peg` catalog-wide (14.28%); 24,187 of
  76,427 oral solids (32.34% excluding no_data, ODT-excluded).
  Label analysis: **0 of 16,585 parseable set_ids carry PEG-allergy
  language**; 175 had no warning-relevant sections.
- **Carmine.** 176 `contains_carmine` catalog-wide (0.09%); 150
  ORAL (85.2%), 26 TOPICAL (14.8%). Label analysis: 0 of 151
  parseable set_ids carry carmine-allergy language; 5 not found.
- **Exposure-path anchor.** 8 of 353 azithromycin-containing
  products list carmine — all 8 generic (ANDA).

### Files modified this session

- Scripts: `analyze_allergens.py`, `analyze_peg_labels.py`,
  `analyze_dpi_labels.py`, `analyze_carmine_labels.py` (all
  modified). `scripts/build_corpus_tests.py` (new).
- Data: `data/bulk/{dpi,peg,carmine}_label_analysis.csv`
  (regenerated). `data/bulk/corpus_test_{milk,peg,carmine}.csv`
  (regenerated, byte-stable).
- Docs: `analysis/allergens/methodology.md` (substantial rewrite),
  `findings_peg.md`, `findings_milk.md`, `findings_carmine.md`,
  `limitations.md`, `narrative_draft.md`, `research_milk.md`,
  `literature.md`, `reconciliation_pass.md` (new).
- Config: `.gitignore` (3 new gitignore entries); `TASKS.md`
  (Task #16 resolved; Task #18 expanded with manual-verification
  section; deferred-items pharmacist line collapsed).

### Open questions for next session

- **Phase E Task #17 — full project reorg.** Approved in principle;
  not started this session. Large: folder renames
  (`analysis/allergens/` becomes the four-allergen root; `data/eda/`
  → `data/pilot/`; `data/bulk/` → `data/fullcatalog/`), file
  renames (many), script renames (many), hardcoded path updates
  across every script + `CLAUDE.md` + `.gitignore`, end-to-end
  re-run verification.
- **Phase E Task #18 — README rewrite.** Blocked by #17. Will
  include the manual-verifications section (pharmacist spot-check +
  FDA-1998-P-0032 docket spot-check) per user direction.
- **Propylene glycol fourth allergen pass.** User declined this
  session ("let that go. what we have now is fine."). Closed.

### Where to pick up

Phase A–D is internally consistent, primary-source anchored,
deterministically reproducible, and byte-stable across re-runs.
Ready to begin Phase E starting with Task #17 (full reorg) when
the user approves. Today's work is saved in the working tree; not
yet committed.

### Phase E executed in same session

After the above status was written, the user approved Phase E and
both Tasks #17 and #18 executed in the same 2026-04-23 session.

**Task #17 — full project reorganization.** Completed atomically.
- 10 scripts renamed (`pull_dailymed` → `pull_dailymed_pilot`;
  `extract_bulk` → `extract_fullcatalog_raw`; `build_excipient_list`
  → `build_gluten_excipient_list`; `build_validation_table` →
  `build_gluten_validation`; `filter_bulk` → `filter_gluten_fullcatalog`;
  `flag_bulk` → `flag_gluten_fullcatalog`; `analyze_bulk` →
  `analyze_gluten_fullcatalog`; `build_allergen_validation_tables` →
  `build_allergens_validation`; `flag_allergens` →
  `flag_allergens_fullcatalog`; `analyze_allergens` →
  `analyze_allergens_fullcatalog`).
- 19 data files moved (`data/eda/` → `data/pilot/`; `data/bulk/` →
  `data/fullcatalog/`; root-level raw CSVs into `fullcatalog/`).
  Old folders removed.
- 10 analysis files moved into `analysis/allergens/{gluten,milk,peg,
  carmine}/` subfolders.
- `analysis/limitations.md` (gluten-era) absorbed into
  `analysis/allergens/limitations.md` §Gluten as 13 numbered
  limitations matching the §PEG/§Milk/§Carmine format. Old file
  deleted.
- `analysis/allergens/carmine_dailymed_hits.csv` deleted (Phase-1
  keyword-search artifact; the 2 unique columns were no longer
  used by any analysis script).
- `analysis/bbc_pitch.md` did not exist — dropped from spec.
- ~80 path references updated across .gitignore, CLAUDE.md (full
  Output File Structure tree rewrite), README.md, TASKS.md.
- ~30 path references updated across 11 analysis docs.
- All 17 scripts compile and import cleanly post-rename.
- All 12 verifiable pipeline outputs byte-stable vs pre-reorg
  MD5 baseline (validation tables, corpus tests, label analyses,
  large flagged catalogs that were moved without regeneration).

**Task #18 — README rewrite.** Completed.
- README.md: 564 lines (gluten-pilot-only) → 530 lines (four-allergen).
- New structure: pitch + four-allergen background + repo tree +
  naming-conventions glossary + 5 reproduction pipelines + findings
  pointer table (15 rows) + warning-pattern vocabulary explainer +
  Role of AI + per-allergen limitations pointer + manual-verifications
  section (4 user-owned items: pharmacist spot-check, regulations.gov
  docket FDA-1998-P-0032, pilot validation borderline cases including
  cyclodextrin re-evaluation, animal-drug bulk-bucket coverage check)
  + citation + project genealogy.
- Verification: zero stale paths, every doc/script reference
  resolves, headline numbers match canonical CSV values
  (199,961 catalog rows; milk 33,481 / PEG 28,551 / carmine 176).
- Per Task #18 spec, full structural rewrite is now the README's
  job; CLAUDE.md remains the governing-instructions doc.

### Decisions made (Phase E)

- **Task #16 option (a):** gitignore all three large derived CSVs.
  Symmetric with already-gitignored raw; deterministic outputs of
  scripts; one (174 MB) exceeds GitHub's 100 MB per-file limit so
  any push would have been blocked anyway.
- **Reorg uses git mv where possible**, plain mv where the source
  was untracked (newer allergen scripts, allergen analysis docs).
  Scripts under git tracking preserved history via `git mv`.
- **Old empty folders removed** (data/eda/, data/bulk/) after all
  moves complete.
- **README full rewrite, not patch.** The gluten-pilot scaffolding
  could not be patch-edited into a four-allergen doc without
  structural confusion. Full rewrite is cleaner and matches the
  Phase E spec ("README structural rewrite is Task #18, deferred
  from #17").

### Assumptions flagged (Phase E)

- ⚠️ ASSUMPTION: All 17 scripts can be run from the project root
  with `python3 scripts/<name>.py`. Verified by `py_compile` +
  module-import smoke test, but the long-running scripts
  (`extract_fullcatalog_raw.py`, `analyze_peg_labels.py`,
  `flag_allergens_fullcatalog.py`) were not re-run end-to-end this
  session — they were import-checked only. Their inputs were not
  re-extracted (the 174 MB and 60-61 MB outputs were preserved
  via `mv`, not regenerated). Full pipeline re-run will confirm.

- ⚠️ ASSUMPTION: `analysis/allergens/carmine_dailymed_hits.csv`
  was safe to delete. The file contained two columns
  (`matched_excipient_strings`, `matched_categories`) not present
  in `allergens_fullcatalog_flagged.csv`. Both were Phase-1
  keyword-search artifacts no longer used by any analysis script.
  TASKS.md spec authorized deletion.

### Open questions for next session

- **Pharmacist spot-check** of milk / PEG / carmine validation
  tables. User-owned, pending.
- **`regulations.gov` docket FDA-1998-P-0032** manual spot-check
  for post-2009 drug-carmine filings. User-owned, programmatic
  access blocked.
- **Pilot validation borderline cases** — Q1-Q8 list at
  `analysis/allergens/gluten/validation_table_review_gluten.md`.
  Cyclodextrin classification specifically rests on a stale 2019
  source.
- **Animal-drug bulk-bucket coverage** — verify no human medications
  ended up misclassified into the animal-drug bulk download.
- **Git commit + push.** Working tree carries 2 sessions of changes
  (rigor pass + Phase E). Not yet committed. User may commit via
  GitHub Desktop or ask Claude to batch the commit.

### Where to pick up

Phase E complete. All four user-owned manual verifications surfaced
in `README.md` and `TASKS.md`. Next non-deferred work item: commit
the working tree (the user may handle this). Beyond that, the four
manual verifications are the only items blocking publication.

### Audit-remediation pass executed in same session

After Phase E, the user requested a brutally honest top-to-bottom
integrity audit. Three parallel `Explore` agents (code / data / docs)
produced findings; walked through each finding with the user one-by-one;
captured 18 tasks (#23-#40) under explicit user approval; then executed
all 18 in one pass. Memory rule added to project memory:
`feedback_process_before_outcome.md` — methodology parameters must be
set before running the analysis, not derived from results.

**Tasks executed (all marked resolved 2026-04-23 in TASKS.md):**

- **#34** — `fda_iid_lookup.py` file-existence guard with download URL
  on missing FDA IID CSV.
- **#26** — Moved `ALLERGY_CONTEXT` to shared `spl_label_parser.py`;
  removed duplicates from 3 analyzer scripts.
- **#27** — Moved `EXCIPIENT_DELIMITER = "; "` to shared
  `allergen_filters.py`; removed duplicates from 5 scripts. Audit
  confirmed 100% of `;` in DailyMed are followed by exactly one space
  (zero non-standard delimiters).
- **#35** — `re.compile()` in `flag_allergens_fullcatalog.load_validation`
  wrapped in try/except with row-context error message.
- **#36** — `.gitignore` cleanup: removed `findings_fullcatalog_gluten.md`
  from drafts block (now an active findings doc, tracked); added
  `*.partial` and `.setid_cache.json` for crash-recovery / cache files.
- **#39** — Deleted redundant
  `data/fullcatalog/dailymed_fullcatalog_raw.csv.zip` (33 MB); updated
  `.gitignore`, `CLAUDE.md`, `README.md` tree refs.
- **#40** — Added corpus-test scope disclosure ("verifies pattern
  matching, not classification correctness") to `methodology.md` §2.3 /
  §3.3 / §4.3.
- **#37** — Fixed `analyze_gluten_fullcatalog.py` `OUTPUT_MD` path bug
  (was writing to old `analysis/bulk_findings.md`); updated 5+ stale
  doc-content references to `analysis/limitations.md` and
  `analysis/findings.md` inside the script's markdown output.
- **#23** — PEG/dairy warning asymmetry. RECONSIDERED during execution:
  initially planned to add `\bPEG\b` as a row in `peg_validation.csv`,
  but that would broaden the flag classification past tight scope (the
  word-boundary regex matches 264 PEG-N derivative excipient strings
  — polysorbates, BIS-PEG, PEG-N stearates, etc. — that the
  tight-scope decision specifically excludes per methodology §3.6).
  Final approach: keep `\bPEG\b` and `\bdairy` in warning detector
  vocabulary; do NOT add to validation tables; document the
  asymmetry honestly in methodology.md §5.3 (warning-text vs
  excipient-string are different domains with different rigor
  requirements).
- **#24** — Methodology §2.3 framing: "FARE-listed ingredients plus
  DailyMed string variants of those entries to catch labelling
  inconsistencies." (Per user instruction, not framed as
  "AI-generated".)
- **#31** — Carmine landscape combo-product handling. 36 of 176
  carmine products are combos (20.5%). New format separates
  single-active count (140 products) from combo enumeration with
  per-active tally.
- **#32** — Manufacturer name normalization (case + punctuation +
  standard suffixes collapsed) in carmine landscape output.
- **#28** — **Allergens baseline filter** — flagger now drops
  homeopathic + unapproved + non-drug rows BEFORE allergen
  classification. Mirrors gluten filter steps 1, 2, 5 (excludes
  `bulk_category=homeopathic`, `approval_type` outside ANDA/NDA/BLA/
  OTC monograph variants, `document_type` outside the 4 human drug
  label types). 34,204 of 199,961 raw rows dropped → 165,757
  retained.
- **#29** — Per-allergen harm-anchored route slice added: parenteral
  (IV/IM/SC/IT/IA) for both milk (Hatcher 2025 anchor) and PEG
  (Stone 2019 anchor).
- **#30** — Gluten-comparable parity stat per allergen (count
  `contains_<allergen>` in the 69,137-row gluten-filtered set for
  like-for-like comparison).
- **#25** — `ALLERGY_CONTEXT` vocabulary expanded conservatively to
  add `intoler`, `adverse\s+react`, `cross[-\s]?react`. Re-ran all
  three label analyzers; same warning counts (18 DPI / 0 PEG /
  0 carmine) — the conservative expansion did not surface new
  warning hits, suggesting the original 4-token list already covers
  the actual label vocabulary in the catalog. The 80-character
  window kept as documented heuristic (no back-derivation per
  process-before-outcome rule).
- **#33** — Created new file
  `analysis/allergens/gluten/methodology_pilot.md` containing the
  pilot's full methodology in one place. Pilot kept distinct from
  full-catalog methodology; cross-references between the two
  removed.
- **#38** — Recovered original 349-line `analysis/limitations.md`
  from git history; expanded `analysis/allergens/limitations.md`
  §Gluten from 13 items to 24 items with the missing technical
  detail (cross-contamination, DailyMed index completeness,
  misspelling coverage, snapshot staleness, combo-product
  weighting, no-dose-level analysis, no_data denominator effect,
  approval_type misclassification risk, homeopathic-tagging
  false-negative risk, source-study classification non-equivalence,
  pointer to git history for further detail).

### Headline numbers post-baseline filter (user-visible)

- **Total catalog (post-baseline):** 165,757 (was 199,961; 17%
  pollution removed).
- **Milk:** 28,567 contains_milk (17.23%); 27,834 oral; 25 of 29
  DPI NDCs; 18 of 19 DPI set_ids carry §4 contraindication.
  Gluten-parity: 27,730 of 69,137 (40.11%).
- **PEG:** 27,956 contains_peg (16.87%); oral-solids 23,834 of
  64,123 (37.17%); parenteral 226 of 11,052; **0 of 16,293 parseable
  oral-solid set_ids carry a PEG-allergy warning**. Gluten-parity:
  24,556 of 69,137 (35.52%).
- **Carmine:** 161 contains_carmine (0.10%); 135 oral, 26 topical;
  **0 of 138 parseable set_ids carry carmine-allergy warning**.
  Gluten-parity: 130 of 69,137 (0.19%). Of 350 azithromycin
  products, 8 list carmine — all generic.

### Phase 8 closing audit results (clean)

- All 17 scripts compile + import cleanly.
- Zero stale `data/eda/` / `data/bulk/` / `dailymed_bulk_*` references.
- Zero stale script names (`extract_bulk`, `flag_bulk`, etc.).
- Stale doc-path references all addressed; the only `analysis/limitations.md`
  occurrences remaining are explicit historical-context mentions
  (e.g. "absorbed from the former...") — not broken references.
- All headline numbers reproduce from canonical CSVs.
- No orphan docs in `analysis/`.
- `.gitignore` honours expected entries; no new files need ignoring.

### Decisions made (audit-remediation)

- **Process-before-outcome rule formalized in memory.** Methodology
  parameters must be set BEFORE running the analysis, not derived
  from results and back-described as the process. The 80-character
  ALLERGY_CONTEXT window is the canonical example: I had proposed
  measuring snippet distances on already-matched warnings to
  back-derive a "verified" window, which would have been circular.
  User caught it ("ya but why find the verification number AFTER
  we verify?"). Memory file:
  `feedback_process_before_outcome.md`.
- **`\bPEG\b` and `\bdairy` warning broadenings KEPT.** Initially
  planned to bring warning detection into alignment with the
  validation tables; reconsidered when the data showed `\bPEG\b`
  matches 264 excluded PEG-N derivative strings. Final framing:
  warning detector and validation table are DIFFERENT TEXT DOMAINS
  (warning section text vs excipient strings) with different rigor
  requirements; the asymmetry is by design and documented.
- **Conservative vocabulary expansion.** User direction was "expand
  significantly," but candidate broad tokens (`warn`, `caution`,
  `adverse` alone, `react` alone) would have triggered thousands of
  generic-warning-vocabulary false positives. Conservative additions
  (`intoler`, `adverse\s+react` specifically, `cross[-\s]?react`)
  capture allergy-specific concepts without the noise. Re-runs
  confirmed no new warning hits surfaced — the original 4-token list
  was already capturing everything in the actual catalog vocabulary.
- **Pilot kept separate from full catalog (Task #33).** Per user
  direction: "no need to confuse or conflate them." New file
  `methodology_pilot.md`; methodology.md is full-catalog only.
  README data sections cover full catalog only (the scientific paper
  background and harm anchors stay in README).

### Assumptions flagged this audit-remediation pass

- ⚠️ ASSUMPTION: The conservative `intoler` / `adverse\s+react` /
  `cross[-\s]?react` vocabulary expansion is sufficient for the
  catalog's actual warning vocabulary. Verified by re-running all 3
  analyzers and observing zero new warning hits, but a more
  aggressive expansion (with proper false-positive review) could
  surface things this conservative pass missed. The user-authorized
  AI false-positive review was not exercised because no new hits
  surfaced.
- ⚠️ ASSUMPTION: The baseline filter's allowlist of approval types
  (ANDA / NDA / NDA AUTHORIZED GENERIC / BLA / OTC MONOGRAPH DRUG /
  OTC MONOGRAPH FINAL / OTC MONOGRAPH NOT FINAL) covers all
  legitimate FDA-recognized human medications. Any approval type
  NOT in this allowlist is dropped (e.g. `unapproved drug for use
  in drug shortage` — 8 products — was dropped; in principle these
  could be real drugs in temporary shortage status). Documented in
  limitations.md.
- ⚠️ ASSUMPTION: The parenteral route harm-anchor (Hatcher 2025
  trace casein in IV methylprednisolone; Stone 2019 PEG anaphylaxis
  in PEGylated drugs) generalizes to the 11,052 parenteral-route
  products in the post-baseline catalog. The numbers reported (129
  parenteral-milk; 226 parenteral-PEG) are based on excipient
  labelling, not on whether each product is a documented harm
  pathway.

### Open questions for next session

- **Pharmacist spot-check** (user-owned, manual). Unchanged.
- **`regulations.gov` docket FDA-1998-P-0032** (user-owned, manual,
  blocked by HTTP 403). Unchanged.
- **Pilot validation borderline cases** (cyclodextrin, ASO, SSG).
  Unchanged.
- **Animal-drug bulk-bucket coverage** (user-owned, manual).
  Unchanged.
- **Git commit + push.** Working tree now carries this entire
  session's work (Phase E reorg + rigor pass + audit remediation).
  Not yet committed.

### Where to pick up

Audit-remediation pass complete. All 18 tasks resolved. Phase 8
audit returns clean. Repo is in coherent state for a single git
commit covering today's work. The four manual verifications
(pharmacist, regulations.gov docket, pilot borderline cases,
animal-drug coverage) remain user-owned and external; nothing else
blocks publication.

## Session 2026-05-05

### What was completed
- Pharmacist spot-check feedback received on the milk validation
  table. Lactose family (9 string variants) and LACTULOSE removed
  from `MILK_CONTAINS_EXACT` in `scripts/build_allergens_validation.py`.
- Regenerated `data/fullcatalog/milk_validation.csv` (37 → 27 entries).
- Reran `flag_allergens_fullcatalog.py`, `build_corpus_tests.py`,
  `analyze_dpi_labels.py`, and `analyze_allergens_fullcatalog.py`.
  No script changes; same workflow with the tighter list.
- Updated milk numbers in `findings_milk.md`,
  `analysis/allergens/narrative_draft.md`, and `README.md` (milk
  row of the per-allergen prevalence table).
- Added a sentence to `analysis/allergens/methodology.md` Part 2
  documenting the pharmacist-driven exclusion + verbatim reason.

### Decisions made
- Excluded entries deleted from the script's `MILK_CONTAINS_EXACT`
  list (Option B, per plan) rather than reclassified in-table —
  cleaner table; audit trail lives in methodology.md Part 2 + this
  session log + the `git log` of the script edit.
- Editing the source script (`build_allergens_validation.py`) and
  regenerating the CSV is preferred over editing the CSV directly,
  to keep the script as the single source of truth and avoid clobber
  on future regeneration.
- Pharmacist's verbatim rationale: lactose and lactulose are milk
  sugars but are not themselves allergens. In purified pharmaceutical
  form they do not inherently contain allergenic milk proteins.
  Lactose intolerance is distinct from milk allergy. Theoretical
  contamination with milk proteins is overall very unlikely. The
  remaining entries (casein and below) are either milk proteins or
  milk itself.

### Headline shifts (full catalog post-baseline, N=165,757)
- contains_milk: 28,567 (17.23%) → 115 (0.07%)
- Oral route: 27,834 (36.90%) → 36 (0.05%)
- DPI strict slice: 25 of 29 (86.21%) → 0 of 29 (0%)
- Parenteral route: 129 (1.39% excl no_data) → 0 (0%)
- Gluten-parity slice: 27,730 of 69,137 (40.11%) → 36 of 69,137 (0.05%)
- DPI label-warning analysis is unchanged (18/19 set_ids carry §4
  contraindication; analysis is XML-driven, not flag-driven).

### Assumptions flagged this session
- None new this session. Prior `⚠️ ASSUMPTION` blocks about
  parenteral harm anchor numbers no longer apply at the previous
  scale (the parenteral milk count went to 0 under the revised
  table).

### Open questions for next session
- DPI harm-anchor framing in `findings_milk.md` and
  `narrative_draft.md`: with 0 of 29 DPIs flagged contains_milk
  under the revised table, the prior framing (lactose carrier as
  harm anchor) collapses. The 18/19 §4 contraindication-language
  finding from `dpi_label_analysis.csv` is still valid and is
  XML-driven, but the prevalence-based "86%" anchor is gone. Awaiting
  user direction on whether to (a) reframe around the 18/19 label
  warnings without a prevalence anchor, (b) re-anchor on a different
  slice, or (c) change scope. Not actioned this session per user
  instruction to "do the analysis till the end and then lets talk
  about it."

### Where to pick up
Discuss the DPI harm-anchor framing and the broader narrative
implications of the revised milk numbers with the user before any
further restructure of `findings_milk.md` or `narrative_draft.md`.

---

## Session 2026-05-08

### What was completed
- Article writing-phase support: drafted the data-analysis paragraphs
  to fill the `TK TK TK` placeholder in the BBC Health article,
  framed around the combined `contains_gluten + unknown + no_data`
  rate. Output delivered in chat (no article file written).
- Added `scripts/analyze_gluten_cannot_confirm.py`: reads
  `data/fullcatalog/gluten_fullcatalog_flagged.csv`, computes the
  combined "cannot confirm gluten-free from the label alone" rate
  by document_type (OTC vs Rx), brand_generic (brand vs generic vs
  OTC monograph), and top 25 active ingredients. Deterministic, no
  AI inference, sanity-checks against `findings_fullcatalog_gluten.md`.
- Added `scripts/analyze_bupropion_gluten.py`: slices the family
  (active_ingredients contains `BUPROPION`) into bupropion-only
  (Wellbutrin / Aplenzin / Zyban / Forfivo / generics, n=506) and
  bupropion-containing combos (Contrave, Auvelity, n=5).
- Verified the SSG Type A claim from `findings_fullcatalog_gluten.md`
  in chat: 13,334 product appearances catalog-wide; 12,328
  source-specified (92.46%); 1,006 source-unspecified (7.54%).
  1,006 of 1,028 unknown-tier products (97.86%) are driven by
  source-unspecified SSG Type A; the remaining 22 trace to other
  source-ambiguous starches.
- Identified a verifiable same-brand same-product mixed-disclosure
  case for the article: Kenvue Brands LLC sells two regular-strength
  Tylenol tablets (NDC 50580-495 and NDC 50580-496) with identical
  active ingredient (acetaminophen 325 mg), identical dosage form
  (uncoated tablet), identical pill appearance and identical other
  inactive ingredients (magnesium stearate + powdered cellulose).
  Their SSG Type A entries differ: 50580-496 specifies POTATO; 50580-495
  does not. Confirmed both are currently active on DailyMed via
  WebFetch (50580-495 = SPL version 7; 50580-496 = SPL version 12;
  both effective 2024-11-07).
- Drafted journalism paragraphs for the article: SSG Type A "single
  ingredient drives almost all uncertainty" block; Tylenol same-brand
  inconsistency block; combined other-allergens (carmine + PEG +
  milk) two-paragraph block with explicit floor-only methodology
  caveat.

### Decisions made
- Combined-rate definition for the article cannot-confirm headline:
  `contains_gluten + unknown + no_data`. Bundles label-based
  unknowability into one figure for readers. 4,081 of 72,358 = 5.64%.
- Cross-allergen parity figures cited in the article use the
  post-pharmacist-review milk number (lactose excluded, 36 of 69,137).
  Lactose-included framing was considered and dropped per user
  decision in this session.
- Carmine count cited is 130 (gluten-parity filter), matching the
  denominator the rest of the article uses. Earlier "161 oral" /
  "176" figures were mixed-denominator and removed.
- Floor-only caveat added to the other-allergens block: matches
  capture only excipients named specifically on the label, not those
  hidden under generic descriptors such as "color added." Carmine
  in particular can still appear under generic color descriptors on
  US drug labels because the 2009 FDA naming rule (74 FR 207) was
  never extended to drugs (21 CFR 73.1100 vs 73.100).
- "Not federally required" warning claim is supported: only sulfites
  (21 CFR 201.22) and FD&C Yellow No. 5 (21 CFR 201.20) carry an
  FDA-mandated drug-label allergy warning. FALCPA excludes drugs.
  The Advair Diskus milk contraindication is a manufacturer-added
  safety statement, not a class-wide FDA mandate.
- Bupropion analysis cohort split: bupropion-only vs combo separated
  by `;` in active_ingredients. Combos (Contrave, Auvelity) are
  reported separately because they are different drugs with
  different indications, not different brands of the same drug.
- Tylenol two-NDC contrast accepted as the article example after
  WebFetch confirmed both filings are current. Children's chewables
  were NOT among the unspecified-SSG Tylenol products in the data;
  user's hypothetical was corrected before publication.

### Assumptions flagged this session
- None new.

### Open questions for next session
- None.

### Where to pick up
Article is in writing phase. Drafted data-analysis prose blocks
delivered in chat: (1) combined cannot-confirm headline + OTC vs Rx
+ brand vs generic + drug-class concentration + cross-allergen
footer; (2) SSG Type A "drives almost all uncertainty" + source
specified vs unspecified; (3) Tylenol same-brand same-product
mixed-disclosure example (NDC 50580-495 vs 50580-496); (4)
two-paragraph other-allergens block (carmine + PEG + milk) with
floor-only methodology caveat. Next session: continue article
writing or run additional cuts as the user requests.
