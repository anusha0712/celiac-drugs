# Validation Table Review — Pending Changes

Items identified during cross-check against external celiac references that
need to be applied to `data/fullcatalog/gluten_validation.csv`. Not yet applied.

## Source provenance reference

For every classification decision in this file, the source(s) backing it are
listed. Sources are categorized as **current** (within 5 years, per project rule)
or **stale** (older than 5 years).

| Source | Date | Status |
|---|---|---|
| National Celiac Association — "Ingredients People Question" | undated, current | current |
| National Celiac Association — "Glucose Syrup From Wheat" | undated, current | current |
| National Celiac Association — "Does Xanthan Gum Contain Gluten?" | undated, current | current |
| FDA Inactive Ingredient Database (IIG) | continuously updated | current |
| FDA 21 CFR 101.91 (gluten grain definition) | regulation | current |
| FDA CPG Sec 578.100 (starches common names) | regulation | current |
| Gluten Intolerance Group (GIG) "Medications and the Gluten-Free Diet" PDF | January 2019 | **STALE (>5y)** |
| Plogsted, "Medications and Celiac Disease," Practical Gastroenterology | January 2007 | **STALE (>5y)** — not used |

**Rule:** Decisions backed only by stale sources should be flagged for re-evaluation
with current evidence or pharmacist consultation.

---

## 1. GLUCOSE family — change `unknown` → `gluten_free`

**Affected entries in validation table:**
- GLUCOSE (current: unknown) — bulk catalog: 42 products
- GLUCOSE SYRUP (current: unknown) — bulk catalog: 0 products
- LIQUID GLUCOSE (current: unknown) — bulk catalog: 0 products

**New flag:** gluten_free

**Source provenance:** ✅ Current sources only
- National Celiac Association — "Glucose Syrup From Wheat in a Gluten-Free Product"
  https://nationalceliac.org/celiac-disease-questions/glucose-syrup-from-wheat-in-a-gluten-free-product/
- National Celiac Association — "Ingredients People Question"
  https://nationalceliac.org/ingredients-people-question/
  Quote: "Glucose syrup is considered safe even when derived from wheat, barley or rye
  because the process used to produce glucose syrup renders the starting material to
  contain less than 20 parts per million of gluten. Dextrose is simply another word
  for glucose. It is considered gluten free regardless of the starting material."

---

## 2. MALTODEXTRIN — keep `gluten_free`, add supporting source

**Current flag:** gluten_free (no change)
**Current source URL:** https://www.fda.gov/media/116958/download (FDA IIG)
**Affected products in bulk catalog:** 4,129

**Note:** Maltodextrin is a LINEAR polysaccharide (partially hydrolyzed starch).
It is chemically distinct from cyclodextrin (a CYCLIC oligosaccharide). Decisions
about maltodextrin and cyclodextrin must NOT be chained.

**Source provenance:** ✅ Current sources only
- FDA Inactive Ingredient Database (existing in pilot entry)
- National Celiac Association — "Ingredients People Question" (to be added)
  https://nationalceliac.org/ingredients-people-question/
  NCA quote: "Maltodextrin is a starch hydrolysate that may be made from wheat
  starch but is usually made from cornstarch, especially in the US. Regardless
  of the starting material, maltodextrin is considered gluten free."

**Action:** Append the NCA URL to the source_url field for the MALTODEXTRIN entry.
No flag change. Also add to pharmacist consultation list (Q4) per user instruction.

---

## 3. CYCLODEXTRINS — flag as `gluten_free` (interim decision)

**Status:** Not yet in validation table. None of our 20 keywords match
"cyclodextrin" or "betadex," so they were missed by the keyword search.

**Interim decision (2026-04-09):** Add cyclodextrin family entries flagged as
`gluten_free` per user instruction. Pending pharmacist consultation for verification
(see Q3 below).

**⚠️ Source provenance: STALE — re-evaluate.**
The only source that explicitly classifies cyclodextrins is the Gluten Intolerance
Group (GIG) "Medications and the Gluten-Free Diet" PDF, **January 2019** (7 years
old, exceeds the project's 5-year rule). The document itself states: "If this
document is more than 2 years old, please visit our website for updated documents."
No current source (NCA, CDF, FDA, or peer-reviewed within 5 years) explicitly
addresses cyclodextrin gluten status in pharmaceutical labeling.

**Note:** Cyclodextrins are CYCLIC oligosaccharides — chemically distinct from
maltodextrin (a LINEAR polysaccharide). Their classifications are NOT chained.

**Strings present in bulk catalog (15 unique strings, 381 unique products,
559 total appearances):**

| String | Product count |
|---|---|
| CYCLODEXTRINS | 261 |
| BETADEX | 133 |
| BETADEX SULFOBUTYL ETHER SODIUM | 58 |
| HYDROXYPROPYL BETADEX | 38 |
| CYCLODEXTRIN | 29 |
| HYDROXYPROPYL .GAMMA.-CYCLODEXTRIN | 9 |
| HYDROXYPROPYL .ALPHA.-CYCLODEXTRIN | 6 |
| HYDROXYPROPYL .BETA.-CYCLODEXTRIN | 6 |
| SULFOBUTYLETHER .BETA.-CYCLODEXTRIN | 5 |
| GAMMA CYCLODEXTRIN | 4 |
| HYDROXYPROPYLBETADEX (0.58-0.68 MS) | 3 |
| ADRABETADEX | 3 |
| .BETA.-CYCLODEXTRIN SULFOBUTYL ETHER | 2 |
| O-METHYL-.BETA.-CYCLODEXTRIN (1.8 METHYLS PER SACCHARIDE) | 1 |
| HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE) | 1 |

**Distribution:**
- Routes: TOPICAL 195, ORAL 103, INTRAVENOUS 49, INTRAMUSCULAR 12, OPHTHALMIC 9,
  CUTANEOUS 4, SUBCUTANEOUS 2, INTRAVESICAL 2, NASAL 2, INTRAEPIDERMAL 1
- Top dosage forms: STICK 84, CREAM 54, INJECTION POWDER LYOPHILIZED 37,
  TABLET 27, LOTION 20, SOLUTION 15, INJECTION SOLUTION 15
- bulk_category: human_otc 231, human_prescription 140, homeopathic 9, other 1

**Sources reviewed:**
- The user-provided screenshot lists "Cyclodextrins" under "Excipients which could
  be derived from wheat or barley." This is the only direct reference found that
  classifies cyclodextrins specifically.
- Celiac Disease Foundation "Gluten in Medicine, Vitamins & Supplements" page —
  does NOT mention cyclodextrins.
  https://celiac.org/gluten-free-living/gluten-in-medicine-vitamins-and-supplements/
- National Celiac Association "Ingredients People Question" page — does NOT mention
  cyclodextrins. https://nationalceliac.org/ingredients-people-question/
- FDA: no specific guidance on cyclodextrin source disclosure in drug labels found.

---

## 4. ICODEXTRIN — flag as `gluten_free`

**Status:** Not in validation table. Add as new entry.
**New flag:** gluten_free
**Rationale:** Derived from maltodextrin (a linear starch hydrolysate). Used as
an osmotic agent in peritoneal dialysis solutions.
**Bulk catalog appearances:** 186 products
**Source provenance:** ✅ Current — chains from MALTODEXTRIN classification, which
is supported by current NCA + FDA IIG sources. Does NOT depend on the GIG 2019 PDF.

---

## 5. MALTODEXTRIN/VP COPOLYMER (1000 MPA.S) — flag as `gluten_free`

**Status:** Not in validation table. Add as new entry.
**New flag:** gluten_free
**Rationale:** Copolymer of maltodextrin (linear starch hydrolysate, gluten_free)
and vinylpyrrolidone (synthetic monomer with no grain involvement). Used as a film
former. The "1000 MPA.S" specifies viscosity, not chemistry.
**Bulk catalog appearances:** 2 products
**Source provenance:** ✅ Current — chains from MALTODEXTRIN classification, which
is supported by current NCA + FDA IIG sources. Does NOT depend on the GIG 2019 PDF.

---

## 6. False positives — add to table as `gluten_free` (Option A)

**Status:** Currently 22 keyword-matched terms are excluded from the validation table
and only documented in CLAUDE.md. Plan: add them to the validation table as
`gluten_free` with rationale "Keyword false positive — matched gluten-adjacent
search term but compound is not grain-derived."

**Why:** Makes the validation table the single source of truth. Re-running
`build_gluten_excipient_list.py` will not require re-excluding them by hand.

**Terms to add as gluten_free with false-positive rationale:**

*Glycolate esters (5):*
- SODIUM GLYCOLATE — sodium salt of glycolic acid (alpha-hydroxy acid)
- ETHYL GLYCOLATE — ester of glycolic acid
- ALLYL AMYL GLYCOLATE — fragrance compound
- BUTYL GLYCOLATE — ester of glycolic acid
- CEFATRIZINE PROPYLENE GLYCOLATE — cephalosporin antibiotic salt

*Methyl glucose esters (6):*
- PEG-120 METHYL GLUCOSE DIOLEATE
- METHYL GLUCOSE SESQUISTEARATE
- PEG-20 METHYL GLUCOSE SESQUISTEARATE
- METHYL GLUCOSE DIOLEATE
- PPG-20 METHYL GLUCOSE ETHER
- PPG-20 METHYL GLUCOSE ETHER DISTEARATE
- METHYL GLUCOSE (synthetic methylated sugar)

*Glucose biochemicals (8):*
- GLUCOSE OXIDASE — enzyme from Aspergillus niger
- DIPOTASSIUM GLUCOSE-6-PHOSPHATE — biochemical
- PSEUDOMONAS GLUCOSE FERMENTATION RHAMNOLIPIDS — biosurfactant
- 2,3 DI-O-METHYL-D-GLUCOSE — synthetic sugar derivative
- GLUCOSE-6-PHOSPHATE — biochemical
- GLUCOSE PENTAACETATE — chemical derivative
- GLUCOSE 1,6-BISPHOSPHATE — biochemical
- .ALPHA.-GLUCOSE-1-PHOSPHATE DIPOTASSIUM DIHYDRATE — biochemical

*Silicone (1):*
- DIMETHICONOL GUM — silicone polymer, "gum" is physical texture not plant gum

**Total to add as false-positive gluten_free:** 21 terms (not 22 — see fix below)

**Fix needed:**
HYDROXYPROPYL BETADEX (0.6 HYDROXYPROPYL RESIDUES PER GLUCOSE) was originally
excluded as a false positive. With the cyclodextrin decision (item 3), this string
should NOT be a false positive — it should be added with the other cyclodextrin
entries flagged as `gluten_free` (cyclodextrin rationale, not false-positive rationale).
Net result: still 1 entry, but in the cyclodextrin group rather than the false-positive
group. CLAUDE.md needs to be updated to reflect this.

---

# Open Questions for Pharmacist Consultation

The following decisions involve excipients where the starch source is not declared
on the label and the project's strict label-based rule says "unknown," but where
celiac authorities, industry practice, or processing chemistry may justify
re-classifying as `gluten_free`. Pharmacist input would help resolve them.

These are listed here so we can revisit them later with informed expert guidance.

## Q1. ALUMINUM STARCH OCTENYLSUCCINATE (ASO)

**Current flag:** unknown (861 products in bulk catalog)
**Current rationale:** Source-unspecified starch derivative.
**Distribution:** 859/861 are TOPICAL (sunscreens, lotions, deodorants); only 2
are ORAL (PureTek prenatal multivitamins).
**Pharmacist questions:**
- Is pharmaceutical-grade ASO ever wheat-derived in practice, or is it always
  corn/tapioca/potato?
- For topical-only ASO, does gluten exposure risk exist at all (gluten generally
  cannot penetrate intact skin)?
- For the 2 oral ASO products, what is the source supplier's typical practice?

## Q2. SODIUM STARCH GLYCOLATE (SSG) without source specified

**Current flag:** unknown (1,123 products in bulk catalog for SSG TYPE A alone)
**Current rationale:** Source-unspecified starch derivative.
**Pharmacist questions:**
- Is SSG with no source on the label predominantly potato-derived per current
  industry sourcing?
- Are there any wheat-derived SSG suppliers active in the US pharmaceutical
  supply chain?
- How do compounding pharmacists currently advise celiac patients about generic
  drugs containing unspecified-source SSG?

## Q3. CYCLODEXTRINS / BETADEX (interim flag: gluten_free)

**Current interim flag:** gluten_free (pending pharmacist input)
**Distribution:** 381 products across topical, oral, and injectable routes.
**Pharmacist questions:**
- Are pharmaceutical-grade cyclodextrins always corn-derived?
- Is the gamma cyclodextrin "may be wheat-derived" claim that appears in some
  third-party sources accurate, and if so, in what fraction of US drug products?
- Does the cyclization process in CD manufacturing reliably reduce gluten below
  20 ppm regardless of starting material (similar reasoning to maltodextrin)?

## Q4. MALTODEXTRIN

**Current flag:** gluten_free (4,129 products)
**Pharmacist questions:**
- For US-marketed drugs, is maltodextrin in pharmaceutical excipients always
  corn-derived, or do wheat-derived sources enter the supply chain?
- Are there any documented celiac reactions to pharmaceutical maltodextrin?

## Q5. HYDROXYETHYL STARCH 130/0.4

**Current flag:** unknown (1 product)
**Pharmacist questions:**
- Is HES 130/0.4 always derived from waxy maize (corn) per FDA-approved
  pharmaceutical practice? If so, can we treat it as gluten_free?

## Q6. HYDROGENATED STARCH HYDROLYSATE

**Current flag:** unknown (40 products)
**Pharmacist questions:**
- What is the typical starch source for pharmaceutical-grade HSH?
- Is the hydrogenation process sufficient to reduce gluten below 20 ppm if the
  starting material were wheat?

## Q7. Source-unspecified starches generally

**Affected entries:** STARCH (unspecified), PREGELATINIZED STARCH (no source),
MODIFIED STARCH (no source), FOOD STARCH-MODIFIED, GELATINIZED STARCH
**Pharmacist questions:**
- Per FDA CPG 578.100, unqualified "starch" in food = corn starch. Does the same
  rule apply in practice for drug labeling, even though FALCPA does not cover drugs?
- Do compounding pharmacists treat unqualified "starch" in drug labels as corn
  starch by default, or do they assume the worst case?

## Q8. Oats and oat derivatives

**Current flag:** unknown (17 entries, 525 products in bulk catalog)
**Distribution:** 508 TOPICAL, 9 CUTANEOUS, 4 ORAL, 2 RECTAL, others minimal —
98.5% topical/cutaneous; only 4 oral.
**Current rationale:** Oats are not classified as a gluten-containing grain by
FDA per 21 CFR 101.91, but cross-contamination with wheat/barley/rye during
cultivation, harvesting, and processing is documented. Pilot decision was
precautionary `unknown`.
**Pharmacist questions:**
- For pharmaceutical-grade oat ingredients (especially Avena sativa extracts in
  dermatologic and cosmetic-adjacent products), are suppliers using certified
  gluten-free oats or commodity oats?
- For the 4 oral oat products, what is the typical supplier and source?
- Does the Celiac Disease Foundation or another current authority have a
  position on pharmaceutical oat ingredients specifically (vs. food oats)?
- For topical oat products on intact skin, does cross-contamination concern
  apply at all (gluten cannot penetrate intact skin)?
