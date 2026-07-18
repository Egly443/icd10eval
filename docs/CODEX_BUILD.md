# Codex build record

This is a concise, truthful record of how Codex was used during the autonomous hackathon build. It is not a fabricated transcript.

## Product and architecture decisions

- Read the supplied engineering handbook and judge-scoring image.
- Asked the owner to resolve the main ambiguity: episode generation is the product; model evaluation/scoring is out of scope.
- Defined the target users as AI developers and NHS-facing evaluators of commercial products.
- Chose deterministic template generation for a reliable no-key demo, with a provider protocol for later API integration.
- Designed the interaction around a generated dossier and click-to-highlight code evidence.
- Kept persistence static and local to maximise reliability within the 210-minute constraint.

## Research assistance

- Located the current NHS England Classifications Browser and 2026 national standards.
- Confirmed the target editions as ICD-10 5th Edition 2026 and OPCS-4.11.
- Checked the limited diagnosis/procedure subset and captured source URLs, versions, access dates and provenance.
- Used NHS, NICE and BAPM pages to bound ten plausible synthetic care pathways.
- Applied a deliberate rule: non-procedural episodes have no OPCS-4 assignment rather than a fabricated one.

## Implementation milestones

1. Created typed models, scenario and reference libraries, provider interface, deterministic generator, validator, atomic JSON repository and FastAPI routes.
2. Built the complete browser experience: value proposition, track/scenario/seed controls, staged generation state, dossier, timeline, quality view, code-to-evidence highlighting and export.
3. Generated and committed ten reproducible exemplar episodes plus the JSON Schema.
4. Added generator, contract and API tests across all ten scenarios.
5. Added one-command startup, architecture, sources, limitations, demo script and future provider contract.

## Defects found and repaired

- Initial dependency installation was blocked by sandboxed network access; the approved install path was used and dependencies were pinned.
- Synchronous `TestClient` lifecycle tests stalled in the execution environment. Tests were moved to direct asynchronous ASGI transport, which tests the same routes without an environment-specific portal-thread deadlock.
- File-response streaming invoked the same constrained thread path. The small validated JSON export is now read into a direct response, simplifying local reliability.
- Generated packaging metadata was identified during repository review and removed from version control.

## Verification performed

- Generated all ten scenarios and confirmed every validation summary passes with 100% evidence coverage.
- Validated every exemplar against the exported JSON Schema.
- Tested same-seed identity and safe different-seed variation.
- Tested code/reference membership, evidence resolution, chronology, newborn demographics, procedure consistency and API error handling.
- Ran the full automated suite and obtained 41 passing tests.
- Performed local HTTP smoke checks and presentation-focused UI review before release.

## Commit milestones

- `feat: build synthetic episode vertical slice` — application, ten scenarios, evidence mapping, UI, exemplars, schema and initial tests.
- A final release commit records documentation, polish and verification repairs.
