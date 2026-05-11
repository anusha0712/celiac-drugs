# Hidden Drug Allergens in US Drug Labels — Narrative Draft

*Working draft for the journalism piece covering four allergen families
(gluten, milk, PEG, carmine) in FDA-regulated drug labels. Findings and
citations in this draft reference the per-allergen `findings_*.md` docs
and the primary-source URLs inline below.*

---

## Framing — three-layer regulatory gap

Every allergen in this series sits under the same structural gap:

1. **Class rule.** No FDA rule mandates allergen-specific warning text
   for these excipients in drug labels. 21 CFR 201.100 and 21 CFR 201.66
   require inactive-ingredient disclosure only. The two allergens FDA
   DOES mandate warnings for — sulfites (21 CFR 201.22) and FD&C Yellow
   No. 5 (21 CFR 201.20) — establish the comparison point.
2. **Product inconsistency.** Where voluntary warnings exist (Advair
   Diskus family for milk; PEG 3350 Rx bowel preps), some equivalent
   generics carry the warning and others do not. No rule mandates
   consistency across ANDA-equivalent products.
3. **Silent listing.** Under allergy-context-anchored warning patterns
   (see `methodology.md` §5), every catalog-wide count of drug labels
   whose warning sections discuss the flagged allergen's allergic
   reactions is orders of magnitude smaller than the count that lists
   the allergen in the inactive ingredients — see each allergen's
   numbers below.

---

## Gluten

Source study: Figueiredo A et al. 2025, Sci Rep 15:10976
(https://pubmed.ncbi.nlm.nih.gov/40307426/). Replicated on DailyMed.

The FDA defines wheat, rye, and barley as gluten-containing grains
(21 CFR 101.91, a food-labeling rule). FDA guidance CPG 578.100
permits unqualified "starch" on US labels to mean corn starch; the
regulation is directed at manufacturers, not patients reading
medication bottles. In the gluten pilot's 6,605 acetaminophen and
ibuprofen products, 92.8% of the `unknown` tier was driven by a
single excipient — SODIUM STARCH GLYCOLATE TYPE A — whose label
listing does not specify the starch source.

See `findings_fullcatalog_gluten.md` for the gluten headline numbers
(pending absorption into this folder by Task #17 reorg).

---

## Milk proteins and lactose

Harm anchor: Nowak-Wegrzyn et al. 2004
(https://pubmed.ncbi.nlm.nih.gov/15007361/) — anaphylaxis in milk-
allergic patients from Advair Diskus DPI. FALCPA (2004) excludes drug
labels from its milk-allergen disclosure mandate.

Of 19 DPI set_ids identified under the strict DPI filter (POWDER /
INHALANT METERED + respiratory; pMDIs excluded), 18 carry a Section 4
milk-protein contraindication (Advair Diskus family, Wixela Inhub
family). 1 is silent (Afrezza, an inhaled insulin that does not use
lactose carrier). Spiriva HandiHaler is documented as a known miss in
`limitations.md` — DailyMed classifies it as CAPSULE/ORAL and so it
falls outside the DPI filter, despite its lactose-carrier mechanism.

Across the broader oral catalog (post-baseline filter), 36 products
list a FARE-defined milk-derived excipient under the revised
validation table (lactose family + lactulose removed 2026-05-05 per
pharmacist review). None carry milk-protein allergy language. Under
the gluten-methodology filter (ORAL only, FDA-recognized, swallowed)
for parity with gluten findings, 36 of 69,137 products contain milk
(0.05%).

See `findings_milk.md`.

---

## Polyethylene glycol (PEG)

Harm anchor: Stone CA Jr et al. 2019
(https://pubmed.ncbi.nlm.nih.gov/30557713/) — two PEG 3350 anaphylaxis
index cases, 53 FAERS reports. Reker et al. 2019
(https://pubmed.ncbi.nlm.nih.gov/30867323/) quantified PEG in 36.03% of
42,052 oral solid formulations.

Under the tight-scope flag (unconjugated PEG polymer only: POLYETHYLENE
GLYCOL, POLYETHYLENE OXIDE, MACROGOL, CARBOWAX) and the post-baseline
catalog, 23,834 of 64,123 oral solid tablets/capsules/granules/pellets
(38.06% excluding products with no excipient data, ODT-excluded) list
a PEG excipient. Of 16,450 unique set_ids in this slice, 16,293 had
parseable warning-relevant sections (Rx + OTC Drug Facts). None carry
PEG-allergy language in any warning section under the allergy-context-
anchored pattern rule (`methodology.md` §5). 157 set_ids had no
warning-relevant sections at all. Under the gluten-methodology filter
for parity with gluten findings, 24,556 of 69,137 products contain PEG
(35.52%).

Adjacent excipient families (polysorbates, poloxamers, polyoxyl
derivatives including Cremophor, mPEG, PEG-N surfactants, TPGS,
Kollicoat IR) are out of the tight scope and documented separately in
`methodology.md` §3.6. Reker 2019 treats PEG and poloxamer as distinct
Table 1 categories; this analysis follows that convention.

See `findings_peg.md`.

---

## Carmine / cochineal

Harm anchor: Greenhawt M et al. 2009
(https://pubmed.ncbi.nlm.nih.gov/19331724/) — only US-published
medication-induced carmine anaphylaxis case, generic azithromycin
tablet with pink carmine coating. Greenhawt subsequently worked with
FDA on the 2009 food-labeling rule.

21 CFR 73.100 (food) requires "cochineal extract" or "carmine"
declaration on ingredient statements. 21 CFR 73.1100 (drug) does not
impose an analogous drug-label requirement. FDA stated in the 2009
final rule that drugs would be addressed in a separate rulemaking. No
separate drug rulemaking has been issued in the 17 years since
(Federal Register and FDA.gov search through April 2026).

161 post-baseline US drug products in the April 2026 catalog list
carmine / cochineal / carminic acid as an excipient. Of 141 unique
set_ids, 138 had parseable warning-relevant sections (Rx + OTC Drug
Facts). Zero carry Section 4 contraindication, boxed warning,
Section 5 warning, OTC allergy-alert, do-not-use, or ask-doctor
language for carmine. 100% are silent. Under the gluten-methodology
filter for parity, 130 of 69,137 products contain carmine (0.19%).

Of 350 azithromycin-containing products in the post-baseline catalog,
8 carry carmine — all 8 are generic (ANDA) formulations. This is the
same exposure path that produced the Greenhawt 2009 anaphylaxis case,
17 years later.

See `findings_carmine.md`.

---

## Pending manual-review items before publication

- Pharmacist spot-check of milk, PEG, and carmine validation tables.
  FDA IID cross-reference was completed using a locally downloaded
  FDA-IID-recent-update.csv; pharmacist review remains a separate
  manual audit.
- Manual spot-check of regulations.gov docket FDA-1998-P-0032 for any
  post-2009 drug-carmine filings (regulations.gov 403'd programmatic
  access).
- Journalist-side verification of BBC coverage gap claim (Anthropic
  crawler is blocked by BBC domains; prior session could not confirm).
