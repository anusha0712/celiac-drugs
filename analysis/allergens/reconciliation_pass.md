# Reconciliation Pass — pre-Phase-E cross-workflow consistency sweep

*Opened: 2026-04-23.*

Purpose: when a fix is applied somewhere in the pipeline (validation table,
script, analyzer), all dependent artifacts (findings, limitations,
methodology, narrative, literature) must be updated in sync. This doc
tracks every known fix and its downstream fan-out. Items are executed in
one batch before Phase E begins.

## How to use
- Each fix block lists: source change, every downstream artifact that
  references the affected number/fact/schema, and a status.
- Work each item to done before moving on.
- After all items are done, do a final cover-to-cover consistency read of
  findings / limitations / narrative / methodology / literature / research.
  Anything still stale goes in a new fix block.

## Permanent prevention (post-pass)
Add `methodology.md` Part 6 — "Artifact dependency graph". A static table
keyed by script / validation-table, listing every downstream doc/section
that cites its numbers. Future changes consult the graph before merge.

---

## Fix 1 — PEG warning patterns are over-broad; `findings_peg.md` overreports

**Primary change.** In `scripts/analyze_peg_labels.py`, remove the four
bare-name patterns (`\bpolyethylene\s+glycol`, `\bpolyethylene\s+oxide`,
`\bmacrogol`, `\bcarbowax`). Keep only the three allergy-context patterns.
Re-run `analyze_peg_labels.py` to regenerate `data/fullcatalog/peg_label_analysis.csv`.

**Expected result.** 0 / 16,585 parseable labels carry a PEG-allergy warning
(previously reported as 3: 2 boxed + 1 Section 5). 100% silent. All three
previously-reported "warnings" were ingredient-list mentions of PEG embedded
in a boxed-warning or Section 5 text block, not warnings about PEG.

**Downstream artifacts to update.**
- `findings_peg.md` — Layer 2 table (Boxed 2→0, Section 5 1→0, Silent
  16,582→16,585); Layer 2 prose ("2 carry boxed-warning PEG language, 1
  carries Section 5" → "0 carry any PEG-allergy language").
- `narrative_draft.md` — grep for "boxed", "Section 5", and the count "3"
  in the PEG paragraph. Update if cited.
- `methodology.md` §3 (PEG) — verify no cited number changes.
- `limitations.md` §PEG — add a line documenting the pattern tightening
  (bare-name matches removed → allergy-context-only) so auditors see
  the scope choice.
- `literature.md` — unlikely to cite; verify.

**Status.** done 2026-04-23.

---

## Fix 2 — Corpus tests don't reflect final validation tables

**Primary change.** Regenerate `data/fullcatalog/corpus_test_milk.csv` and
`data/fullcatalog/corpus_test_carmine.csv` against the current validation tables.
- Milk final table is exact-match only; corpus test should list every
  DailyMed excipient string that is an exact match on any `fda_term` in
  `milk_validation.csv`. Current test uses regex patterns that aren't in
  the final table and includes a `MILK THISTLE → review` row that never
  fires in the flagger.
- Carmine final table is 24 rows (21 exact + 3 regex); current corpus test
  has only 3 rows and misses all 21 exact-match terms.
- PEG corpus test appears aligned; verify no drift.

Requires a small helper (or reuse of `flag_allergens_fullcatalog.py` logic) that emits
corpus tests directly from the final tables. Deterministic, one-shot.

**Downstream artifacts to update.**
- `methodology.md` §2 (milk), §3 (PEG), §4 (carmine) — wherever corpus-test
  stats or counts are cited.

**Status.** done 2026-04-23.

---

## Fix 3 — `methodology.md` has stale content in multiple sections

**Primary change.** Update `methodology.md` to match current state.

Known stale spots:
- **§1.3 Validation-table schema.** Lists 6 columns with a `source` column.
  Actual schema is 7 columns: `fda_term, match_type, flag_decision,
  source_url, iid_status, iid_unii, rationale`. Rewrite the schema table.
- **§2.2 Milk UNIIs.** Text says "All 7 primer-named milk-related UNIIs
  confirmed" but only 6 UNIIs are then listed. Cross-check against
  `research_milk.md` and either correct the count or list the seventh.
- **§4.4 Carmine validation table structure.** Claims "12 rows total:
  11 exact + 1 regex". Actual table is 24 rows (21 exact + 3 regex).
  Rewrite the row inventory. Cross-check §4.3 too.
- **§4.5 / §4.7 Carmine harm-anchor filter / results.** Describes drug-class
  slices (azithromycin 8/353, omeprazole 27/877, levothyroxine 22/934,
  calcium carbonate 17/1,867, chewable tablets 24/1,902) that were removed
  by Task #22's landscape rewrite. Rewrite §4.5 (no pre-filter, landscape
  description) and §4.7 (report dimensions: route / dosage_form /
  approval_type / bulk_category / brand_generic / top active ingredients
  for drug-identity labeling / top manufacturers).

**Downstream artifacts.** Self-contained (methodology.md is terminal).
- `findings_*.md` that cross-cite methodology sections — check refs.
- `narrative_draft.md` — check for cites of the removed carmine slices.

**Status.** done 2026-04-23.

---

## Fix 4 — `analyze_allergens_fullcatalog.py` code-quality cleanup

**Primary change.**
- Replace inline `_is_oral_solid` helper (lines 81–89) with
  `from allergen_filters import is_oral_solid`. The same script already
  imports `is_dpi` from `allergen_filters`; this removes the duplicate.
- Rewrite docstring (lines 9–13) to match current behaviour:
  - milk: DPI harm anchor, oral, respiratory, full-catalog.
  - PEG: full-catalog / oral / oral-solids (ODT-excluded) / oral
    solutions-or-powders-for-solution. (No bowel-preps slice — removed
    2026-04-22.)
  - carmine: landscape (no pre-filtering) across route, dosage_form,
    approval_type, bulk_category, brand_generic, top active ingredients
    (drug-identity only), top manufacturers.
- Re-run the script and verify every number cited in findings still
  reproduces.

**Downstream artifacts.** None — code-internal cleanup; numbers don't
change. Verify via re-run.

**Status.** done 2026-04-23.

---

## Fix 5 — Cross-doc consistency sweep (catch-all)

After Fixes 1–4 land, do a cover-to-cover read of every doc below. Flag
and repair any stale number, broken cross-reference, or contradicted
decision. Add new fix blocks to this doc for anything found.

**Docs to read in full.**
- `analysis/allergens/methodology.md` (post-Fix-3)
- `analysis/allergens/limitations.md`
- `analysis/allergens/literature.md`
- `analysis/allergens/narrative_draft.md`
- `analysis/allergens/findings_milk.md`
- `analysis/allergens/findings_peg.md` (post-Fix-1)
- `analysis/allergens/findings_carmine.md`
- `analysis/allergens/research_milk.md`
- `analysis/allergens/research_peg.md`
- `analysis/allergens/research_carmine.md`

**Status.** done 2026-04-23.

---

## Fix 6 — Write "Part 6 — Artifact dependency graph" into methodology.md

**Primary change.** Add a new section to `methodology.md` that documents
which downstream artifacts cite numbers or facts from each script or
validation table. Serves as the consultation checklist for every future
change.

Draft structure:

| If you change… | Re-run | Re-check these docs |
| :--- | :--- | :--- |
| `flag_allergens_fullcatalog.py` or any validation CSV | `flag_allergens_fullcatalog.py` | all findings_*.md prevalence tables, methodology §2.x/§3.x/§4.x |
| `analyze_peg_labels.py` | `analyze_peg_labels.py` | findings_peg.md Layer 2, limitations.md §PEG |
| `analyze_dpi_labels.py` | `analyze_dpi_labels.py` | findings_milk.md Layer 2, limitations.md §Milk |
| `analyze_carmine_labels.py` | `analyze_carmine_labels.py` | findings_carmine.md Layer 2, limitations.md §Carmine |
| `analyze_allergens_fullcatalog.py` carmine section | `analyze_allergens_fullcatalog.py` | findings_carmine.md prevalence + landscape, methodology §4.5/§4.7 |
| `allergen_filters.py` DPI / oral-solid defs | all three label-analysis scripts + analyze_allergens.py | every findings_*.md and limitations.md §filters |
| any `research_{milk,peg,carmine}.md` claim | n/a | methodology.md §2.2/§3.2/§4.2 citation tables; check quote in narrative_draft.md |

Final form filled in during the pass.

**Status.** done 2026-04-23.

---

## Execution order

1. Fix 1 (PEG patterns) — changes a published number; do first.
2. Fix 2 (corpus tests) — isolated, easy, deterministic.
3. Fix 3 (methodology stale content) — lots of edits, no data re-run.
4. Fix 4 (analyze_allergens.py cleanup) — no number changes; verify re-run
   reproduces findings.
5. Fix 5 (sweep) — catches anything missed.
6. Fix 6 (dependency graph) — seals the gate before Phase E.
