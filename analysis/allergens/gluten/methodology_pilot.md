# Methodology — Gluten pilot (Phase 1-3)

*Written: 2026-04-23 (created during Task #33 audit-remediation pass).*
*Pilot data snapshot: DailyMed API pull, March 2026.*

This document records the methodology of the original gluten pilot
(Phase 1-3 of the project). The pilot is a historical anchor — the
4-tier gluten classification system, the FDA IIG cross-reference
approach, and the acetaminophen + ibuprofen scope all originated
here. The full-catalog gluten analysis and the milk / PEG / carmine
pipelines superseded this work and are documented separately in
`analysis/allergens/methodology.md`. Pilot is kept distinct so the
two are not conflated in any reader-facing document.

**Why separate (Task #33, 2026-04-23 user direction):** the pilot used
a different filter (injectables-only exclusion), a different
denominator (6,605 vs 199,961 / 165,757), a different naming
convention in code/data paths (`pilot/` vs `fullcatalog/`), and the
pilot validation table (48 entries) was the seed for the full-catalog
gluten validation table (171 entries) but is not the same artifact.
Keeping them in separate methodology files prevents accidental
cross-contamination of numbers or framing.

---

## Part 1 — Scope

The pilot replicated the Portuguese Figueiredo et al. 2025 (Sci Rep
15:10976) methodology on US data via DailyMed. Two drug categories,
matching the Portuguese study's only two oral-medication categories
that mattered for celiac journalism:

- **Analgesics / Antipyretics** — acetaminophen products (Portuguese
  paracetamol equivalent).
- **NSAIDs** — ibuprofen products.

Antiasthmatics / bronchodilators (the third Portuguese study category,
where gluten was 0% by definition because inhalers don't use starch)
were dropped.

Single-ingredient and combination products both included. Generic and
branded both included. Both OTC and Rx, reported separately.

Injectables excluded (33 products removed: IV acetaminophen, IV
ibuprofen). No other route filter.

---

## Part 2 — Data acquisition

`scripts/pull_dailymed_pilot.py` queries the DailyMed JSON API
(`/services/v2/spls.json?drug_name=acetaminophen` and similarly for
ibuprofen), paginates through results, caches `set_id`s, then fetches
SPL XML for each set_id and parses out 39 columns per product
(NDC-level row).

Final pilot dataset: **6,605 products** (4,986 acetaminophen + 1,619
ibuprofen). Saved to `data/pilot/dailymed_pilot_raw.csv` (never
modified after creation). The pull script is idempotent — re-running
extends rather than replaces.

Misspelling sweep performed manually (2026-03-27): searched for common
misspellings of both active ingredients. Two Scot-Tussin products were
added from `acetominophen` hits (5 total hits, 2 added, 3 excluded
because propoxyphene was withdrawn from the US market in 2010). Other
misspellings produced zero hits.

---

## Part 3 — Validation table (48 entries)

`data/pilot/gluten_pilot_validation.csv` — kept unchanged as a
historical snapshot of pilot-era classification decisions. 48 rows
covering FDA IIG ingredient names mapped to one of three flags:
`gluten_free`, `unknown`, or `contains_gluten`.

Schema (6 columns):
- `fda_term` — excipient string as stored in DailyMed (uppercase)
- `source` — FDA IIG, Portuguese study, or DailyMed-derived
- `flag_decision` — `gluten_free` / `unknown` / `contains_gluten`
- `rationale` — one-line justification
- `source_url` — link to FDA IIG, NCA, or other authority
- `eu_equivalent` — if any (for cross-reference with the Portuguese
  study's EU-naming-convention table)

Three notable decisions, all departures from the Portuguese study,
documented at the time:

- **Xanthan gum:** reclassified from `unknown` (precautionary, per
  the Portuguese study) to `gluten_free` per National Celiac
  Association guidance
  (https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/).
  Moved 727 products from `unknown` to `gluten_free`.

- **Sodium carboxymethyl starch:** identified as the same compound as
  sodium starch glycolate (SSG). Croscarmellose sodium is a different
  compound (cellulose-based, gluten-free).

- **Starch (unspecified):** flagged `unknown` despite FDA Compliance
  Policy Guide 578.100 saying unqualified "starch" on US labels means
  corn starch. Rationale: a celiac patient reading the label has no
  way to know that regulatory technicality.

The pilot table also includes 29 explicit `gluten_free` exclusion
rows for FALSE POSITIVES that AI classification would otherwise have
caught (lactic acid, lactobacillus, plant butters, milk thistle,
etc.). Note: this approach was **abandoned in the full-catalog table**
under Task #21 strict rules — exclusion rows without a primary-source
"this is NOT gluten-derived" claim were removed because the flagger
defaults to `gluten_free` on no match, making them unnecessary.

---

## Part 4 — Filtering and flagging

Filter: only injectables excluded (33 products removed). All other
routes, dosage forms, approval types kept. No homeopathic or
unapproved-drug exclusion in the pilot. (The full-catalog
`filter_gluten_fullcatalog.py` 6-step pipeline is a much stricter cut
that did not exist at pilot time.)

Flagger: `data/pilot/gluten_pilot_flagged.csv`. Per-product `gluten_flag`
column under the worst-excipient rule:
- If any excipient is `contains_gluten` → product is `contains_gluten`
- Else if any is `unknown` → product is `unknown`
- Else if `excipients_raw` is empty → product is `no_data`
- Else → product is `gluten_free`

---

## Part 5 — Pilot results

| Flag | Count | % of 6,605 |
|---|---:|---:|
| `gluten_free` | ~6,418 | 97.2% |
| `unknown` | ~178 | 2.7% |
| `contains_gluten` | 1 | 0.02% |
| `no_data` (KIT products + missing) | 8 | 0.1% |

Headline findings:
- 97.2% of pilot products were `gluten_free`.
- The 1 `contains_gluten` product was a wheat-starch-containing
  formulation explicitly labelled.
- 92.8% of `unknown` products were driven by a single excipient:
  SODIUM STARCH GLYCOLATE TYPE A (with no source specified on the
  label).

Comparison to Portuguese study (Figueiredo 2025):
- Portugal: 44.4% paracetamol non-gluten-free, 8.2% ibuprofen
  non-gluten-free.
- Pilot: ~16% acetaminophen non-gluten-free under our methodology
  (xanthan-gum-as-gluten-free); would be higher under Portuguese
  precautionary classification.
- The gap reflects (a) larger US sample size (4,986 vs 108 for
  acetaminophen, 1,619 vs 85 for ibuprofen), (b) xanthan gum
  reclassification, (c) FDA CPG 578.100 corn-starch interpretation
  (we still flag `unknown` because patients can't know the rule).

Detailed pilot findings: `analysis/allergens/gluten/findings_pilot_gluten.md`.

---

## Part 6 — Pilot limitations

1. **Two drug categories only** (acetaminophen + ibuprofen). Not
   generalizable to all medications. The full-catalog analysis covers
   all categories.
2. **Injectables-only exclusion.** No homeopathic or unapproved-drug
   exclusion. Some pilot rows may be products the full-catalog
   pipeline would drop.
3. **No FDA IID cross-reference of every excipient string.**
   Validation rationales cite FDA IIG selectively. Full-catalog
   validation tables (Task #21 strict) cross-reference every row.
4. **KIT products list no excipients at the KIT level.** 8 KIT
   products show `no_data` because the extractor did not unpack
   `<part>` elements.
5. **Snapshot in time.** DailyMed pulled March 26, 2026.
6. **No cross-reference against FDA NDC Directory.** DailyMed is the
   tool the FDA recommends to patients but its index completeness vs
   the NDC Directory is not independently verified.

Detailed pilot limitations: `analysis/allergens/limitations.md`
§Gluten (which absorbed the original 349-line `analysis/limitations.md`
content per Task #17 reorg).

---

## Part 7 — Provenance and cross-reference

**Pilot scripts (used by this methodology):**
- `scripts/pull_dailymed_pilot.py` — DailyMed API pull (pilot extraction).
- `scripts/build_gluten_validation.py` — reads the pilot CSV as input
  for `PILOT_OVERRIDES` inheritance into the full-catalog table. The
  pilot table itself remains unchanged historical artifact.

**Pilot data:**
- `data/pilot/dailymed_pilot_raw.csv` — pilot raw pull (6,605 rows × 39 cols).
- `data/pilot/gluten_pilot_flagged.csv` — pilot + gluten flag columns.
- `data/pilot/gluten_pilot_validation.csv` — 48-entry pilot validation
  table (preserved unchanged since 2026-03-27).

**Pilot analysis:**
- `analysis/allergens/gluten/findings_pilot_gluten.md` — pilot
  findings document (Phase 3 output).
- `analysis/allergens/gluten/source_paper_critique_gluten.md` —
  Phase 1 critical analysis of the Portuguese source study using
  ScholarEval framework (composite 2.9/5).

**Pilot scope ENDS at this file.** The full-catalog gluten analysis
(Phases 4-5) and the milk / PEG / carmine pipelines have separate
methodology in `analysis/allergens/methodology.md`. Don't conflate
the two — different denominators, different filter pipelines,
different validation table schemas.
