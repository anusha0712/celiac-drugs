# Allergen Workflow Limitations

Consolidated per-allergen limitations for the gluten, milk, PEG, and
carmine analyses. Objective statements only — no editorializing. Gluten
content absorbed from the former `analysis/limitations.md` on 2026-04-23
as part of the Task #17 reorganization.

---

## PEG

1. **Label-based only.** Every flag is derived from the DailyMed
   `excipients_raw` field. Actual PEG content, molecular weight, and
   grade are not independently measured or audited against manufacturer
   certificates of analysis.

2. **Tight-scope floor estimate.** `contains_peg` is restricted to
   POLYETHYLENE GLYCOL, POLYETHYLENE OXIDE, MACROGOL, and CARBOWAX
   (scope decision 2026-04-22). Adjacent families are intentionally
   excluded and may represent real PEG exposure for cross-reactive
   patients. Excluded families documented in
   `allergens/methodology.md` §3.6:
   - Polysorbates (Tween 20–85)
   - Poloxamers (Pluronic F-68, F-127, etc.)
   - Polyoxyl derivatives (Cremophor EL / RH 40; polyoxyl stearates)
   - mPEG / methoxy-PEG
   - PEG-N surfactants (PEG-40 stearate etc. — same compound as
     polyoxyl stearates)
   - Vitamin E TPGS
   - Kollicoat IR (polyvinyl alcohol-PEG graft copolymer)
   - Propylene glycol (chemically distinct — non-polymer)
   A patient who is cross-reactive to polysorbates or poloxamers will
   encounter PEG-family excipients beyond what the tight-scope flag
   captures.

3. **Active-ingredient PEG out of scope.** 151 catalog products list
   PEG 3350 as an active ingredient (MiraLAX, GoLYTELY, NuLYTELY,
   CoLyte, MoviPrep, Plenvu, GaviLyte family). The project scope is
   inactive-ingredient labeling transparency. Active PEG is a different
   story (drug identity, dose-response to an approved active) and is
   not in this analysis.

4. **No `unknown` tier.** POLYETHYLENE GLYCOL and its MW grades are
   unambiguously PEG per the USP-NF monograph. No ambiguous
   source-specification cases have surfaced that would merit an
   `unknown` tier for PEG (unlike milk, where animal-source ambiguity
   can apply).

5. **FDA IID verification via locally downloaded CSV.** The FDA
   `FDA-IID-recent-update.csv` (9,068 rows) is loaded at build time by
   `scripts/fda_iid_lookup.py`. Each PEG validation-table row now
   carries `iid_status = in_iid` or `not_in_iid` with the IID-listed
   UNII where applicable. Pharmacist spot-check remains a separate
   pending manual review.

6. **Pharmacist spot-check not performed.** Flagged as final, manual,
   user-owned; pending.

7. **Unit of analysis is NDC-level.** Matches the gluten and other
   allergen conventions. Distinct NDCs under the same SPL label can
   have different excipient profiles.

8. **Primary-source anchoring is source-level, not per-row FDA IID.**
   Keyword list is anchored to the USP-NF PEG monograph and AAAAI/ACAAI
   2022 practice parameter for the family. Per-ingredient prevalence
   confirmation against FDA IID is the pending manual audit item
   referenced in (5) above.

9. **Warning-pattern vocabulary is editorial selection.**
   `analyze_peg_labels.py` requires an allergy-context token
   (`allerg` / `hypersens` / `anaphyla` / `contraindicat`) within 80
   characters of a PEG-family name. The 4 token roots are an
   editorial selection informed by 21 CFR 201.22, AAAAI/ACAAI 2022,
   and the Advair Diskus §4 template — not prescribed verbatim by
   any single primary source. Labels using vocabulary outside these
   tokens (e.g. "intolerance", "sensitivity", "adverse reaction")
   would not be detected. Vocabulary expansion is tracked as Task
   #25. Methodology §5 has the full disclosure.

10. **80-character window is a heuristic.** No empirical validation
    of the optimal window. Per the project's "process before outcome"
    rule, we do not back-derive the window from already-matched
    warnings. Validation comes from the AI false-positive sweep
    (Task #25), not from window-distance measurement.

11. **Warning detector matches `\bPEG\b` in label text but
    `peg_validation.csv` does NOT include `\bPEG\b`.** By design.
    Bare `\bPEG\b` matches 264 PEG-N derivative excipient strings
    (polysorbates, polyoxyl, BIS-PEG, mPEG, TPGS) that the
    tight-scope decision (methodology §3.5 / §3.6) excludes. Adding
    it to the validation table would re-broaden flag classification.
    Warning detection runs against label text where "PEG-allergic"
    is real vocabulary; flag classification runs against excipient
    strings where tight scope must hold. Different domains.

---

## Milk

1. **Label-based only.** Every flag is derived from the DailyMed
   `excipients_raw` field.

2. **Keyword list anchored to FARE.** Primary-source list is the FARE
   (Food Allergy Research & Education) milk-allergen ingredient list.
   Not every string on the list appears in DailyMed. The 37-entry
   validation table (post-Task-#21, 2026-04-22) enumerates every
   DailyMed raw-string variant of a FARE-listed ingredient. An earlier
   version also included explicit `milk_free` false-positive exclusion
   rows (lactic acid esters, lactobacillus species, milk thistle, shea
   / cocoa butter, etc.); Task #21 removed those rows because the
   flagger defaults to `milk_free` on no match and the exclusions had
   no primary-source citation. Historical snapshot in git.

3. **DPI harm anchor is narrow.** Dry powder inhalers for
   asthma/COPD are the harm-anchor subcategory (Nowak-Wegrzyn 2004,
   Robles 2014, Bar-On 2022).

4. **Lactulose classification.** FARE lists lactulose as a
   milk-derived ingredient; pharmaceutical lactulose is synthesized
   by isomerizing lactose. Flagged `contains_milk` per FARE.
   Reclassified from `milk_free` 2026-04-22 as part of the Task #21
   primary-source-anchoring pass. Source:
   https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens/milk

5. **FDA IID verification via locally downloaded CSV.** Same mechanism
   as PEG. Each milk validation-table row carries
   `iid_status = in_iid` or `not_in_iid`.

6. **Spiriva HandiHaler is misclassified in DailyMed.** Spiriva
   HandiHaler is a powder-in-capsule dry powder inhaler, but DailyMed
   classifies it as `CAPSULE / ORAL` rather than
   `POWDER, METERED / RESPIRATORY`. The DPI harm-anchor filter uses
   DailyMed's own dosage-form and route fields and therefore does not
   capture Spiriva. Spiriva's Section 5.2 does carry a milk-protein
   warning ("use with caution...") but the product is not counted in
   the DPI slice reported in `findings_milk.md` Layer 2.

7. **Pharmacist spot-check not performed.** Manual, user-owned, pending.

8. **Unit of analysis is NDC-level.**

9. **Warning-pattern vocabulary is editorial selection.**
   `analyze_dpi_labels.py` requires an allergy-context token
   (`allerg` / `hypersens` / `anaphyla` / `contraindicat`) within 80
   characters of a milk-family name. The 4 token roots are an
   editorial selection informed by 21 CFR 201.22, AAAAI/ACAAI 2022,
   and the Advair Diskus §4 template — not prescribed verbatim by
   any single primary source. Methodology §5 has the full disclosure.

10. **80-character window is a heuristic.** Same caveat as PEG; see
    `methodology.md` §5.2.

11. **Warning detector matches `\bdairy` in label text but
    `milk_validation.csv` does NOT include `\bdairy`.** By design.
    FARE doesn't list "dairy" as an ingredient (it's a category
    word). But labels use "dairy allergy" as warning vocabulary.
    Warning detection includes it; flag classification stays
    FARE-anchored. Different text domains.

---

## Carmine

1. **Label-based only.**

2. **Small universe.** 176 products catalog-wide flag
   `contains_carmine`. This small denominator makes fine-grained slicing
   sensitive to single-product changes and limits the statistical claims
   that can be made.

3. **Greenhawt 2009 is the only US-drug harm anchor.**
   Medication-specific carmine anaphylaxis in the peer-reviewed US
   literature is a single 2009 case (azithromycin tablet with pink
   carmine film coating). Other carmine anaphylaxis literature is
   food-additive (Weisbrod 2023, Slurpee) or non-US (Takeo 2018
   Japanese cases; Khalil 2025 Qatar / US co-authored; Sadowska 2022
   Poland).

4. **Regulatory gap verification incomplete.** The claim that no
   separate drug-carmine rulemaking has followed the 2009 food rule
   (74 FR 207) rests on Federal Register and FDA.gov search. The
   regulations.gov docket FDA-1998-P-0032 returned HTTP 403 to
   programmatic access during Phase 1 fact-check; 2020–2026 filings
   were not fully enumerated. Manual docket spot-check is a pending
   item (user-owned).

5. **FDA IID verification via locally downloaded CSV.** Same mechanism
   as PEG and milk. Each carmine validation-table row now carries
   `iid_status = in_iid` or `not_in_iid`. Only 2 of 24 carmine rows
   (CARMINE and COCHINEAL) appear in FDA IID as exact names; the rest
   are GSRS-confirmed synonyms (Natural Red 4, CI 75470, E 120, etc.)
   that IID does not enumerate separately. The primary-source URL
   (21 CFR 73.100 or GSRS synonym record) remains the authoritative
   classification anchor for those rows.

6. **Pharmacist spot-check not performed.** Manual, user-owned, pending.

7. **Unit of analysis is NDC-level.**

8. **Warning-pattern vocabulary is editorial selection.**
   `analyze_carmine_labels.py` requires an allergy-context token
   (`allerg` / `hypersens` / `anaphyla` / `contraindicat`) within 80
   characters of a carmine-family name. The 4 token roots are an
   editorial selection informed by 21 CFR 201.22, AAAAI/ACAAI 2022,
   and the Advair Diskus §4 template — not prescribed verbatim by
   any single primary source. Methodology §5 has the full disclosure.

9. **80-character window is a heuristic.** Same caveat as PEG; see
   `methodology.md` §5.2.

---

## Gluten

1. **Label-based only.** Every flag is derived from the DailyMed
   `excipients_raw` field. No ELISA or HPLC measurement of actual gluten
   content. Cross-contamination during manufacturing is not detectable
   from labels.

2. **Four-tier flag system.** `gluten_free / unknown / contains_gluten /
   no_data`. The `unknown` tier captures source-ambiguous excipients
   (e.g. SODIUM STARCH GLYCOLATE TYPE A — gluten status depends on
   starch source, which the label does not specify). The single largest
   `unknown`-driver is SSG Type A: 92.8% of `unknown` products in the
   pilot stem from this one excipient.

3. **Pharmaceutical SSG is predominantly potato- or corn-derived.** The
   154 `unknown` SSG products in the pilot most likely contain zero
   gluten in practice. The flag reflects labeling ambiguity, not
   probable gluten presence. A celiac patient reading the label still
   has no way to know.

4. **FDA CPG 578.100 manufacturer-facing rule.** Unqualified "starch"
   on a US drug label is legally defined as corn starch under FDA's
   Compliance Policy Guide 578.100. The rule is directed at
   manufacturers; patients reading bottles have no way to know it.

5. **Xanthan gum reclassified to `gluten_free`** (2026-03-27,
   departure from the Portuguese source study which flags it
   precautionarily). Source: National Celiac Association.
   https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/
   Reclassification reduced overall pilot `unknown` from 13.5% to 2.5%.
   If the Portuguese precautionary classification is applied instead,
   pilot acetaminophen would be ~16% non-gluten-free (vs. Portugal's
   44.4%) and ibuprofen ~18% (vs. Portugal's 8.2%). The gap with
   Portugal narrows but remains large.

6. **Pilot vs full-catalog non-comparable.** The pilot dataset (Phases
   1-3, acetaminophen + ibuprofen, 6,605 products) excluded only
   injectables and kept everything else. The full catalog runs through
   the 6-step `filter_gluten_fullcatalog.py` pipeline that drops
   non-oral routes, mouth-only delivery forms, and non-FDA-recognized
   approval types. Percentages from the two datasets are not directly
   comparable.

7. **Grandfathered medications excluded from full catalog.** The
   `unapproved drug other` bucket (1,445 rows) is dropped by Step 5
   of `filter_gluten_fullcatalog.py`. This bucket contains real
   medications in continuous US use for decades but never formally
   FDA-approved (Phenobarbital ~191 rows, Phenazopyridine ~110,
   Hyoscyamine ~35, Armour Thyroid family ~70, Salsalate ~19, Donnatal
   ~12, others). Trade-off accepted in exchange for a clean
   "FDA-recognized" cut. Documented limitation; celiac patients on
   these drugs are not represented in the full-catalog analysis.

8. **OTC monograph drugs included without individual NDA review.**
   ~11,000 OTC monograph products (acetaminophen, ibuprofen, antacids,
   cough/cold combos, etc.) are kept in the full-catalog cut. The FDA
   does not individually approve each manufacturer's OTC monograph
   product. Excipient selection is not vetted by FDA review.

9. **DailyMed source-data inconsistencies.** Some products have
   `route = ORAL` but dosage forms clearly for other routes
   (INJECTION, AEROSOL, CREAM, etc.). The 6-step filter pipeline
   catches the major buckets (Step 4 drops mismatched dosage forms;
   Step 6 catches mouthwash-by-name slips). Other inconsistencies
   likely exist that the pipeline does not detect.

10. **KIT products list no excipients at the KIT level.** 1,292 KIT
    products survive the filter; their excipients live on the
    individual component labels inside the kit, which the extractor
    does not unpack. Result: KIT products show `gluten_flag = no_data`.

11. **NDC-level unit of analysis.** Same convention as the other three
    allergens. A single SPL label can contain multiple NDC entries
    with different excipient profiles.

12. **Source study comparison is methodological reference, not
    statistical replication.** The Portuguese study (Figueiredo et al.
    2025) sampled 308 products across 3 categories from INFOMED
    (Portugal). Our acetaminophen sample is 21× larger (4,986 vs
    108) and our ibuprofen sample 19× larger (1,619 vs 85). The
    Portuguese 8.2% ibuprofen figure has an approximate 95% CI of
    3.2-17.0% due to small sample size.

13. **Pharmacist spot-check not performed.** Manual, user-owned,
    pending. Same as the other three allergens.

14. **Cross-contamination during manufacturing is undetectable.** A
    product flagged `gluten_free` may still contain trace gluten if
    the manufacturing line is shared with gluten-containing products.
    Label-based analysis cannot detect this.

15. **DailyMed index completeness not verified against FDA NDC
    Directory.** Products missing from DailyMed's search index would
    be absent from the dataset. DailyMed is FDA-recommended for
    patients but no independent cross-reference was performed.

16. **Misspelling coverage is best-effort.** Pilot caught 2
    `acetominophen` misspellings via manual sweep; other less-common
    misspellings may exist and would be missed.

17. **DailyMed index staleness.** The bulk download is a snapshot
    (April 6, 2026). Newer products added after that date are not
    in the dataset. Formulations also change.

18. **Combination products counted with same weight as single-active
    products.** A combo product (e.g. acetaminophen + caffeine) gets
    one row even though it contains two pharmacologically relevant
    actives. Reflects real-shelf exposure but inflates per-active
    counts when broken out.

19. **No dose-level analysis.** Excipient quantity per dose is not
    measured. A product can list "starch" once and contain 1 mg or
    100 mg — the flag is the same.

20. **`no_data` denominator effect on percentages.** Excluding
    no_data products from the denominator raises all flag
    percentages; including them lowers them. Findings reports both
    framings explicitly.

21. **Possible `approval_type` misclassification.** The
    `approval_type` field comes from the manufacturer's SPL
    submission, not independent FDA verification. Spot-checks during
    pipeline development suggest reliability for the major buckets
    but rare manufacturer-side errors cannot be ruled out.

22. **Filter false-negative risk for mistagged homeopathic
    products.** Step 2 of the gluten filter drops `bulk_category =
    homeopathic` and Step 5 drops `approval_type = unapproved
    homeopathic`. Products from manufacturers selling both
    homeopathic and conventional drugs (e.g. Schwabe North America)
    may classify edge cases inconsistently. Spot-checks during
    pipeline development found no obvious slips, but the
    cross-product-line case is not exhaustively audited.

23. **Source study (Figueiredo 2025) classification non-equivalent
    to ours.** The Portuguese study used a 2-tier classification
    (gluten / non-gluten-free); we use 4 tiers (gluten_free /
    unknown / contains_gluten / no_data). Direct percentage
    comparisons should be presented with caveats. Their 8.2%
    ibuprofen figure has approx 95% CI of 3.2-17.0% due to small
    sample size (n=85).

24. **Pre-Task-#17 detail recoverable from git history.** This
    §Gluten section is a distillation of a 349-line `analysis/limitations.md`
    file that was absorbed during the Phase E reorg (2026-04-23).
    The full original is in git history at the deletion commit. If
    detail beyond this 24-item summary is needed (e.g. the full
    flagging-methodology breakdown, decision-rules-for-edge-cases
    enumeration), recover via `git show <commit>:analysis/limitations.md`
    and consult the original Parts 1-4.
