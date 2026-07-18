# Source register

Accessed 18 July 2026. Sources were used to bound plausible synthetic narratives and verify the deliberately small classification subset. No real patient record or reference case was copied.

## Evaluation-data landscape

| Region | Dataset | What it establishes for the business-case comparison |
|---|---|---|
| USA | [MIMIC-IV v3.0 (PhysioNet)](https://physionet.org/content/mimiciv/3.0/) | A reusable credentialed benchmark with 364,627 de-identified patients, hospital/ICU events and ICD billing data |
| USA | [CMS Medicare Claims Synthetic Public Use Files](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) | Publicly downloadable synthetic claims designed for software development and familiarity with CMS formats; CMS cautions against population inference |
| England | [NHS England Artificial Data pilot](https://digital.nhs.uk/services/artificial-data) | Three public artificial HES datasets support pipeline development, teaching and schema familiarity; relationships between fields are not preserved, records can be unrealistic and the files cannot support analysis |
| England | [Hospital Episode Statistics](https://digital.nhs.uk/data-and-information/data-tools-and-services/data-services/hospital-episode-statistics) | National patient-level hospital activity data spanning admitted care, outpatient appointments and emergency attendance; access to record-level extracts is governed |
| UK | [CPRD GOLD December 2024](https://www.cprd.com/doi/cprd-gold-december-2024-dataset) | Longitudinal UK primary-care EHR data with linked sources; anonymised extracts require a licence, study specification and protocol approval |

The page's “fewer ready-made UK benchmarks” statement is an inference from these access models, not a claim that the UK lacks rich health data. These sources are representative examples rather than an exhaustive catalogue. Public aggregate NHS statistics, controlled real-world data and synthetic engineering fixtures serve different evaluation questions and should not be treated as interchangeable.

## Classification and coding sources

| Source | Use in the MVP |
|---|---|
| [NHS England Classifications Browser](https://classbrowser.nhs.uk/) | Current UK classification landing page; ICD-10 5th Edition 2026, OPCS-4.11 and national standards |
| [National Clinical Coding Standards — ICD-10 2026](https://classbrowser.nhs.uk/ref_books/ICD-10_2026_5th_Ed_NCCS.pdf) | Current morbidity coding conventions, including birth-episode use of Z38.0 |
| [National Clinical Coding Standards — OPCS-4 2026](https://classbrowser.nhs.uk/ref_books/OPCS-4.11_NCCS-2026.pdf) | Current procedure coding standards and examples |
| [NHS England clinical classifications overview](https://digital.nhs.uk/services/terminology-and-classifications/clinical-classifications) | Purpose, governance and mandated use of ICD-10 and OPCS-4 |
| [NHS England terminology licences](https://digital.nhs.uk/services/terminology-server/content-licences-agreement) | Reminder that broader terminology integration and redistribution require applicable licence terms |

Every `CodeReference` stores its system, version, code, display label, applicable scenario, source URL, access date and provenance note. The application packages only the 14 entries needed by the demonstration; it does not reproduce a classification manual.

## Clinical pathway sources

| Scenario | Primary guidance used to shape the synthetic pathway |
|---|---|
| Acute appendicitis | [NHS — Appendicitis](https://www.nhs.uk/conditions/appendicitis/) |
| Acute calculous cholecystitis | [NHS — Acute cholecystitis](https://www.nhs.uk/conditions/acute-cholecystitis/) |
| Inguinal hernia | [NHS — Inguinal hernia repair](https://www.nhs.uk/conditions/inguinal-hernia-repair/) |
| Uncomplicated diverticulitis | [NICE NG147 — Diverticular disease](https://www.nice.org.uk/guidance/ng147) |
| Perianal abscess | [NHS — Anal fistula](https://www.nhs.uk/conditions/anal-fistula/) (context only; scenario remains deliberately generic) |
| Healthy newborn | [NHS — Newborn physical examination](https://www.nhs.uk/conditions/baby/newborn-screening/physical-examination/) |
| Neonatal jaundice | [NICE CG98 — Jaundice in newborn babies](https://www.nice.org.uk/guidance/cg98) |
| Breastfeeding difficulty | [NHS Start for Life — Positioning and attachment](https://www.nhs.uk/start-for-life/baby/feeding-your-baby/breastfeeding/how-to-breastfeed/positioning-and-attachment/) |
| Transient neonatal hypoglycaemia | [BAPM — Identification and management of neonatal hypoglycaemia](https://www.bapm.org/resources/identification-and-management-of-neonatal-hypoglycaemia-in-the-full-term-infant-a-framework-for-practice) |
| Infant of a diabetic mother | [NICE NG3 — Diabetes in pregnancy](https://www.nice.org.uk/guidance/ng3) |

## Curated classification subset

| Scenario | ICD-10 5th Edition 2026 | OPCS-4.11 |
|---|---|---|
| Acute appendicitis | K35.8 | H01.1 |
| Acute calculous cholecystitis | K80.0 | J18.3 |
| Inguinal hernia | K40.9 | T20.2 |
| Uncomplicated diverticulitis | K57.3 | — |
| Perianal abscess | K61.0 | H58.2 |
| Healthy newborn | Z38.0 | — |
| Neonatal jaundice | P59.9, Z38.0 | — |
| Breastfeeding difficulty | P92.5, Z38.0 | — |
| Transient neonatal hypoglycaemia | P70.4, Z38.0 | — |
| Infant of a diabetic mother | P70.1, Z38.0 | — |

The subset is demonstration metadata, not a comprehensive code list or an instruction to assign these codes in real care. Assignment depends on complete documentation and current national standards; trained clinical coders must review real episodes.
