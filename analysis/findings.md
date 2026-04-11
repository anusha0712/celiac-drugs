# Findings: Gluten-Related Excipients in US Acetaminophen and Ibuprofen Products

*Analysis date: March 27, 2026*
*Data source: DailyMed (dailymed.nlm.nih.gov), pulled March 26, 2026*

---

## 1. Dataset Overview

### 1.1 Scope

All products listing acetaminophen or ibuprofen as an active ingredient were
extracted from DailyMed via the DailyMed API and XML endpoint. Injectable
formulations (33 products) were excluded. A misspelling sweep identified and
added 2 additional products listed under "acetominophen."

**Total products: 6,605**

| Metric | Count |
|---|---|
| Acetaminophen products | 4,986 |
| Ibuprofen products | 1,619 |
| OTC products | 5,101 |
| Prescription products | 1,502 |
| Other (medical device, bulk) | 2 |
| Single-ingredient products | 3,259 |
| Combination products | 3,346 |
| Products with inactive ingredients listed | 6,039 |
| Products with NO inactive ingredients listed | 566 |

### 1.2 Unit of analysis

Each row represents one NDC (National Drug Code) — a specific product
identified by its shelf-level code. Two NDCs can exist under one SPL label
but have different excipient profiles.

- Total NDCs: 6,605
- Unique SPL labels (set_ids): 6,037
- NDCs sharing a label with different excipients: 568

### 1.3 Exclusions

- Antiasthmatics/bronchodilators — excluded per methodology (inhalers do not
  use starch excipients; the source study found 0% gluten in this category)
- Injectable formulations — 33 removed (IV acetaminophen, IV ibuprofen)
- Propoxyphene products — 2 excluded (withdrawn from US market November 2010)

### 1.4 OTC vs. Prescription classification

Determined by `document_type` field in DailyMed SPL XML:
- "HUMAN OTC DRUG LABEL" → OTC (5,101 products)
- "HUMAN PRESCRIPTION DRUG LABEL" → Rx (1,502 products)
- Other (2 products)

---

## 2. Flagging Methodology Summary

Each product was assigned one of four flags based on its inactive ingredients.
Full methodology and decision rules are documented in `analysis/limitations.md`.

| Flag | Definition |
|---|---|
| `contains_gluten` | At least one excipient is a confirmed gluten grain or derivative with gluten source specified |
| `unknown` | At least one excipient is a starch or starch derivative with no source grain specified; no excipient is confirmed gluten |
| `gluten_free` | All excipients are either non-grain-derived, specify a non-gluten source, or are not in the validation table |
| `no_data` | Label lists no inactive ingredients |

The validation table (`data/excipient_validation.csv`) contains 48 entries:
8 flagged `contains_gluten`, 13 flagged `unknown`, 27 flagged `gluten_free`.
Sources include the Figueiredo et al. (2025) excipient list, the FDA Inactive
Ingredient Database, and actual strings observed in DailyMed labels.

Xanthan gum is classified `gluten_free` per National Celiac Association
guidance. This differs from Figueiredo et al. (2025), which flagged it
precautionarily. Source: https://nationalceliac.org/celiac-disease-questions/does-xanthan-gum-contain-gluten/

---

## 3. Overall Results

### 3.1 All products (n=6,605)

| Flag | Count | % of all | % of products with data (n=6,039) |
|---|---|---|---|
| gluten_free | 5,872 | 88.9% | 97.2% |
| unknown | 166 | 2.5% | 2.7% |
| contains_gluten | 1 | 0.02% | 0.02% |
| no_data | 566 | 8.6% | — |

---

## 4. Results by Drug Category

### 4.1 Acetaminophen (n=4,986)

| Flag | Count | % of all | % with data (n=4,506) |
|---|---|---|---|
| gluten_free | 4,355 | 87.3% | 96.6% |
| unknown | 151 | 3.0% | 3.4% |
| contains_gluten | 0 | 0.0% | 0.0% |
| no_data | 480 | 9.6% | — |

Excipients driving `unknown` in acetaminophen:

| Excipient | Products | % of category unknowns |
|---|---|---|
| SODIUM STARCH GLYCOLATE TYPE A (no source) | 141 | 93.4% |
| PREGELATINIZED STARCH (no source) | 6 | 4.0% |
| SODIUM STARCH GLYCOLATE TYPE B (no source) | 3 | 2.0% |
| SODIUM CARBOXYMETHYL STARCH | 1 | 0.7% |

### 4.2 Ibuprofen (n=1,619)

| Flag | Count | % of all | % with data (n=1,533) |
|---|---|---|---|
| gluten_free | 1,517 | 93.7% | 99.0% |
| unknown | 15 | 0.9% | 1.0% |
| contains_gluten | 1 | 0.1% | 0.1% |
| no_data | 86 | 5.3% | — |

Excipients driving `unknown` in ibuprofen:

| Excipient | Products | % of category unknowns |
|---|---|---|
| SODIUM STARCH GLYCOLATE TYPE A (no source) | 13 | 86.7% |
| PREGELATINIZED STARCH (no source) | 2 | 13.3% |

---

## 5. Results by OTC vs. Prescription

### 5.1 OTC (n=5,101; n with data=4,676)

| Flag | Count | % with data |
|---|---|---|
| gluten_free | 4,517 | 96.6% |
| unknown | 158 | 3.4% |
| contains_gluten | 1 | 0.02% |
| no_data | 425 | — |

OTC uncertainty excipients: SODIUM STARCH GLYCOLATE TYPE A (154),
SODIUM STARCH GLYCOLATE TYPE B (3), SODIUM CARBOXYMETHYL STARCH (1).

### 5.2 Prescription (n=1,502; n with data=1,363)

| Flag | Count | % with data |
|---|---|---|
| gluten_free | 1,355 | 99.4% |
| unknown | 8 | 0.6% |
| contains_gluten | 0 | 0.0% |
| no_data | 139 | — |

Rx uncertainty excipients: PREGELATINIZED STARCH (8). All Rx unknowns trace
to this single excipient.

### 5.3 OTC vs. Rx summary

| Metric | OTC | Rx |
|---|---|---|
| Total products | 5,101 | 1,502 |
| Products with data | 4,676 | 1,363 |
| % unknown or contains_gluten | 3.4% | 0.6% |
| % no_data | 8.3% | 9.3% |
| Primary uncertainty source | SSG Type A (no source) | Pregelatinized starch (no source) |

### 5.4 OTC/Rx × Drug Category (no_data excluded)

| Segment | n | % unknown+gluten | % gluten_free |
|---|---|---|---|
| OTC Acetaminophen | 3,596 | 4.0% | 96.0% |
| OTC Ibuprofen | 1,080 | 1.3% | 98.6% |
| Rx Acetaminophen | 910 | 0.7% | 99.3% |
| Rx Ibuprofen | 453 | 0.4% | 99.6% |

---

## 6. Results by Dosage Form

### 6.1 All dosage forms

| Dosage Form | Count | % of dataset |
|---|---|---|
| TABLET | 1,963 | 29.7% |
| TABLET, FILM COATED | 1,152 | 17.4% |
| CAPSULE, LIQUID FILLED | 635 | 9.6% |
| TABLET, COATED | 617 | 9.3% |
| SUSPENSION | 497 | 7.5% |
| KIT | 428 | 6.5% |
| LIQUID | 345 | 5.2% |
| SOLUTION | 305 | 4.6% |
| TABLET, CHEWABLE | 107 | 1.6% |
| CAPSULE | 89 | 1.3% |
| TABLET, EXTENDED RELEASE | 74 | 1.1% |
| TABLET, FILM COATED, EXTENDED RELEASE | 70 | 1.1% |
| All others (17 forms) | 323 | 4.9% |

### 6.2 Gluten flags by dosage form (no_data excluded)

| Dosage Form | n | % unknown+gluten | % gluten_free |
|---|---|---|---|
| TABLET, EXTENDED RELEASE | 74 | 29.7% | 70.3% |
| TABLET, FILM COATED, EXTENDED RELEASE | 70 | 4.3% | 95.7% |
| TABLET, FILM COATED | 1,140 | 4.1% | 95.9% |
| TABLET, COATED | 617 | 3.6% | 96.4% |
| TABLET | 1,845 | 3.6% | 96.4% |
| TABLET, CHEWABLE | 107 | 2.8% | 97.2% |
| CAPSULE | 84 | 1.2% | 98.8% |
| CAPSULE, LIQUID FILLED | 635 | 0.0% | 100.0% |
| SUSPENSION | 497 | 0.0% | 100.0% |
| LIQUID | 345 | 0.0% | 100.0% |
| SOLUTION | 304 | 0.0% | 100.0% |

### 6.3 Extended-release tablets

TABLET, EXTENDED RELEASE has the highest uncertainty rate at 29.7% (22 of 74
products). All 74 products in this dosage form are acetaminophen. All 22
unknowns are driven by SODIUM STARCH GLYCOLATE TYPE A without source specified.

### 6.4 Dosage form × drug category (solid oral forms, no_data excluded)

**Acetaminophen:**

| Dosage Form | n | % unknown | % gluten_free |
|---|---|---|---|
| TABLET, EXTENDED RELEASE | 74 | 29.7% | 70.3% |
| TABLET, FILM COATED | 630 | 6.8% | 93.2% |
| TABLET, CHEWABLE | 68 | 4.4% | 95.6% |
| TABLET, FILM COATED, EXT REL | 70 | 4.3% | 95.7% |
| TABLET | 1,556 | 4.0% | 96.0% |
| TABLET, COATED | 424 | 3.3% | 96.7% |
| CAPSULE | 75 | 1.3% | 98.7% |
| CAPSULE, LIQUID FILLED | 422 | 0.0% | 100.0% |
| POWDER | 24 | 0.0% | 100.0% |

**Ibuprofen:**

| Dosage Form | n | % unknown+gluten | % gluten_free |
|---|---|---|---|
| TABLET, COATED | 193 | 4.1% | 95.9% |
| TABLET | 289 | 1.4% | 98.6% |
| TABLET, FILM COATED | 510 | 0.8% | 99.2% |
| CAPSULE, LIQUID FILLED | 213 | 0.0% | 100.0% |
| CAPSULE | 9 | 0.0% | 100.0% |
| TABLET, CHEWABLE | 39 | 0.0% | 100.0% |

The ibuprofen TABLET, FILM COATED figure (0.8%) includes the one
`contains_gluten` product (wheat starch).

---

## 7. Sources of Uncertainty

### 7.1 Excipients causing the `unknown` flag

Of 166 products flagged `unknown`, the uncertainty traces to four excipient
strings:

| Excipient | Products | % of unknowns | % of all products |
|---|---|---|---|
| SODIUM STARCH GLYCOLATE TYPE A | 154 | 92.8% | 2.3% |
| PREGELATINIZED STARCH | 8 | 4.8% | 0.1% |
| SODIUM STARCH GLYCOLATE TYPE B | 3 | 1.8% | 0.05% |
| SODIUM CARBOXYMETHYL STARCH | 1 | 0.6% | 0.02% |

Zero products have multiple unknown excipients.

### 7.2 Source-specified vs. unspecified comparison

For the same compound, some labels specify the source and some do not:

**Sodium starch glycolate Type A:**
- With source specified: 1,263 products (864 potato, 393 corn, 6 potato w/ extra space)
- Without source: 154 products
- Ratio: 89.1% specified, 10.9% unspecified

**Pregelatinized starch:**
- With corn source specified: 454 products (452 "STARCH, PREGELATINIZED CORN" + 2 "CORN STARCH (PREGELATINIZED)")
- Without source: 8 products
- Ratio: 98.3% specified, 1.7% unspecified

---

## 8. Confirmed Gluten Product

One product contains a confirmed gluten grain:

| Field | Value |
|---|---|
| Drug name | Ibuprofen |
| Generic name | Ibuprofen |
| Dosage form | TABLET, FILM COATED |
| Route | ORAL |
| OTC/Rx | OTC |
| NDC | 70677-1244 |
| Manufacturer | Strategic Sourcing Services, LLC |
| Marketing status | Active |
| DailyMed URL | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dc469eb2-89cc-46c9-9304-f6cf119c0570 |

Full excipient list: SILICON DIOXIDE; STARCH, CORN; HYPROMELLOSES;
FERRIC OXIDE RED; MAGNESIUM STEARATE; MICROCRYSTALLINE CELLULOSE;
POVIDONE K30; **STARCH, WHEAT**; SODIUM STARCH GLYCOLATE TYPE A CORN;
STEARIC ACID; TITANIUM DIOXIDE; TRIACETIN

This product lists both STARCH, CORN and STARCH, WHEAT in its inactive
ingredients.

---

## 9. No-Data Products

### 9.1 Overview

566 products (8.6%) list no inactive ingredients on their DailyMed label.

### 9.2 Composition

| Dosage Form | Count | % of no_data |
|---|---|---|
| KIT | 428 | 75.6% |
| TABLET | 118 | 20.8% |
| TABLET, FILM COATED | 12 | 2.1% |
| CAPSULE | 5 | 0.9% |
| POWDER | 1 | 0.2% |
| SOLUTION | 1 | 0.2% |
| TABLET, CHEWABLE | 1 | 0.2% |

KIT products are multi-component packages (e.g., day/night combo packs). The
KIT-level label does not list excipients; the individual components inside have
their own separate labels.

Non-KIT no_data products: 138 (118 tablets, 12 film-coated tablets, 5 capsules,
1 powder, 1 solution, 1 chewable tablet).

### 9.3 By category and scope

| Segment | no_data count | % of segment |
|---|---|---|
| Acetaminophen | 480 | 9.6% |
| Ibuprofen | 86 | 5.3% |
| OTC | 425 | 8.3% |
| Rx | 139 | 9.3% |

### 9.4 Marketing status

| Status | Count |
|---|---|
| Active | 469 |
| (blank) | 77 |
| Completed | 20 |

---

## 10. Single-Ingredient vs. Combination Products

No_data excluded:

| Type | n | % unknown+gluten | % gluten_free |
|---|---|---|---|
| Single-ingredient | 2,750 | 3.7% | 96.3% |
| Combination | 3,289 | 2.0% | 98.0% |

---

## 11. Methodological Reference: Comparison to Figueiredo et al. (2025)

The source study used a binary classification ("gluten-free" vs.
"non-gluten-free"). The closest equivalent in our system is `unknown` +
`contains_gluten`. All US figures below exclude no_data from the denominator.

| Metric | Portugal | US |
|---|---|---|
| Paracetamol/Acetaminophen % non-gluten-free | 44.4% (n=108) | 3.4% (n=4,506) |
| Ibuprofen % non-gluten-free | 8.2% (n=85) | 1.0% (n=1,533) |
| Solid oral analgesics % non-gluten-free | 51.2% | 4.5% (n=3,343) |
| Film-coated tablets % non-gluten-free | 61.1% | 4.1% (n=1,140) |
| Regular tablets % non-gluten-free | 60.0% | 3.6% (n=1,845) |
| Products with confirmed gluten grains | 0 | 1 |

Methodological differences affecting comparison:

| Factor | Portugal | US |
|---|---|---|
| Sample size | 108 + 85 | 4,986 + 1,619 |
| Database | INFOMED (SmPCs) | DailyMed (SPL labels) |
| Classification system | Binary | Three-tier + no_data |
| Xanthan gum | Non-gluten-free | Gluten-free (NCA) |
| Unit of analysis | Not specified | NDC |

---

## 12. Interpretation and Analysis

This section presents analytical observations on the data reported above. All
interpretive claims are flagged with their underlying assumptions and cited
where applicable.

### 12.1 Starch source disclosure rates

Of products using starch-based excipients whose gluten status depends on the
source grain, the large majority specify the source:
- SSG Type A: 89.1% specify source, 10.9% do not
- Pregelatinized starch: 98.3% specify source, 1.7% do not

This indicates that starch source disclosure is standard industry practice in
US drug labeling, but not universal. The FDA does not require starch source
disclosure in drug labels — FALCPA (Food Allergen Labeling and Consumer
Protection Act of 2004) mandates wheat disclosure in food labeling but
explicitly excludes drugs (Pub. L. 108-282, §203(a); 21 U.S.C. §343(w)).
Source: https://www.congress.gov/108/plaws/publ282/PLAW-108publ282.htm

The high voluntary disclosure rate suggests that the infrastructure for full
transparency already exists. The gap is in the 10.9% of SSG Type A products
and 1.7% of pregelatinized starch products that omit it.

> ⚠️ **ASSUMPTION:** The high disclosure rate reflects voluntary manufacturer
> practice, not regulatory mandate. We have not verified whether specific FDA
> guidance documents recommend (but do not require) source disclosure. If such
> guidance exists, the non-disclosing products may be non-compliant rather than
> exercising discretion.

### 12.2 Concentration of uncertainty in one excipient

92.8% of all `unknown` flags trace to a single excipient string: SODIUM STARCH
GLYCOLATE TYPE A without source specified. This concentration means the
labeling gap is narrow and specific. It also means that the 2.7% unknown rate
(excluding no_data) is not distributed broadly across diverse excipients — it
reflects a single naming practice by a subset of manufacturers (https://www.fda.gov/media/116958/download)

For comparison, 1,263 products use the same compound with source specified.
The products with and without source specification are pharmaceutically
equivalent in their use of SSG — the difference is what appears on the label.

> ⚠️ **ASSUMPTION:** Products listing "SODIUM STARCH GLYCOLATE TYPE A" without
> a source are using the same potato- or corn-derived compound as those that
> specify. This is consistent with pharmaceutical industry practice (SSG is
> predominantly potato-derived per the Handbook of Pharmaceutical Excipients,
> 9th ed.), but we have not verified the actual source for these specific
> products. If any use wheat-derived SSG, the `unknown` flag is understating
> the risk.
> Source: Rowe, Sheskey, Quinn (eds.), Handbook of Pharmaceutical Excipients,
> 9th edition, Pharmaceutical Press, 2020.

### 12.3 OTC vs. prescription uncertainty gap

OTC products have a 3.4% uncertainty rate vs. 0.6% for prescription products.
The excipients driving uncertainty differ between the two categories:
- OTC: sodium starch glycolate (no source)
- Rx: pregelatinized starch (no source)

This difference may reflect different manufacturer populations. OTC monograph
drugs (which make up the majority of OTC products — 3,763 of 5,101) follow
different labeling pathways than ANDA-approved generics (which dominate the
Rx space). The OTC monograph pathway may have less standardized excipient
naming conventions.

> ⚠️ **ASSUMPTION:** The OTC/Rx difference reflects labeling pathway
> differences, not formulation differences. We have not verified whether OTC
> and Rx products use SSG from different suppliers or sources.

### 12.4 Extended-release tablet uncertainty

The 29.7% unknown rate for extended-release tablets (all acetaminophen) is
notably higher than other dosage forms. All 74 products in this form are
acetaminophen; 22 list SSG Type A without source.

Extended-release formulations use starch glycolate as a matrix-forming
component, not just a disintegrant. This may explain the higher prevalence
of SSG in this form. However, the high rate of source non-disclosure (29.7%)
relative to other tablet forms (3.6–6.8%) is not explained by the excipient's
function alone — it likely reflects a smaller number of manufacturers producing
these products, with one or more consistently omitting the source.

> ⚠️ **ASSUMPTION:** The 29.7% rate reflects a manufacturer concentration
> effect. We have not verified whether a small number of manufacturers account
> for most of the unspecified SSG in extended-release tablets.

### 12.5 Zero uncertainty in non-solid dosage forms

Liquid formulations (suspensions, solutions, liquids, syrups) and liquid-filled
capsules show 0.0% uncertainty across all categories. This is expected:
liquid dosage forms do not use starch-based excipients as binders or
disintegrants. They use solubilizers, suspending agents, sweeteners, and
preservatives — none of which are gluten-related.

This means the labeling transparency question is specific to solid oral dosage
forms. A celiac patient choosing a liquid formulation of acetaminophen or
ibuprofen faces no starch-source ambiguity from the label.

### 12.6 The no_data question

566 products list no inactive ingredients. 428 of these are KITs (multi-product
packages). KIT labels are structural containers — the individual products
inside typically have their own labels with excipient data. The KIT-level
no_data is an artifact of how DailyMed organizes multi-product packages, not
necessarily a transparency failure.

The remaining 138 non-KIT products with no inactive ingredient data are
individual products (tablets, capsules) whose DailyMed labels do not include
excipient information. Of these, 118 are tablets. Whether these products
actually lack excipient data in their physical package inserts (and the
DailyMed label is simply incomplete) or whether they genuinely do not disclose
excipients cannot be determined from DailyMed alone.

> ⚠️ **ASSUMPTION:** KIT-level no_data is structural, not a transparency
> failure. The individual components within KITs likely have their own
> excipient-bearing labels. We have not verified this by looking up the
> individual components.

### 12.7 The confirmed wheat starch product

One product (NDC 70677-1244, ibuprofen film-coated tablet, Strategic Sourcing
Services, LLC) explicitly lists STARCH, WHEAT as an inactive ingredient. This
product also lists STARCH, CORN and SODIUM STARCH GLYCOLATE TYPE A CORN —
both gluten-free. The wheat starch is a distinct additional excipient.

This product is actively marketed and available OTC. It represents 0.02% of
all products in the dataset, or 1 out of 1,533 ibuprofen products with data.

> ⚠️ **ASSUMPTION:** The DailyMed label for this product accurately reflects
> its current formulation. We have not verified the physical package label or
> contacted the manufacturer. DailyMed labels can lag behind reformulations.

### 12.8 Comparison to Portugal: methodological context

The difference between Portugal's 44.4% non-gluten-free rate for paracetamol
and our 3.4% for acetaminophen is large. Three methodological factors
contribute to this difference and should be considered before drawing
comparative conclusions:

**1. Starch source disclosure.** Portuguese SmPCs (Summaries of Product
Characteristics) used terms like "pre-gelatinized starch" and "sodium
carboxymethyl starch" without specifying the botanical source. US DailyMed
labels predominantly specify the source (e.g., "STARCH, PREGELATINIZED CORN").
This is the largest single factor. The Portuguese study's 44.4% was driven
by source-unspecified excipients; the equivalent US excipients are mostly
source-specified.

**2. Xanthan gum classification.** The Portuguese study classified xanthan gum
as non-gluten-free. We classified it as gluten-free per the National Celiac
Association. Xanthan gum appeared on 727 products in our dataset. If we had
matched the Portuguese classification, our overall unknown rate would rise
from 2.5% to approximately 13.5%.

**3. Different regulatory and labeling frameworks.** EU SmPCs and US SPL labels
follow different structures and naming conventions. The FDA's Structured
Product Labeling format requires standardized ingredient names with UNII
(Unique Ingredient Identifier) codes, which may encourage more specific
naming. Direct percentage comparisons between the two systems should be made
with this context.

> ⚠️ **ASSUMPTION:** The Portugal-US difference is primarily a labeling
> transparency difference, not a formulation difference. Both countries likely
> use similar starch sources (predominantly corn and potato) in pharmaceutical
> manufacturing. We have not verified Portuguese excipient sourcing practices.

---

## 13. All Assumptions

Collected from all sections above:

1. High starch source disclosure rates reflect voluntary manufacturer practice,
   not regulatory mandate. Unverified whether FDA guidance recommends source
   disclosure. (Section 12.1)

2. Products listing SSG without source are using the same potato/corn-derived
   compound as those that specify. Consistent with industry practice per
   Handbook of Pharmaceutical Excipients, but unverified for specific products.
   (Section 12.2)

3. OTC/Rx uncertainty difference reflects labeling pathway differences, not
   formulation differences. Unverified. (Section 12.3)

4. The 29.7% extended-release tablet rate reflects manufacturer concentration.
   Unverified. (Section 12.4)

5. KIT-level no_data is structural — individual components likely have their
   own excipient-bearing labels. Unverified. (Section 12.6)

6. The wheat starch product's DailyMed label reflects current formulation.
   Physical label not verified. (Section 12.7)

7. Portugal-US difference is primarily labeling transparency, not formulation.
   Portuguese sourcing practices unverified. (Section 12.8)

8. DailyMed search index captures effectively all acetaminophen and ibuprofen
   products. Two products returned 404 during collection; reverse gaps
   (missing products) are unquantifiable.

9. National Celiac Association guidance on xanthan gum is appropriate for this
   analysis. The NCA states xanthan gum does not contain gluten. If this
   guidance is incorrect or inapplicable to pharmaceutical-grade xanthan gum,
   727 products would shift from gluten_free to unknown.
