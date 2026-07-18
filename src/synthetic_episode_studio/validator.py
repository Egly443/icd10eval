from __future__ import annotations

from .models import Episode, Track, ValidationCheck, ValidationSummary
from .references import REFERENCE_BY_KEY


def _check(name: str, ok: bool, success: str, failure: str) -> ValidationCheck:
    return ValidationCheck(name=name, status="pass" if ok else "fail", message=success if ok else failure)


def validate_episode(episode: Episode) -> ValidationSummary:
    passage_ids = {
        passage.id
        for document in episode.documents
        for passage in document.passages
    }
    evidence_total = sum(len(code.evidence_passage_ids) for code in episode.codes)
    evidence_valid = sum(
        1
        for code in episode.codes
        for evidence_id in code.evidence_passage_ids
        if evidence_id in passage_ids
    )
    evidence_ok = evidence_total > 0 and evidence_valid == evidence_total
    references_ok = all((code.system, code.code) in REFERENCE_BY_KEY for code in episode.codes)
    chronology_ok = episode.timeline == sorted(episode.timeline, key=lambda event: event.occurred_at)
    baby_ok = (
        episode.patient.gestational_age_weeks is not None
        and "days" in episode.patient.age
        if episode.metadata.track == Track.WELL_BABY
        else episode.patient.gestational_age_weeks is None and "years" in episode.patient.age
    )
    identifiers_ok = (
        episode.patient.synthetic_identifier.startswith("SYN-")
        and episode.patient.display_name.startswith("Synthetic ")
        and episode.metadata.synthetic
    )
    procedure_ok = any(code.system == "OPCS-4" for code in episode.codes) == bool(episode.procedures)

    checks = [
        _check("chronology", chronology_ok, "Timeline is chronological and encounter-bounded.", "Timeline chronology is invalid."),
        _check("reference-library", references_ok, "Every code is in the curated reference subset.", "An emitted code is not in the curated reference subset."),
        _check("evidence-links", evidence_ok, "Every code resolves to supporting passages.", "One or more evidence links do not resolve."),
        _check("track-demographics", baby_ok, "Demographics are plausible for the selected track.", "Demographics conflict with the selected track."),
        _check("synthetic-identifiers", identifiers_ok, "Synthetic-only identifiers and labels are present.", "A synthetic identifier safeguard failed."),
        _check("procedure-consistency", procedure_ok, "Procedure concepts and OPCS-4 assignments agree.", "Procedure concepts and OPCS-4 assignments conflict."),
    ]
    valid = all(item.status == "pass" for item in checks)
    coverage = round((evidence_valid / evidence_total) * 100) if evidence_total else 0
    return ValidationSummary(valid=valid, evidence_coverage_percent=coverage, checks=checks)
