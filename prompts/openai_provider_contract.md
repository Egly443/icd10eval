# Future OpenAI provider contract

This file defines the boundary for a future runtime generation provider; it is not active in the MVP.

## System intent

Generate only fictional NHS-style clinical episode content for AI-product evaluation. Never produce or infer a real person's information. Never claim that output is clinically validated or suitable for patient care.

## Inputs

- Selected `scenario_id` from the curated catalogue.
- Numeric seed and permitted variation constraints.
- Episode JSON Schema.
- Approved, versioned reference subset.
- Evidence-link requirement.

## Output constraints

- Return one JSON object and no surrounding prose.
- Conform exactly to the current Episode JSON Schema.
- Use synthetic identifiers and labels only.
- Keep chronology internally consistent and inside the encounter.
- Emit only codes from the supplied reference subset.
- Link every code to one or more passage IDs containing explicit support.
- Leave procedures and OPCS-4 assignments empty when no classifiable procedure is documented.
- Preserve all safety and provenance fields.

## Acceptance pipeline

Candidate output must be parsed as the typed `Episode` model and run through the same validator as the deterministic provider. Failure triggers bounded retry or deterministic fallback; invalid output is never persisted or shown as successful.
