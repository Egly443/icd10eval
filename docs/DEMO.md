# Two-minute demo

## Before presenting

1. Run `./scripts/start.sh` and open `http://127.0.0.1:8000`.
2. Keep the window at desktop width and the page at the top.
3. Confirm the API status at `/health` if the venue connection is uncertain.

## Script

**0:00–0:20 — Problem and buyer**

“Commercial clinical-coding products need realistic episodes for evaluation, but patient records are difficult and risky to access. Synthetic Episode Studio creates consistent evaluation inputs without exposing patient data.”

Point out the three permanent safety labels and the deterministic, evidence-linked and schema-valid product promises.

**0:20–0:42 — Generate**

Select **Run the 90-sec demo**. It chooses General Surgery → Acute appendicitis → seed 2026 and starts generation.

“The studio uses a curated pathway and a seed, so this exact record can be reproduced by every evaluator. There is no API key or runtime model dependency in this MVP.”

**0:42–1:12 — Show the dossier**

When the dossier appears, point to the synthetic identifier, scenario, dates and green validation status. Briefly scan the encounter summary and structured documents.

“This is more than plausible prose. It is a typed episode with chronology, documents, diagnoses, procedures and provenance.”

**1:12–1:35 — The wow interaction**

Select **K35.8** and then **H01.1** in the classification panel.

“Every expected classification resolves to the exact passages that support it. Evaluation teams can inspect why an expected output exists instead of trusting an opaque answer key.”

Show the green evidence highlights in the assessment, imaging and operative record.

**1:35–1:52 — Quality and export**

Select **Quality & provenance**, mention six automated gates and 100% evidence coverage, then return to the dossier and select **Export JSON**.

“The result is ready for a downstream evaluation harness. The same schema covers both General Surgery and Well Baby.”

**1:52–2:00 — Close**

“Today, this creates safe, traceable inputs. Next, the provider seam can add API-driven variation while the same validation contract protects quality.”

## If time is cut

Use the first 20 seconds, generate the default episode, click one classification to highlight evidence, and close on JSON export. That communicates usefulness, execution and traceability in under one minute.
