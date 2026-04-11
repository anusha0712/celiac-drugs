# Methodological Limitations and Flagging Methodology

*Running log — updated per phase*
*Last updated: March 27, 2026*

---

## Part 1: Flagging Methodology

### Three-Tier Classification System

Every inactive ingredient (excipient) in the dataset is assigned one of three
flags. A fourth flag (`no_data`) applies at the product level when no inactive
ingredients are listed.

#### `contains_gluten`
The excipient is derived from a confirmed gluten-containing grain (wheat, rye,
barley) OR the label explicitly names a gluten grain as the source.

**Criteria — ALL must be met:**
- The excipient IS a gluten grain, or is KNOWN to be derived from a gluten grain
- The derivation process does NOT remove gluten proteins to below 20 ppm
- There is no ambiguity about the source grain

**Examples:** wheat starch, rye, barley, semolina, bran (when wheat-sourced), malt

#### `unknown`
The excipient COULD contain gluten depending on its botanical source or
manufacturing process, but the label does not provide enough information to
determine gluten status. This is the core of the labeling transparency problem.

**Criteria — ANY of the following:**
- The excipient is a starch or starch derivative with NO source grain specified
- The excipient's manufacturing process MAY use a gluten grain as a feedstock,
  and the label does not disclose the feedstock

**Examples:** "pregelatinized starch" (no source), "sodium starch glycolate"
(no source)

**This flag does NOT mean the product contains gluten.** It means a celiac
patient cannot determine from the label alone whether the product is safe.

#### `gluten_free`
The excipient is confirmed to NOT derive from a gluten grain, OR the label
explicitly names a non-gluten source.

**Criteria — ANY of the following:**
- The excipient is not derived from any cereal grain
- The excipient is derived from a non-gluten grain (corn, rice, potato, tapioca)
  and the label specifies the source
- The excipient's chemical class makes gluten presence impossible regardless
  of source (e.g., cellulose-based compounds derived from wood pulp/cotton)
- The excipient is a simple chemical compound with no botanical origin

**Examples:** corn starch, potato starch, croscarmellose sodium (cellulose-based),
pregelatinized corn starch, maltodextrin (corn-derived in US), xanthan gum

#### `no_data`
The product label lists no inactive ingredients at all. Applied at the product
level only. The product cannot be classified.

### Product-Level Flag Assignment

A product's overall gluten flag is determined by its worst excipient:
1. If any excipient is `contains_gluten` → product is `contains_gluten`
2. If none are `contains_gluten` but any are `unknown` → product is `unknown`
3. If all matched excipients are `gluten_free`, OR no excipients match the
   validation table → product is `gluten_free`
4. If the product has no inactive ingredients listed → `no_data`

A product flagged `gluten_free` via rule 3 may contain excipients not in
the validation table (e.g., magnesium stearate, titanium dioxide). These
are not gluten-related and don't affect the flag.

### Decision Rules for Edge Cases

**Source-specified starches:** If the label names the source (e.g., "STARCH,
CORN"), the flag follows the source grain. Corn, potato, tapioca, rice →
`gluten_free`. Wheat → `contains_gluten`.

**Source-unspecified starches:** If the label says only "starch" or
"pregelatinized starch" with no source → `unknown`. Note: FDA CPG 578.100
states unqualified "starch" in the US legally means corn starch, but this
regulatory technicality is not visible to a patient reading the label. The
flag reflects patient-facing information, not regulatory interpretation.

**Sodium starch glycolate (SSG):**
- With source specified (potato or corn) → `gluten_free`
- Without source specified → `unknown`
- Critical: SSG is NOT the same compound as croscarmellose sodium. SSG is
  starch-based; croscarmellose sodium is cellulose-based (wood pulp/cotton).

**"Malt" in the name:**
- "Malt" (the ingredient) → `contains_gluten` (barley-derived)
- "Maltodextrin" → `gluten_free` (corn-derived; unrelated to barley malt)
- Maltitol, ethyl maltol, isomalt → NOT in the validation table (chemically
  distinct compounds that are not gluten-related despite the substring)

**Xanthan gum:** Classified `gluten_free` per National Celiac Association
guidance (https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/).
This is a **methodological departure from the Portuguese study**, which flagged
it precautionarily. The NCA states xanthan gum does not contain gluten.

**"Bran" in the name:**
- "Bran" (unspecified) → `contains_gluten` (most common source = wheat)
- "Rice bran" → `gluten_free` (rice is not a gluten-containing grain, 21 CFR 101.91)

**Corn-derived compounds:** Excipients that explicitly name corn as their
source are `gluten_free`. This includes variant namings: "corn starch,"
"starch, corn," "zea mays (corn) starch," "modified corn starch," etc.

### Validation Table

The validation table (`data/excipient_validation.csv`) contains 48 entries
drawn from three sources:
- **Portuguese study (Table 1):** 14 EU excipient terms and their gluten status
- **FDA Inactive Ingredient Database:** Standard US excipient naming
- **DailyMed dataset:** Actual strings found on product labels in our data

Each entry includes the exact string to match, flag decision, rationale with
chemical identity, UNII code when available, and a citation URL.

### What This Analysis Measures

This is a **labeling transparency analysis**, not a toxicology study. We
measure whether a celiac patient can determine from label information alone
whether an excipient is safe. We are NOT measuring:
- Actual gluten protein levels in any product
- Manufacturing cross-contamination risk
- Whether any product would cause a clinical reaction

A product flagged `unknown` may contain zero gluten. The flag reflects
**information available to the patient**, not the product's actual gluten content.

### Relationship to Source Study

The Portuguese study used a binary classification: "gluten-free" vs
"non-gluten-free." Our three-tier system splits their "non-gluten-free" into
`unknown` and `contains_gluten` to distinguish between labeling ambiguity and
confirmed gluten presence.

When comparing to Portugal, we use `unknown` + `contains_gluten` as the
equivalent of "non-gluten-free." This is the closest match but not identical:
we reclassified xanthan gum to `gluten_free` while they counted it as
non-gluten-free.

---

## Part 2: Data Collection Limitations

### 2.1 Label-based analysis only
Actual gluten protein levels are not measured. A product flagged `unknown` may
contain zero gluten. A product flagged `gluten_free` could theoretically contain
trace gluten from manufacturing cross-contamination. This limitation applies
equally to the Portuguese study.

### 2.2 Cross-contamination undetectable
Manufacturing cross-contamination (shared equipment, shared facilities) cannot
be identified from drug labels. This is a well-known gap in pharmaceutical
allergen safety — shared-line contamination risks are not disclosed on drug
labels.

### 2.3 DailyMed index completeness
Our dataset reflects what was available on DailyMed as of March 26, 2026, and
may not capture every product on the US market. The DailyMed search API may
not index every product. Two products appeared in search results but returned
404 on fetch (removed between indexing and retrieval). We did not cross-reference
against the FDA NDC Directory.

### 2.4 Misspelling coverage
DailyMed contains products with misspelled active ingredient names (e.g.,
"acetominophen"). We searched for common misspellings and found 5 products.
Two were added, two were excluded (withdrawn drug), one was already captured.
There may be additional misspellings we did not search for, though the
ibuprofen search found zero misspellings.

### 2.5 DailyMed index staleness
Two products appeared in DailyMed search results but returned 404 on XML
fetch — they were removed between indexing and retrieval.

### 2.6 Prescription label XML structure
Ten prescription drugs used a different SPL format without structured
`<ingredient>` elements. These were recovered by parsing DESCRIPTION prose,
which is less reliable than structured XML extraction. Three additional labels
with malformed XML were recovered by scraping DailyMed web pages.

### 2.7 KIT-level labeling
428 products are KIT-type packages (e.g., day/night combo packs). KIT labels
typically don't list excipients because the individual components inside have
their own labels. These appear as `no_data` in our dataset. The excipient
information exists — just not at the KIT level we captured.

### 2.8 Snapshot in time
Data pulled March 26, 2026. Formulations change; labels are updated.
Results reflect this date only.

### 2.9 Only two drug categories
Acetaminophen and ibuprofen. Not representative of the full pharmaceutical
market. Other drug categories may have different excipient profiles and
different rates of starch source disclosure.

### 2.10 Combination products included
Some products contain acetaminophen or ibuprofen plus opioids, decongestants,
antihistamines, etc. These combination products may have different excipient
profiles than single-ingredient products. We report single vs. combination
separately in findings.

### 2.11 No dose-level analysis
Excipient quantity per dose is not analyzed. A product containing 2mg of
unspecified-source SSG is flagged identically to one containing 200mg. The
Portuguese study also did not analyze dose levels.

---

## Part 3: Analytical Limitations

### 3.1 Non-equivalence with Portuguese classification
Our three-tier system is not directly equivalent to the Portuguese binary
system. We reclassified xanthan gum (affecting 727 products) and added a
`no_data` category they did not use. Direct percentage comparisons should be
presented with these caveats.

### 3.2 SSG source in practice
Sodium starch glycolate in pharmaceutical manufacturing is predominantly
potato-derived (Type A) or corn-derived. Wheat-derived SSG exists but is rare.
The 154 products flagged `unknown` for SSG most likely contain zero gluten.
The flag reflects labeling ambiguity, not probable gluten presence.

### 3.3 FDA CPG 578.100 interpretation
The FDA's Compliance Policy Guide 578.100 states that the term "starch" without
qualification is the common or usual name for corn starch. Under this rule,
some products flagged `unknown` may be legally defined as corn starch. We
flag patient-facing ambiguity, not regulatory interpretation — a celiac patient
reading the label has no way to know this rule.

### 3.4 Xanthan gum reclassification impact
Reclassifying xanthan gum from `unknown` to `gluten_free` reduced the overall
unknown rate from 13.5% to 2.5%. This is the single largest methodological
decision in the analysis. If the Portuguese study's precautionary classification
is applied instead, US rates would be:
- Acetaminophen: ~16% non-gluten-free (vs. Portugal's 44.4%)
- Ibuprofen: ~18% non-gluten-free (vs. Portugal's 8.2%)

The gap with Portugal would narrow but remain large.

### 3.5 no_data denominator effect
566 products have no excipient data. Including them in the denominator lowers
all flag percentages; excluding them raises them. Findings are reported both
ways. The 428 KIT products in no_data are a structural artifact of label
organization, not necessarily a transparency failure.

### 3.6 Sample size disparity with Portugal
Our dataset is 21× larger than the Portuguese study for acetaminophen (4,986 vs
108) and 19× larger for ibuprofen (1,619 vs 85). The Portuguese percentages
have wide confidence intervals due to small sample size. Their 8.2% ibuprofen
figure has an approximate 95% CI of 3.2–17.0%.

---

## Part 4: Bulk Filtering Limitations

These limitations apply to the bulk catalog filtering pipeline (`scripts/filter_bulk.py`,
locked 2026-04-10), which restricts the 199,961-row raw bulk extraction to the 72,358-row
analysis-ready dataset of FDA-recognized swallowed human medications.

### 4.1 Loss of grandfathered "marketed unapproved drugs"
Step 5 of the filter pipeline drops the entire `unapproved drug other` approval-type
bucket (1,445 rows). This bucket contains both non-medications (herbal supplements,
Korean traditional medicine, foreign imports, vitamin combinations) AND legitimate
grandfathered medications that have been sold in the US for decades but were never
formally approved by FDA via NDA/ANDA review:

- **Phenobarbital** (191 rows) — anticonvulsant, in continuous use since 1912
- **Phenazopyridine HCl** / Pyridium (110 rows) — urinary tract analgesic since 1914
- **Hyoscyamine Sulfate** / Levsin (35 rows) — antispasmodic for IBS, 1800s
- **Armour Thyroid / NP Thyroid / Niva Thyroid / EvexiTHROID** (~70 rows combined) —
  desiccated porcine thyroid extract for hypothyroidism, in use since the 1890s
- **Salsalate** (19 rows) — non-acetylated salicylate anti-inflammatory
- **Donnatal** (12 rows) — atropine/scopolamine/hyoscyamine combination for GI cramping
- **Pyrimethamine + Leucovorin** (12 rows), **Esterified Estrogens + Methyltestosterone**
  (25 rows), **Effer-K** (8 rows), and others

These are real medications taken by real patients every day. Their absence from the
analysis dataset is a known trade-off, accepted in exchange for a clean and defensible
"FDA-recognized" cut. A celiac patient on Phenobarbital or NP Thyroid would not benefit
from this analysis. Manual classification of the 400 unique active ingredients in
the `unapproved drug other` bucket was considered as an alternative but rejected to
keep the methodology simple and reproducible.

### 4.2 OTC monograph drugs included without individual NDA review
Step 5 keeps all OTC monograph drugs (11,098 rows). These are products marketed under
the FDA's OTC Drug Review framework (e.g. 21 CFR 343 for internal analgesics), which
permits sale of any product complying with the published monograph for that drug class.
The FDA does not individually review each manufacturer's product. The monograph specifies
permitted active ingredients, doses, indications, and labeling — but does not vet excipient
selection. This means all generic acetaminophen, ibuprofen, antacids, cough/cold combinations,
and similar products are included even though no individual FDA approval document exists for
each product. This is consistent with the celiac journalism story's focus on OTCs that
patients buy off the shelf.

### 4.3 Possible misclassifications in DailyMed's `approval_type` field
The `approval_type` value comes from the manufacturer's SPL submission to DailyMed, not
from an independent FDA verification. A product may be tagged with an incorrect approval
type. We have not cross-referenced against the FDA Orange Book (NDA/ANDA list) or the
FDA OTC Drug Database to verify approval status. Spot-checks during pipeline development
suggest the approval_type field is reliable for the major categories, but rare
manufacturer-side errors cannot be ruled out.

### 4.4 SPL inconsistencies between `drug_name`, `dosage_form`, and `route`
The DailyMed source data contains label-level inconsistencies that no single column-based
filter can catch:

- **Mouthwash-by-name slip:** 29 products named "Mouthwash" / "Mouth Rinse" / etc.
  carry `dosage_form = LIQUID` instead of `MOUTHWASH`. These bypassed the Step 4
  dosage_form filter and required a Step 6 cleanup based on `drug_name` regex.
- **Wrong-route data errors:** dozens of products had `route = ORAL` despite carrying
  dosage forms that are clearly for other routes (INJECTION, AEROSOL, CREAM, LOTION,
  PATCH, etc.). These were caught by including those forms in Step 4's drop set.
- **Other inconsistencies likely exist** that we did not detect. Products with both a
  conventional drug_name and a conventional dosage_form may still have one column
  populated incorrectly. The pipeline does not attempt cross-column validation beyond
  the explicit Step 6 mouthwash check.

### 4.5 KIT products (cross-reference)
The pipeline keeps KIT-type multi-component packages (1,292 rows). KIT labels typically
do not list excipients at the KIT level — the individual component products inside have
their own labels. These show up as `gluten_flag = no_data` in the flagged output. This
is a continuation of the existing pilot limitation documented in §2.7 above. The
underlying excipient data exists in DailyMed but is not extracted at the KIT level.

### 4.6 Filter step false-negative risk for misclassified homeopathics
Step 2 (`bulk_category != homeopathic`) catches the bulk of homeopathic products, and
Step 5 (`approval_type` filter) catches an additional 48 products explicitly tagged
`unapproved homeopathic`. However, homeopathic-style products that are tagged as
ordinary OTC monograph or NDA in `approval_type` would slip through both filters.
Spot-checks during pipeline development found that the major homeopathic-product
manufacturers (Boiron, Warsan Homeopathic, Newton Laboratories, RUBIMED, etc.) all
correctly tag their products as `unapproved homeopathic`, but products from manufacturers
that sell both homeopathic and conventional drugs (e.g. Schwabe North America) may
classify edge cases inconsistently.

### 4.7 Methodology departure from pilot
The pilot dataset (Phases 1–3, acetaminophen + ibuprofen, 6,605 products) did NOT apply
the bulk filter pipeline. The pilot applied only an injectable-route exclusion (33 products
removed) and kept everything else regardless of dosage form, approval type, or whether
homeopathic. As a result, percentages from the pilot dataset are not directly comparable
to percentages from the bulk filtered dataset. The bulk dataset reflects a stricter "real
swallowed FDA-recognized medication" cut; the pilot reflects a broader "any product
containing acetaminophen or ibuprofen, excluding injectables" cut.
