# Pending Tasks

Persistent task list. The Claude Code in-session task harness is ephemeral —
this file is the source of truth across sessions. Update both in sync.

Task numbers are chronological. New audit-remediation tasks (Task #23+)
are appended sequentially; resolved Phase A–E tasks are kept as one-line
records under "Completed tasks" at the bottom for audit trail.

---

# Audit remediation pass (2026-04-23)

Tasks captured from the integrity audit walk-through. Each task is added
only after explicit user approval of the fix.

## Workflow integrity rule (binding on every task in this section)

**User direction (2026-04-23):** every fix in this audit-remediation
block must propagate end-to-end through the workflow. Changing the
code, validation table, or methodology in isolation is insufficient.
For each pending task:

1. **If the change affects numbers** (validation tables, flagger
   logic, warning patterns, filters): re-run every downstream script
   that consumes the changed input, regenerate every CSV, then update
   every findings / methodology / limitations / narrative / README
   passage that cites those numbers. The
   `methodology.md` Part 6 artifact-dependency graph names the
   downstream docs per script; consult it.
2. **If the change affects methodology framing or scope**: update
   every doc that describes that methodology — methodology.md
   per-allergen sections, limitations.md per-allergen sections,
   findings.md headers, narrative_draft.md framing, README.md
   "Where to read findings" pointers and harm-anchor descriptions.
3. **If new analysis is needed** (e.g. new slices, new vocabulary,
   new filter): the corresponding script must be amended and re-run.
   Don't add a new finding to a doc without the underlying
   reproducible analysis.
4. **Verification before task close**: the task is not done when the
   code change lands. It is done when (a) the code change lands,
   (b) all downstream artifacts are updated to match, (c) all
   re-runs reproduce the new numbers cleanly, (d) a grep across
   the repo confirms no stale reference to the previous state
   survives.

This rule is binding on Tasks #23 through #40 and any future audit
fixes. If a task as written omits this propagation step, the
omission is implicit; the task is not complete until propagation
is done.

## Task #23 — C1 Warning-pattern asymmetry resolution

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Decision (option 3 hybrid):
1. **Add `\bPEG\b` as a regex row to `data/fullcatalog/peg_validation.csv`**
   so the validation table is the source of truth for PEG terms (USP-NF
   PEG monograph recognizes "PEG" abbreviation for the polymer).
2. **Keep `\bdairy` in `MILK_NAME` warning patterns** in
   `analyze_dpi_labels.py`. Don't add it to `milk_validation.csv` —
   FARE doesn't list "dairy" as an ingredient, but real-world labels
   use "dairy allergy" as warning vocabulary.
3. **Update `methodology.md` §5** ("Warning-pattern vocabulary") and
   `analysis/allergens/limitations.md` to disclose that warning
   detection is intentionally broader than the flag classification:
   the warning detector matches `\bdairy` (milk) even though FARE
   doesn't list it. After PEG is added to `peg_validation.csv`, the
   PEG asymmetry goes away.
4. **Re-run `analyze_dpi_labels.py` and `analyze_peg_labels.py`**
   to confirm the new behaviour reproduces the existing warning
   counts (18 DPI / 0 PEG) — if either changes, investigate.

## Task #25 — C3 ALLERGY_CONTEXT vocabulary expansion + AI false-positive review

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

The current 4 token roots (`allerg | hypersens | anaphyla | contraindicat`)
are an editorial selection that miss labels using vocabulary like
`intoler`, `sensit`, `react`, `adverse`, `risk`. Two-step fix:

1. **Expand `ALLERGY_CONTEXT` significantly.** Add token roots covering
   the full vocabulary actually used in drug-allergy warning language.
   Candidate set (refine before merging):
   `(?:allerg|hypersens|anaphyla|contraindicat|intoler|sensit|react|adverse|risk\s+of|warn|caution|avoid|known\s+to)`.
   Re-run `analyze_dpi_labels.py`, `analyze_peg_labels.py`,
   `analyze_carmine_labels.py` with the expanded vocabulary.

2. **AI false-positive review of every newly-detected warning.** For
   each new warning hit (i.e. labels that go from "silent" → some
   warning level under the expanded vocabulary), read the triggering
   snippet and the surrounding context. Classify each as:
   - **True positive** — genuinely warns about the allergen.
   - **False positive** — the allergen name and the new context word
     happen to co-occur within 80 chars but the sentence is not a
     warning about the allergen (e.g. ingredient list inside a
     warning section, or a generic adverse-reaction list that
     doesn't single out the allergen).
   - For false positives: tighten the pattern (e.g. require the
     context word and allergen name to be in the same clause, not
     just the same 80-char window).

3. **Update `methodology.md` §5** with the final vocabulary list and
   document the false-positive review pass as the validation step.
   Be explicit that the AI review is an authorized methodology step
   (user-approved 2026-04-23) — not undisclosed AI judgment.

4. **Sample of "still silent" labels too.** After the expansion, also
   sample ~20 random labels still flagged silent per allergen — if
   any of those genuinely warn about the allergen using vocabulary
   the expansion still misses, that's a follow-up tightening.

User direction (2026-04-23): "expand vocabulary significantly and
then do a stringent AI pass to catch any false positives."

**C4 absorbed into this task (2026-04-23).** The 80-character window
between allergen name and allergy-context token is a heuristic, not
empirically verified. Do NOT back-derive a "verified" window size from
the results of this analysis (would be circular — measurements would
trivially confirm 80 because the matcher already filters at 80).
Instead:
- Keep the window value as a heuristic, document it as such in
  `methodology.md` §5 (remove the false "spot-verified against the 18
  DPI snippets" claim).
- The AI false-positive sweep above is the validation step. It
  validates "did the matcher produce defensible outputs," NOT "the
  outputs prove the window size was right." Keep the framings
  separate per the project's process-before-outcome rule.

---

## Task #26 — M1 Move `ALLERGY_CONTEXT` to shared module

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

`ALLERGY_CONTEXT = r"(?:allerg|hypersens|anaphyla|contraindicat)"` is
currently duplicated in `analyze_dpi_labels.py`,
`analyze_peg_labels.py`, `analyze_carmine_labels.py`. Move to
`scripts/spl_label_parser.py` (where `classify_warning_level()` lives)
as a module-level constant. Import in the three analyzers; remove
local copies. Coordinate with Task #25 — the vocabulary expansion
should land at the new shared location, not at the duplicate sites.

---

## Task #27 — M3 `EXCIPIENT_DELIMITER` shared-constant cleanup

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Audit (2026-04-23) confirmed every `;` in
`dailymed_fullcatalog_raw.csv` is followed by exactly one space across
all 171,700 products with at least one `;`. The `"; "` assumption is
correct — no data-correctness fix needed. This task is hygiene only:

1. Define `EXCIPIENT_DELIMITER = "; "` once in
   `scripts/allergen_filters.py` (single source of truth).
2. Import in every script currently hardcoding the literal string:
   `flag_allergens_fullcatalog.py`, `flag_gluten_fullcatalog.py`,
   `build_corpus_tests.py`, `build_gluten_excipient_list.py`,
   `build_gluten_validation.py`.
3. Remove local definitions.
4. Re-run flaggers + corpus tests; confirm byte-identical output.

---

## Task #28 — Allergens baseline filter (homeopathic + unapproved + non-drug exclusion)

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Audit (2026-04-23) showed the current `flag_allergens_fullcatalog.py`
applies flags to the unfiltered raw 199,961 catalog — including
homeopathic products, unapproved drugs, dietary supplements,
animal-tagged products, vaccines, bulk ingredients. Pollution in
current allergen counts:

| Category | contains_milk | contains_peg | contains_carmine |
| :--- | ---: | ---: | ---: |
| Homeopathic | 4,436 (13.2%) | 48 (0.2%) | 2 (1.1%) |
| Unapproved / export / dietary supplement | 4,905 (14.6%) | 588 (2.1%) | 15 (8.5%) |
| Animal-tagged | 16 | 0 | 0 |

Milk count is overstated by roughly 25% from these non-drug rows.

Build `scripts/filter_allergens_baseline.py` (or extend flagger) to
exclude in one pass:
- `bulk_category == "homeopathic"`
- `approval_type` in `{unapproved drug other, export only, dietary
  supplement, unapproved homeopathic, Emergency Use Authorization,
  unapproved medical gas, cosmetic}` (case-insensitive)
- `document_type` indicating non-drug labels (animal, vaccine, device,
  bulk ingredient, allergenic, cellular/gene therapy)

Apply this baseline BEFORE per-allergen flag classification. Re-run
flagger; expect headline numbers to drop (especially milk). Update
all findings/methodology/narrative docs with the new denominators
and percentages.

## Task #29 — Per-allergen harm-anchored route + form filter

**Status:** resolved 2026-04-23
**Added:** 2026-04-23
**Blocked by:** Task #28 (baseline filter must run first)

After the baseline filter (Task #28), each allergen applies its own
route/form slice anchored to the harm mechanism, not a one-size-fits-all
"oral only" rule:

- **Milk** — ORAL (lactose carriers in oral meds) + RESPIRATORY/INHAL
  (DPI lactose carriers, the documented anaphylaxis pathway). IV
  routes added if Hatcher 2025 trace-casein evidence motivates a
  parenteral slice.
- **PEG** — ORAL (oral-solids slice) + INJECTION/IV/SUBCUTANEOUS
  (PEGylated drug bloodstream pathway; primary Stone 2019 anaphylaxis
  setting).
- **Carmine** — landscape (all routes — carmine appears in oral,
  topical, and ophthalmic; harm anchor is oral but the labelling
  question is wider). No additional route filtering beyond the
  baseline.
- **Gluten** — already done via `scripts/filter_gluten_fullcatalog.py`
  (ORAL only).

Document each per-allergen route choice in `methodology.md` Parts 2-4
with the harm-anchor citation that motivated it.

## Task #30 — Gluten-comparable parity stat per allergen

**Status:** resolved 2026-04-23
**Added:** 2026-04-23
**Blocked by:** Task #28

In addition to each allergen's primary slice (Task #29), compute and
report a "gluten-comparable" parity stat using the SAME 6-step
gluten filter (`filter_gluten_fullcatalog.py` output: 72,358 rows,
ORAL-only, FDA-recognized, swallowed). For each allergen, count
`contains_<allergen>` in that 72,358-row filtered set. Add an extra
row to the prevalence table in each `findings_<allergen>.md`:

> Under gluten-methodology filter (ORAL only, FDA-recognized,
> swallowed): N of 72,358 = X%.

Lets the journalism piece make like-for-like comparisons across all
four allergens under one filtering convention.

---

## Task #31 — M6 Carmine landscape: combo-product handling

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Audit (2026-04-23): of 176 carmine products, 140 are single-active
(79.5%) and 36 are combos with 2-11 active ingredients (20.5%).
Notable combo families: sunscreen lip-cosmetic combos (OCTINOXATE +
OCTISALATE + AVOBENZONE / HOMOSALATE), cold/flu OTC multi-symptom
products (ACETAMINOPHEN + DEXTROMETHORPHAN + PHENYLEPHRINE +
optional GUAIFENESIN / TRIPROLIDINE), prescription combos
(LUMACAFTOR + IVACAFTOR = Orkambi), and homeopathic combo remedies.

Update `analyze_allergens_fullcatalog.py` carmine section to report:

1. **Top single-active ingredients** — same `head_ingredient` count
   as today, but restricted to the 140 single-active products only
   (so the count means "single-ingredient products containing
   carmine, by active").
2. **Combo products section** — enumerate the 36 combo products with
   their full active-ingredient lists. Plus a per-active tally
   restricted to combos (showing OCTISALATE 11, ACETAMINOPHEN 8,
   OCTINOXATE 8, DEXTROMETHORPHAN 7, etc.).

Update `findings_carmine.md` §Landscape with both subsections.
Update methodology footnote: the previous "top active ingredients"
list was head-only and undercounted secondary actives in combo
products; new format separates single from combo counts so neither
is misleading.

---

## Task #32 — M7 Manufacturer name normalization in carmine landscape

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

In `analyze_allergens_fullcatalog.py` carmine landscape section, the
manufacturer counter currently uses raw strings with only `.strip()`.
Variants like `"Sixarp, LLC"` vs `"Sixarp LLC"` count separately.

Apply normalization at counting time:
- Uppercase
- Strip trailing punctuation (`,`, `.`, `;`)
- Collapse multiple internal spaces to single
- Strip standard suffixes for matching only (`LLC`, `INC`, `LTD`,
  `CORPORATION`, `CO`, `CORP`, `LIMITED LIABILITY COMPANY`) — but
  retain the most-common original spelling for display.

Re-run `analyze_allergens_fullcatalog.py`; verify the carmine
top-manufacturer list shrinks (or stays the same if no duplicates
existed). Update `findings_carmine.md` §Landscape with the
post-normalization counts.

Apply the same normalization to milk and PEG manufacturer counts
if/when those are reported.

---

## Task #33 — Separate pilot from full catalog (subsumes M8)

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

User direction (2026-04-23): pilot and full catalog should not be
conflated in any methodology or reader-facing doc. They are
independent workflows. Annotating pilot rationales with bulk-catalog
counts (the M8 unfulfilled promise) is no longer needed under this
separation.

Concrete changes:

1. **New file `analysis/allergens/gluten/methodology_pilot.md`** —
   contains all pilot-specific methodology: the original Phase 1-3
   acetaminophen + ibuprofen pull, the 4-tier gluten classification
   as applied to the pilot, the 48-entry `gluten_pilot_validation.csv`,
   the pilot's filtering decisions (excluded injectables only), the
   pilot's findings numbers (97.2% gluten_free / 2.7% unknown / 0.02%
   contains_gluten / 6,605 products). Standalone, no cross-references
   to full-catalog methodology.

2. **`analysis/allergens/methodology.md`** — strip every pilot
   reference. Keep only full-catalog methodology. The current
   `gluten_validation.csv` (171 entries) is described as the
   full-catalog table, not as "pilot + 123 new" derivative.
   Remove the "annotated with `Bulk catalog: N products.`"
   sentence (the annotation never existed; the cross-link is
   gone).

3. **`CLAUDE.md`** — strip pilot references from any "Output File
   Structure" or methodology sections that conflate the two.
   Pilot lives only as a historical Phase 1-3 mention in the
   project-phases section.

4. **`README.md`** — data sections (prevalence numbers, headline
   figures, "Where to read findings" pointers) cover full catalog
   only. Pilot mentioned only as historical context under
   "Project genealogy" — no pilot percentages in the data tables.
   Scientific paper background (Figueiredo 2025), harm anchors
   (Nowak-Wegrzyn, Stone, Greenhawt, etc.), and regulatory framing
   (FALCPA, 21 CFR 201.22, etc.) stay in README — that's the *why*,
   not the data.

5. **Pilot data files stay in place** at `data/pilot/`, treated as
   archive. No annotation update applied. The pilot CSV remains the
   pre-Task-#21 historical snapshot.

6. **Build script `build_gluten_validation.py`** — keep as is
   (still references the pilot CSV as input for PILOT_OVERRIDES
   inheritance). Document this clearly inside the script docstring
   so the cross-reference is honest at the code level even though
   the docs are split.

Verification: after the split, every reference in methodology.md
and README.md to "pilot" should be either (a) absent, or (b)
explicitly tagged as historical context. No pilot numbers should
appear in any prevalence table or headline figure.

---

## Task #34 — M9 File-existence guard for FDA-IID CSV

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

In `scripts/fda_iid_lookup.py`, add an existence check before opening
`FDA-IID-recent-update.csv`. On missing file, exit with a helpful
message that includes the download URL and the expected filename
location at the project root. Prevents cryptic
`FileNotFoundError` mid-pipeline for any caller (e.g.
`build_allergens_validation.py`) that depends on the lookup.

---

## Task #35 — M10 Try/except for malformed regex in validation loaders

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Wrap `re.compile()` calls in `load_validation()` in
`flag_allergens_fullcatalog.py`, `flag_gluten_fullcatalog.py`, and
any other loader that compiles validation-table regex patterns.
On `re.error`, print the validation CSV path, the row number, and
the offending pattern, then exit with a nonzero status. Prevents
cryptic failures when a hand-edited validation CSV contains a
malformed regex.

---

## Task #36 — `.gitignore` cleanup (M11 follow-up)

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Two changes to `.gitignore`:

1. **Remove** `analysis/allergens/gluten/findings_fullcatalog_gluten.md`
   from the "Analysis drafts" block. The file is now an active findings
   doc (post-Task-#17 reorg), not a draft, and should be tracked
   alongside the other findings files.

2. **Add** two crash-recovery / cache patterns the pilot extractor
   creates that should never be committed:
   - `*.partial` — `pull_dailymed_pilot.py` writes these during long
     pulls for resume-after-interrupt support.
   - `.setid_cache.json` — `pull_dailymed_pilot.py` caches set_ids
     to avoid re-querying the DailyMed API. Local-only, regenerable.

After these changes, all currently-untracked files outside the
already-gitignored large CSVs are intended to be tracked. M11 is
resolved by user direction (2026-04-23): "everything visible except
the stuff we already added to gitignore."

---

## Task #37 — Fix stale paths in `analyze_gluten_fullcatalog.py`

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Static path audit (2026-04-23) found one real path bug and a cluster
of stale doc references in `scripts/analyze_gluten_fullcatalog.py`
that the Task #17 sed pass missed:

1. **Output path bug — line 26.** Currently:
   ```python
   OUTPUT_MD = BASE_DIR / "analysis" / "bulk_findings.md"
   ```
   Should be:
   ```python
   OUTPUT_MD = BASE_DIR / "analysis" / "allergens" / "gluten" / "findings_fullcatalog_gluten.md"
   ```
   The path is constructed segment-by-segment so the sed pattern
   `data/bulk/dailymed_bulk_filtered.csv → data/fullcatalog/...`
   never matched it. If the script is re-run, it writes to the
   wrong location (recreates the deleted `analysis/bulk_findings.md`
   in the project root rather than the new findings location).

2. **Stale doc references inside the script's markdown output**
   (lines 3, 6, 113, 213, 268, 598, 622, 669):
   - `analysis/bulk_findings.md` (3 hits) → should be
     `analysis/allergens/gluten/findings_fullcatalog_gluten.md`.
   - `analysis/limitations.md` (4 hits) → should be
     `analysis/allergens/limitations.md` (§Gluten section).
   - `analysis/findings.md` (2 hits) → should be
     `analysis/allergens/gluten/findings_pilot_gluten.md`.
   These are inside string content the script writes into the
   regenerated findings doc, so they'd produce stale references in
   the output. Find/replace inside the script.

3. **Verify with a one-run re-execution** AFTER fix 1 + 2 land —
   `python3 scripts/analyze_gluten_fullcatalog.py` and check that
   the new `findings_fullcatalog_gluten.md` content is correct and
   the old `analysis/bulk_findings.md` is NOT recreated.

Static audit also confirmed: every other script (16 of 17) has
all path constants resolving correctly; all 8 internal imports
between scripts resolve to the renamed modules; FDA-IID,
bulk-data, data/fullcatalog, data/pilot paths all resolve. This
script was the only path-bug survivor of the reorg.

---

## Task #38 — Recover detail in methodology + limitations across all allergens (m1)

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

The original `analysis/limitations.md` (349 lines, gluten-era) was
distilled to ~80 lines as §Gluten in `analysis/allergens/limitations.md`
during Task #17. Detail was lost: the full 4-tier flagging methodology
breakdown, OTC monograph regulatory framework, KIT product handling,
DailyMed source-data inconsistencies, the bulk-filtering pipeline
trade-offs (loss of grandfathered drugs, OTC monograph caveats,
mouthwash-by-name slips, etc.).

User direction (2026-04-23): "all those details for all allergens
(if required) should be present in either the methodology file or
the limitations file."

Concrete steps:

1. **Recover gluten detail** from the deleted
   `analysis/limitations.md` in git history (pre-Task-#17 commit).
2. **Sort into the right doc per item:**
   - "How we did it" content → `methodology.md` (per-allergen
     section, currently Parts 2-4; gluten section to be added per
     Task #33).
   - "What's wrong with it / known caveats" content →
     `analysis/allergens/limitations.md` §Gluten (expand current
     13-numbered list to include the recovered detail).
3. **Apply same depth-review to milk / PEG / carmine** — read each
   allergen's current methodology section + limitations section and
   confirm the same level of detail is present. If anything is
   sparser than gluten's recovered version, expand to match.
4. **Result:** every allergen has the same depth of methodology
   + limitations documentation. No content lost.

Coordinate with Task #33 (pilot vs full-catalog separation) — gluten
methodology is being split into two files; the detail recovery should
land in the new `methodology_pilot.md` (for pilot details) and
`methodology.md` (for full-catalog details) as appropriate.

---

## Task #39 — m2 Delete redundant raw-catalog .zip

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

`data/fullcatalog/dailymed_fullcatalog_raw.csv.zip` (33 MB) is a
compressed duplicate of `dailymed_fullcatalog_raw.csv` (173 MB).
Both gitignored; only the `.csv` is used by any pipeline script.
Delete the `.zip`. Update `.gitignore` to remove the now-unused
entry for the .zip path. Update CLAUDE.md / README.md tree
references that mention the .zip.

---

## Task #40 — m4 Disclose corpus-test scope in methodology

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Add one sentence to `methodology.md` §2.3 (milk), §3.3 (PEG), and
§4.3 (carmine) — the corpus-test description sections — explicitly
noting:

> Corpus tests verify pattern-matching behavior (rule X matches
> DailyMed string Y) only. They do NOT verify the underlying
> classification correctness (whether rule X correctly classifies
> the matched compound as a member of the allergen family). That
> evidence comes from the per-row `source_url` and `rationale`,
> not from the corpus test.

---

## Task #24 — C2 Milk validation table framing

**Status:** resolved 2026-04-23
**Added:** 2026-04-23

Update `methodology.md` §2.4 and any reference in
`analysis/allergens/limitations.md` to state that the milk validation
table includes FARE-listed ingredients **plus DailyMed string variants
of those ingredients** to catch labelling inconsistencies (comma-flips,
double-spaces, .ALPHA. prefixes, etc.). The variants are deterministic
and visible in the CSV. Methodology framing should not say
"AI-generated" — describe as "DailyMed string variants" / "DailyMed
formatting variants" of the FARE-listed ingredients.

---

# Optional / open-decision

## Task TBD — Optional fourth allergen: propylene glycol

**Status:** pending / open decision
**Added:** 2026-04-21

Not scheduled in the main Phase A–E path. Open decision from 2026-04-21:
add propylene glycol as a fourth allergen pass? 27,136 rows in bulk
catalog, chemically distinct from PEG (single 3-carbon diol, not polymer).
Would cover delayed-type hypersensitivity patients. If slotted in, most
natural place is a second iteration through Phase A–C.

---

# Completed tasks

One-liner record of resolved tasks for audit trail. Full execution
detail is in `SESSION_LOG.md` under the relevant session date.

- **Task #8** — Milk workflow hardening — resolved 2026-04-22
  (FARE-anchored validation table; FDA IID cross-reference via local
  CSV; 100% source_url coverage on the rebuilt table).
- **Task #9** — PEG workflow hardening — resolved 2026-04-22
  (tight scope: POLYETHYLENE GLYCOL / OXIDE / MACROGOL / CARBOWAX
  only; USP-NF anchored; adjacent families documented separately).
- **Task #10** — DPI contraindication-level analysis — resolved
  2026-04-22 (`scripts/analyze_dpi_labels.py`; 18 of 19 DPI set_ids
  carry §4 milk-protein contraindication).
- **Task #11** — Editorial scrub + three-layer framing — resolved
  2026-04-22 (rewrote `narrative_draft.md` and three `findings_*.md`
  files to objective language with three-layer regulatory-gap
  framing).
- **Task #12** — Methodology + literature documentation — resolved
  2026-04-22 (Parts 1-4 of `methodology.md` + per-allergen
  `literature.md`; further updates 2026-04-23 in the rigor pass).
- **Task #13** — Carmine workflow hardening — resolved 2026-04-22
  (21 CFR 73.100 + GSRS UNII synonym anchoring; word-boundary regex
  to prevent CROSCARMELLOSE false-positives).
- **Task #14** — Document PEG-adjacent excipients — resolved
  2026-04-22 (`methodology.md` §3.5–3.6 + `limitations.md` §PEG).
- **Task #15** — Rework primer documents to verified-claims-only —
  resolved 2026-04-22 (rewrote `research_{milk,peg,carmine}.md`;
  deleted three `factcheck_log_*.csv` files as redundant).
- **Task #16** — Resolve git tracking policy for large derived CSVs —
  resolved 2026-04-23 (option (a): gitignore all three large derived
  CSVs; symmetric with raw which is already gitignored; one file
  exceeded GitHub's 100 MB per-file limit so a push would have been
  blocked).
- **Task #17** — Project reorganization — resolved 2026-04-23
  (10 scripts renamed, 19 data files moved, 10 analysis files moved
  into per-allergen subfolders; `analysis/limitations.md` absorbed
  into `analysis/allergens/limitations.md` §Gluten;
  `carmine_dailymed_hits.csv` deleted; ~110 path references updated;
  all 17 scripts compile + import cleanly post-rename).
- **Task #18** — README.md rewrite — resolved 2026-04-23
  (564 → 530 lines; four-allergen scope; 5-pipeline reproduction
  guide; manual-verifications section; project genealogy).
- **Task #19** — Carmine contraindication-level label analysis —
  resolved 2026-04-22 (`scripts/analyze_carmine_labels.py`; 0 of 151
  parseable carmine set_ids carry carmine-allergy language; 100%
  silent).
- **Task #20** — PEG contraindication-level label analysis —
  resolved 2026-04-22 (`scripts/analyze_peg_labels.py`; original
  count 3 false-positive warnings; corrected to 0 of 16,585 in the
  2026-04-23 rigor pass after warning patterns were tightened to
  require allergy-context tokens).
- **Task #21** — Anchor validation tables to primary sources —
  resolved 2026-04-22 (strict per-row primary-source URL +
  `iid_status` flag requirement applied to milk / PEG / carmine
  validation tables; AI-reasoned exclusion rows removed).
- **Task #22** — Carmine landscape analysis (no pre-filtering) —
  resolved 2026-04-22 (rewrote `analyze_allergens_fullcatalog.py`
  carmine section to landscape view across route / dosage_form /
  approval_type / bulk_category / brand_generic / top active
  ingredients / top manufacturers).
- **Audit M11** (untracked files from Task #17 reorg need tracking
  decision) — resolved 2026-04-23. User direction: track everything
  except the already-gitignored large CSVs. Two `.gitignore`
  refinements covered by Task #36 (drafts-block cleanup + crash-recovery
  patterns). All other untracked files (10 scripts, 12 markdown, 15
  small CSVs, FDA-IID CSV, TASKS.md) get committed in the next push.
- **Audit M5** (`is_oral_solid` substring matching potentially
  over-inclusive) — audit-resolved no-fix 2026-04-23. Direct check
  of route=ORAL + dosage_form contains TABLET/CAPSULE/GRANULE/PELLET
  combination shows zero SUBLINGUAL / BUCCAL / VAGINAL / RECTAL /
  DENTAL / OPHTHALMIC tablets survive — those products carry
  non-ORAL routes and the route filter excludes them first. The 33
  distinct dosage forms in the slice are all legitimate oral solids.
  TABLET, CHEWABLE (1,896) and TABLET, EFFERVESCENT (150) are
  borderline but genuinely swallowed. No code change.

---

# Deferred items (user-arranged, manual verification)

- **Pharmacist spot-check** of milk / PEG / carmine validation tables.
  Recorded in README §Manual verifications. User-owned, external.
- **`regulations.gov` docket FDA-1998-P-0032** spot-check for
  post-2009 drug-carmine filings. Programmatic access blocked
  (HTTP 403). User-owned, manual.
- **Pilot validation borderline cases** (Q1-Q8 list at
  `analysis/allergens/gluten/validation_table_review_gluten.md`):
  ASO, SSG, cyclodextrins, maltodextrin, HES 130/0.4, HSH,
  source-unspecified starches, oats. Cyclodextrin classification
  rests on a stale 2019 source.
- **Animal-drug bulk-bucket coverage** spot-check. The April 2026
  bulk extraction pulled human OTC, human prescription, homeopathic,
  remainder buckets only. Verify no human medications were
  misclassified into animal buckets.
