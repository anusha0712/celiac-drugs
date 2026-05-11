# Bulk Catalog Findings: Gluten Labeling Transparency in FDA-Recognized Oral Medications

*Analysis date: 2026-04-23*
*Data source: DailyMed bulk download (April 6, 2026), filtered per CLAUDE.md "Bulk Filtering Decisions (2026-04-10)"*
*Scope: FDA-recognized human medications directly delivered to the GI tract by swallowing*
*Input file: `data/fullcatalog/gluten_fullcatalog_flagged.csv` (72,358 rows)*

This document reports objective data cuts on the bulk dataset. It contains no
interpretation. Methodology is documented in CLAUDE.md; limitations are
documented in `analysis/allergens/limitations.md` §Gluten.

**Denominator convention:** All percentages reported in the breakdown sections
exclude `no_data` products from the denominator unless a column header
explicitly says otherwise. The `no_data %` column, where shown, is computed
against the full subset total.


## Executive Summary

- **Dataset:** 72,358 FDA-recognized swallowed human medications
- **Confirmed gluten grain on label:** 12 products (0.02% of products with data)
- **Cannot be determined safe from label alone (`unknown`):** 1,028 products (1.48% of products with data)
- **Confirmed gluten-free from label:** 68,277 products (98.50% of products with data)
- **No excipient data on label (`no_data`):** 3,041 products (4.20% of total)
- **Share of `no_data` that is KIT packages:** 41.20% (1,253 of 3,041)
- **Top excipient driving `unknown`:** `SODIUM STARCH GLYCOLATE TYPE A` — 999 products
- **Uncertainty rate (no_data excluded):** OTC 3.09% vs Rx 1.06%


## 1. Scope and Dataset Composition

| Metric | Count |
| :--- | ---: |
| Total products | 72,358 |
| Products with excipient data | 69,317 (95.80%) |
| Products without excipient data (`no_data`) | 3,041 (4.20%) |
|  |  |
| OTC drug labels | 15,958 |
| Prescription drug labels | 56,397 |
| Prescription drug labels with highlights | 3 |
| Human compounded drug labels | 0 |
|  |  |
| Brand (NDA / BLA) | 7,036 |
| Generic (ANDA / NDA authorized generic) | 54,253 |
| OTC monograph | 11,069 |
|  |  |
| Single-ingredient products | 62,582 |
| Combination products | 9,776 |
|  |  |
| DEA controlled substances | 6,580 |
| Non-controlled | 65,778 |

Unit of analysis: NDC-level. The bulk extraction produces one row per
`<manufacturedProduct>` block in the SPL XML, so a single SPL label can
contribute multiple rows when different NDCs carry different dosage forms
or excipient profiles.

Full filter pipeline: CLAUDE.md § "Bulk Filtering Decisions (2026-04-10)".
Full limitations: `analysis/allergens/limitations.md` §Gluten.


## 2. Headline Results — All Products

| Flag | Count | % of all products | % of products with data |
| :--- | ---: | ---: | ---: |
| `gluten_free` | 68,277 | 94.36% | 98.50% |
| `unknown` | 1,028 | 1.42% | 1.48% |
| `contains_gluten` | 12 | 0.02% | 0.02% |
| `no_data` | 3,041 | 4.20% | — |
| **Total** | **72,358** | **100.00%** | **n = 69,317** |


## 3. Confirmed Gluten Products

The following 12 products explicitly list a confirmed gluten grain
(wheat, barley, or rye, or an identified derivative thereof) on their DailyMed
label. "Confirmed" here means the label string names the grain; it does not
mean the product has been tested for gluten protein content. See
`analysis/allergens/limitations.md` §Gluten on the label-only methodology.

| Drug name | Manufacturer | Dosage form | NDC | Flagged excipient(s) |
| :--- | :--- | :--- | :--- | :--- |
| Dermamed Nutrition for troubled skin | DermaMed | CAPSULE, GELATIN COATED | 69711-687 | WHEAT GERM OIL |
| Tums Chewy Bites | Haleon US Holdings LLC | TABLET, CHEWABLE | 0135-0606 | STARCH, WHEAT |
| Tums Chewy Bites | Navajo Manufacturing Company Inc. | TABLET, CHEWABLE | 67751-235 | STARCH, WHEAT |
| Tekturna HCT | Noden Pharma USA, Inc. | TABLET, FILM COATED | 70839-112 | STARCH, WHEAT |
| Tekturna HCT | Noden Pharma USA, Inc. | TABLET, FILM COATED | 70839-125 | STARCH, WHEAT |
| Tekturna HCT | Noden Pharma USA, Inc. | TABLET, FILM COATED | 70839-312 | STARCH, WHEAT |
| Tekturna HCT | Noden Pharma USA, Inc. | TABLET, FILM COATED | 70839-325 | STARCH, WHEAT |
| Tekturna HCT | Physicians Total Care, Inc. | TABLET, FILM COATED | 54868-6041 | STARCH, WHEAT |
| Tekturna HCT | Physicians Total Care, Inc. | TABLET, FILM COATED | 54868-6103 | STARCH, WHEAT |
| Tekturna HCT | Physicians Total Care, Inc. | TABLET, FILM COATED | 54868-6194 | STARCH, WHEAT |
| Tums Chewy Bites | Select Consumer Group | TABLET, CHEWABLE | 85237-1860 | STARCH, WHEAT |
| Ibuprofen | Strategic Sourcing Services, LLC | TABLET, FILM COATED | 70677-1244 | STARCH, WHEAT |


## 4. Breakdowns

All percentages in this section exclude `no_data` from the flag denominator.
The `no_data %` column is computed against the subgroup total.

### 4.1 By Regulatory Category

| Category | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| OTC drug label (document_type) | 15,958 | 96.91% | 3.05% | 0.03% | 4.79% |
| Prescription drug label (document_type) | 56,397 | 98.94% | 1.04% | 0.01% | 4.04% |
| ANDA (generic Rx) | 54,253 | 98.61% | 1.39% | 0.00% | 3.34% |
| NDA (brand Rx) | 5,741 | 97.93% | 1.93% | 0.13% | 8.92% |
| NDA authorized generic | 1,250 | 98.84% | 1.16% | 0.00% | 3.60% |
| OTC monograph (all variants) | 11,069 | 98.23% | 1.73% | 0.04% | 5.96% |
| BLA (biologic) | 45 | 87.88% | 12.12% | 0.00% | 26.67% |

### 4.2 By Dosage Form (Top 20 by Row Count)

| Dosage form | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Tablet | 25,036 | 98.30% | 1.70% | 0.00% | 2.66% |
| Tablet, Film Coated | 15,255 | 97.96% | 1.99% | 0.05% | 1.70% |
| Capsule | 8,768 | 99.43% | 0.57% | 0.00% | 2.70% |
| Tablet, Extended Release | 3,042 | 97.46% | 2.54% | 0.00% | 3.06% |
| Solution | 2,088 | 100.00% | 0.00% | 0.00% | 1.53% |
| Tablet, Coated | 1,833 | 97.01% | 2.99% | 0.00% | 1.58% |
| Capsule, Liquid Filled | 1,781 | 100.00% | 0.00% | 0.00% | 0.56% |
| Liquid | 1,728 | 99.82% | 0.18% | 0.00% | 1.45% |
| Capsule, Extended Release | 1,677 | 99.82% | 0.18% | 0.00% | 1.97% |
| Tablet, Chewable | 1,658 | 98.13% | 1.69% | 0.18% | 0.12% |
| Tablet, Film Coated, Extended Release | 1,553 | 99.81% | 0.19% | 0.00% | 0.84% |
| Suspension | 1,287 | 100.00% | 0.00% | 0.00% | 1.17% |
| Kit | 1,253 | — | — | — | 100.00% |
| Tablet, Delayed Release | 1,227 | 95.76% | 4.24% | 0.00% | 1.96% |
| Capsule, Delayed Release | 990 | 99.59% | 0.41% | 0.00% | 1.82% |
| Powder, For Suspension | 632 | 100.00% | 0.00% | 0.00% | 4.91% |
| Powder, For Solution | 330 | 100.00% | 0.00% | 0.00% | 40.30% |
| Syrup | 309 | 99.34% | 0.66% | 0.00% | 1.94% |
| Capsule, Gelatin Coated | 295 | 96.55% | 3.10% | 0.34% | 1.69% |
| Powder | 176 | 100.00% | 0.00% | 0.00% | 11.93% |

Dosage forms outside the top 20 are omitted from the table but are included
in all section-level totals and in Section 2.

### 4.3 Single-Ingredient vs Combination

| Product type | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Single-ingredient | 62,582 | 98.51% | 1.48% | 0.01% | 4.54% |
| Combination | 9,776 | 98.43% | 1.48% | 0.08% | 2.07% |

### 4.4 By DEA Schedule

| DEA schedule | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Non-controlled | 65,778 | 98.41% | 1.57% | 0.02% | 4.32% |
| Schedule II | 2,629 | 99.96% | 0.04% | 0.00% | 1.79% |
| Schedule III | 519 | 99.39% | 0.61% | 0.00% | 5.78% |
| Schedule IV | 2,386 | 98.52% | 1.48% | 0.00% | 3.60% |
| Schedule V | 1,046 | 100.00% | 0.00% | 0.00% | 3.35% |

### 4.5 By Active Ingredient String (Top 20 by Row Count)

| Active ingredient(s) | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| IBUPROFEN | 1,559 | 99.25% | 0.68% | 0.07% | 5.45% |
| ACETAMINOPHEN | 1,410 | 93.22% | 6.78% | 0.00% | 0.64% |
|  | 1,253 | — | — | — | 100.00% |
| DIPHENHYDRAMINE HYDROCHLORIDE | 944 | 100.00% | 0.00% | 0.00% | 0.21% |
| GABAPENTIN | 813 | 100.00% | 0.00% | 0.00% | 6.15% |
| LEVOTHYROXINE SODIUM | 806 | 95.51% | 4.49% | 0.00% | 0.62% |
| CALCIUM CARBONATE | 754 | 99.60% | 0.00% | 0.40% | 0.00% |
| PREGABALIN | 677 | 100.00% | 0.00% | 0.00% | 3.25% |
| METFORMIN HYDROCHLORIDE | 662 | 100.00% | 0.00% | 0.00% | 2.27% |
| ASPIRIN | 587 | 100.00% | 0.00% | 0.00% | 0.85% |
| PREDNISONE | 517 | 99.22% | 0.78% | 0.00% | 1.35% |
| CETIRIZINE HYDROCHLORIDE | 504 | 99.40% | 0.60% | 0.00% | 0.20% |
| BUPROPION HYDROCHLORIDE | 502 | 100.00% | 0.00% | 0.00% | 0.80% |
| VENLAFAXINE HYDROCHLORIDE | 481 | 100.00% | 0.00% | 0.00% | 1.46% |
| LISINOPRIL | 474 | 100.00% | 0.00% | 0.00% | 1.48% |
| FAMOTIDINE | 447 | 83.63% | 16.37% | 0.00% | 0.22% |
| LORATADINE | 446 | 96.64% | 3.36% | 0.00% | 0.00% |
| ATORVASTATIN CALCIUM TRIHYDRATE | 446 | 100.00% | 0.00% | 0.00% | 0.22% |
| GUAIFENESIN | 442 | 81.86% | 18.14% | 0.00% | 0.23% |
| QUETIAPINE FUMARATE | 439 | 100.00% | 0.00% | 0.00% | 0.46% |

Active ingredient strings are grouped as written on the label (semicolon-
separated for combination products). This does not consolidate salt forms
or different orderings of the same components.

### 4.6 By Manufacturer (Top 20 by Row Count)

| Manufacturer | n | gluten_free % | unknown % | contains_gluten % | no_data % |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Bryant Ranch Prepack | 4,124 | 99.16% | 0.84% | 0.00% | 2.01% |
| A-S Medication Solutions | 3,418 | 99.28% | 0.72% | 0.00% | 2.34% |
| Proficient Rx LP | 1,533 | 99.67% | 0.33% | 0.00% | 2.28% |
| Physicians Total Care, Inc. | 1,433 | 99.78% | 0.00% | 0.22% | 3.63% |
| NuCare Pharmaceuticals,Inc. | 1,358 | 99.25% | 0.75% | 0.00% | 1.55% |
| REMEDYREPACK INC. | 1,345 | 98.65% | 1.35% | 0.00% | 0.74% |
| Aphena Pharma Solutions - Tennessee, LLC | 1,276 | 99.44% | 0.56% | 0.00% | 1.41% |
| PD-Rx Pharmaceuticals, Inc. | 1,194 | 99.74% | 0.26% | 0.00% | 2.01% |
| Aurobindo Pharma Limited | 967 | 98.62% | 1.38% | 0.00% | 2.48% |
| Preferred Pharmaceuticals Inc. | 728 | 98.61% | 1.39% | 0.00% | 1.37% |
| Rebel Distributors Corp | 675 | 100.00% | 0.00% | 0.00% | 6.22% |
| American Health Packaging | 673 | 100.00% | 0.00% | 0.00% | 0.15% |
| Major Pharmaceuticals | 631 | 97.77% | 2.23% | 0.00% | 0.48% |
| Golden State Medical Supply, Inc. | 619 | 99.02% | 0.98% | 0.00% | 1.13% |
| Direct_Rx | 604 | 100.00% | 0.00% | 0.00% | 0.50% |
| Aidarex Pharmaceuticals LLC | 586 | 100.00% | 0.00% | 0.00% | 3.92% |
| RPK Pharmaceuticals, Inc. | 562 | 100.00% | 0.00% | 0.00% | 7.12% |
| Zydus Lifesciences Limited | 554 | 99.09% | 0.91% | 0.00% | 0.36% |
| Camber Pharmaceuticals, Inc. | 554 | 96.90% | 3.10% | 0.00% | 1.08% |
| State of Florida DOH Central Pharmacy | 551 | 100.00% | 0.00% | 0.00% | 3.81% |

Manufacturer names are grouped as written in the SPL label. Variant spellings
("Acme, Inc." vs "Acme Inc." vs "ACME INC.") appear as separate rows.


## 5. Sources of Uncertainty

### 5.1 Excipients Driving the `unknown` Flag

Every product flagged `unknown` has at least one excipient whose gluten
status cannot be determined from the label (typically a starch derivative
with no botanical source specified). The breakdown below counts each
product once per flagging excipient — a product flagged for two different
unknown excipients is counted in both rows.

| Excipient string | Products flagged | % of unknown products | % of all products |
| :--- | ---: | ---: | ---: |
| `SODIUM STARCH GLYCOLATE TYPE A` | 999 | 97.18% | 1.38% |
| `SODIUM CARBOXYMETHYL STARCH` | 13 | 1.26% | 0.02% |
| `Sodium Starch Glycolate Type A` | 7 | 0.68% | 0.01% |
| `SODIUM STARCH GLYCOLATE TYPE B` | 6 | 0.58% | 0.01% |
| `OAT` | 2 | 0.19% | 0.00% |
| `HYDROGENATED STARCH HYDROLYSATE` | 1 | 0.10% | 0.00% |

Denominator for "% of unknown products" is the total number of products
with `unknown` flag (1,028). Denominator for "% of all
products" is the full dataset (72,358).

### 5.2 Source-Specified vs Source-Unspecified Excipient Use

For the excipient families that drive the `unknown` flag, the table below
counts how often the same excipient family appears with vs without a
specified botanical source across the entire filtered dataset. A high
"% unspecified" value means the excipient is usually declared without a
source grain.

| Excipient family | Total uses | Source-specified | Source-unspecified | % unspecified |
| :--- | ---: | ---: | ---: | ---: |
| `SODIUM STARCH GLYCOLATE TYPE A` | 13,334 | 12,328 | 1,006 | 7.54% |
| `PREGELATINIZED STARCH` | 886 | 886 | 0 | 0.00% |
| `STARCH` (any source or unspecified) | 25,330 | 25,330 | 0 | 0.00% |


## 6. No-Data Products

3,041 products in the dataset list no inactive ingredients on
their DailyMed label. The composition of this group is shown below.

### 6.1 By Dosage Form

| Dosage form | n | % of no_data |
| :--- | ---: | ---: |
| Kit | 1,253 | 41.20% |
| Tablet | 665 | 21.87% |
| Tablet, Film Coated | 259 | 8.52% |
| Capsule | 237 | 7.79% |
| Powder, For Solution | 133 | 4.37% |
| Tablet, Extended Release | 93 | 3.06% |
| Tablet, Effervescent | 40 | 1.32% |
| Granule | 40 | 1.32% |
| Capsule, Extended Release | 33 | 1.09% |
| Solution | 32 | 1.05% |
| Powder, For Suspension | 31 | 1.02% |
| Tablet, Coated | 29 | 0.95% |
| Liquid | 25 | 0.82% |
| Tablet, Delayed Release | 24 | 0.79% |
| Powder | 21 | 0.69% |
| All other forms | 126 | 4.14% |

KIT products are multi-component packages. The KIT-level label typically
does not enumerate excipients — the individual product labels inside the
KIT have their own excipient lists. This structural pattern is the reason
KIT appears at 41.20% of the no_data bucket. See
`analysis/allergens/limitations.md` §Gluten.

### 6.2 Non-KIT No-Data Manufacturers (Top 10 by Row Count)

1,788 non-KIT products have no excipient data on their
label — i.e., the label format does not include an inactive ingredients
section at all.

| Manufacturer | n non-KIT no_data products |
| :--- | ---: |
| Advanced Rx Pharmacy of Tennessee, LLC | 172 |
| Advanced Rx of Tennessee, LLC | 89 |
| Bryant Ranch Prepack | 70 |
| Contract Pharmacy Services-PA | 58 |
| Boehringer Ingelheim Pharmaceuticals, Inc. | 54 |
| A-S Medication Solutions | 51 |
| H.J. Harkins Company, Inc. | 47 |
| Rebel Distributors Corp | 31 |
| Stat Rx USA | 29 |
| Aidarex Pharmaceuticals LLC | 23 |


## 7. Pilot Subset Comparison

The pilot dataset (`data/pilot/gluten_pilot_flagged.csv`, 6,605 products) covered
all DailyMed products containing acetaminophen or ibuprofen as an active
ingredient, with only injectables excluded. The bulk dataset applies a
stricter filter pipeline (`scripts/filter_gluten_fullcatalog.py`) that additionally drops
homeopathic, non-FDA-recognized (`unapproved drug other`, `unapproved
homeopathic`, etc.), and non-swallowed dosage forms (lozenges, films,
orally disintegrating tablets, mouthwashes, pastes, etc.).

Row counts differ because of the stricter filters. Percentages differ
because the bulk dataset excludes dosage forms the pilot kept and because
the validation table used for the bulk dataset has 171 entries vs the
pilot's 48.

| Subset | Pilot n | Pilot unknown+contains_gluten % | Bulk n | Bulk unknown+contains_gluten % |
| :--- | ---: | ---: | ---: | ---: |
| Acetaminophen-containing | 4,986 | 3.4% | 4,834 | 3.19% |
| Ibuprofen-containing | 1,619 | 1.0% | 1,781 | 0.89% |

Pilot percentages are taken from `analysis/allergens/gluten/findings_pilot_gluten.md` § 4.1 and § 4.2.
All percentages exclude `no_data` from the denominator.


## 8. Methodological Reference — Figueiredo et al. (2025)

Figueiredo et al. (2025), "Presence of gluten and soy derived excipients in
medicinal products and their implications on allergen safety and labeling,"
Scientific Reports 15, 10976. https://doi.org/10.1038/s41598-025-95525-6

The Portuguese source study used a binary classification ("gluten-free" vs
"non-gluten-free"). The closest equivalent in this project's four-tier
system is `unknown` + `contains_gluten`. All US percentages below exclude
`no_data` from the denominator.

| Metric | Portugal | Portugal n | US (bulk) | US n |
| :--- | ---: | ---: | ---: | ---: |
| Paracetamol/Acetaminophen — % non-gluten-free | 44.4% | n=108 | 3.19% | n=4,770 |
| Ibuprofen — % non-gluten-free | 8.2% | n=85 | 0.89% | n=1,694 |
| Products with confirmed gluten grains | 0 |  | 12 | n=69,317 |

Methodological differences affecting the comparison:

| Factor | Portugal | US (bulk) |
| :--- | :--- | :--- |
| Sample size | 108 + 85 | See § 7 |
| Database | INFOMED (SmPCs) | DailyMed (SPL labels) |
| Classification system | Binary | Four-tier (gluten_free / unknown / contains_gluten / no_data) |
| Xanthan gum | Non-gluten-free | Gluten-free (per NCA) |
| Filter pipeline | Therapeutic category only | See CLAUDE.md § Bulk Filtering Decisions |
| Unit of analysis | Not specified | NDC |

