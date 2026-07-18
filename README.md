# Synthetic Episode Studio

Public demo: [egly443.github.io/icd10eval](https://egly443.github.io/icd10eval/)

Create consistent, traceable, export-ready synthetic NHS-style clinical episodes without exposing patient data.

Synthetic Episode Studio is a hackathon MVP for AI developers and NHS-facing evaluation teams assessing commercial clinical-coding products. It creates repeatable evaluation inputs—not scores—from ten curated General Surgery and Well Baby pathways. Each output is schema-valid, carries explicit generation provenance, and links every expected ICD-10 or OPCS-4 classification to the passages that support it.

> **Safety:** All records are synthetic demonstration data. They are not clinically validated, are not for patient care, and are not endorsed by the NHS.

## The 90-second journey

1. Choose **General Surgery** or **Well Baby**.
2. Select a scenario, or let the studio choose one.
3. Set a seed and generate a repeatable episode.
4. Inspect its clinical dossier, timeline, quality gates and classification output.
5. Select a code to highlight its supporting record passages.
6. Export the complete validated record as JSON.

## Start with one command

Prerequisites: Python 3.12 and internet access for the first dependency installation.

```bash
./scripts/start.sh
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The startup script creates `.venv`, installs the application if required, and launches Uvicorn. Set a different port with `PORT=8080 ./scripts/start.sh`.

For the presentation-ready path, select **Run the 90-sec demo**. It generates Acute appendicitis with seed `2026`.

## What is included

- Ten deterministic, curated scenario definitions and ten committed exemplar JSON episodes.
- Seeded demographic, date and safe narrative variation.
- FastAPI generation, retrieval, download, catalogue and health routes.
- Pydantic models plus an exported JSON Schema.
- Validation for chronology, track-appropriate demographics, reference membership, evidence integrity, synthetic identifiers and procedure consistency.
- Static JSON persistence in `episodes/generated/`.
- Responsive Jinja/HTML/CSS/JavaScript interface with evidence highlighting.
- A provider protocol ready for a future OpenAI-backed implementation.
- 41 automated tests covering all ten pathways and the public API.

## Clinical scope

| Track | Curated pathways |
|---|---|
| General Surgery | Acute appendicitis, acute calculous cholecystitis, inguinal hernia, uncomplicated acute diverticulitis, perianal abscess |
| Well Baby | Healthy term newborn, neonatal jaundice, breastfeeding difficulty, transient neonatal hypoglycaemia, infant of a diabetic mother |

The deliberately small reference subset targets **ICD-10 5th Edition 2026** and **OPCS-4.11 (2026)**. A non-procedural episode has an empty OPCS-4 list and an explicit explanation; the generator never creates a procedure code merely to fill a field.

## API

Interactive documentation is available at `/docs` while the app is running.

```bash
curl -X POST http://127.0.0.1:8000/api/episodes \
  -H 'content-type: application/json' \
  -d '{"scenario_id":"acute-appendicitis","seed":2026}'
```

| Route | Purpose |
|---|---|
| `GET /health` | Startup/readiness check |
| `GET /api/scenarios` | Ten-scenario catalogue |
| `POST /api/episodes` | Generate, validate and persist an episode |
| `GET /api/episodes/{episode_id}` | Retrieve a generated episode |
| `GET /api/episodes/{episode_id}/download` | Download validated JSON |
| `GET /api/benchmark` | Latest EPICODE-Bench Mini leaderboard data |

## EPICODE-Bench Mini

Open [http://127.0.0.1:8000/epicode-bench](http://127.0.0.1:8000/epicode-bench) for the SWE-bench-style leaderboard. The benchmark contains one fixed-seed case for each of the ten pathways. Models receive clinical passages and a closed 14-code ICD-10/OPCS-4 codebook; diagnoses, expected codes, rationales and other label-bearing fields are withheld.

The headline **Episode Resolved** metric requires both the exact classification set and exact supporting-passage set. Secondary metrics report micro code F1, micro evidence F1, hallucinated-code rate, latency and token use.

```bash
# Rebuild the committed ten-case dataset
.venv/bin/python -m synthetic_episode_studio.benchmark generate

# Run the official frontier-vs-cost-sensitive comparison (20 API requests)
export OPENAI_API_KEY="..."
.venv/bin/python -m synthetic_episode_studio.benchmark run
```

The default contenders are `gpt-5.6-sol` and `gpt-5.6-luna`, with identical prompts. Sol runs with `xhigh` reasoning effort; Luna remains at `low`. The private detailed report is written to `benchmark/results/latest.json`, while the summary-only public report is written to `benchmark/results/public.json`. API use incurs charges; do not commit API keys.

## Rebuild and verify

```bash
.venv/bin/python scripts/build_exemplars.py
.venv/bin/python scripts/build_static_site.py
.venv/bin/pytest
```

Expected result: `41 passed`. The exemplar build also refreshes [the JSON Schema](schemas/episode.schema.json).

## Repository map

```text
src/synthetic_episode_studio/  Application, templates and static assets
episodes/exemplars/            Ten committed demonstration records
episodes/generated/            Runtime JSON persistence (ignored by Git)
schemas/                        Exported episode JSON Schema
tests/                          Generator, validation and API tests
docs/                           Architecture, sources, demo and Codex record
prompts/                        Future API-provider contract
scripts/                        Startup and exemplar build commands
```

## Design and limitations

The current provider uses reviewed templates rather than a runtime model. This makes the demo reliable, offline after setup and exactly repeatable. The provider boundary is intentionally small so a later OpenAI integration can produce candidate content before the same validation layer accepts or rejects it.

This MVP is not a coding engine, clinical decision-support system, certified reference implementation or substitute for trained clinical coders. Its classification subset is intentionally incomplete. Clinical narratives are plausible synthetic demonstrations rather than validated reference cases. Before any commercial or NHS use, obtain the appropriate terminology licences, governance approval, clinical review and independent validation.

Further detail:

- [Architecture and extension points](docs/ARCHITECTURE.md)
- [Authoritative source register](docs/SOURCES.md)
- [Two-minute demo script](docs/DEMO.md)
- [Truthful Codex build record](docs/CODEX_BUILD.md)
- [Judge-focused self-review](docs/SELF_REVIEW.md)
