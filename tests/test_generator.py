from __future__ import annotations

import json

import jsonschema
import pytest

from synthetic_episode_studio.generator import DeterministicTemplateProvider
from synthetic_episode_studio.models import Episode, Track
from synthetic_episode_studio.references import REFERENCE_BY_KEY
from synthetic_episode_studio.scenarios import SCENARIOS


@pytest.fixture(scope="module")
def provider() -> DeterministicTemplateProvider:
    return DeterministicTemplateProvider()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
def test_all_scenarios_validate(scenario, provider) -> None:
    episode = provider.generate(scenario.id, 2026)
    assert episode.validation is not None
    assert episode.validation.valid
    assert episode.validation.evidence_coverage_percent == 100
    jsonschema.validate(
        instance=json.loads(episode.model_dump_json()),
        schema=Episode.model_json_schema(),
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
def test_codes_are_curated_and_evidence_resolves(scenario, provider) -> None:
    episode = provider.generate(scenario.id, 77)
    passages = {passage.id for document in episode.documents for passage in document.passages}
    for code in episode.codes:
        assert (code.system, code.code) in REFERENCE_BY_KEY
        assert code.evidence_passage_ids
        assert set(code.evidence_passage_ids) <= passages


def test_same_seed_is_identical(provider) -> None:
    first = provider.generate("acute-appendicitis", 101)
    second = provider.generate("acute-appendicitis", 101)
    assert first == second


def test_different_seed_changes_safe_fields_not_contract(provider) -> None:
    first = provider.generate("acute-appendicitis", 101)
    second = provider.generate("acute-appendicitis", 102)
    assert first.metadata.episode_id != second.metadata.episode_id
    assert first.encounter.admission_at != second.encounter.admission_at
    assert [(item.system, item.code) for item in first.codes] == [
        (item.system, item.code) for item in second.codes
    ]
    assert first.validation and first.validation.valid
    assert second.validation and second.validation.valid


@pytest.mark.parametrize("scenario", [item for item in SCENARIOS if item.track == Track.WELL_BABY], ids=lambda scenario: scenario.id)
def test_well_baby_demographics_and_no_fabricated_opcs(scenario, provider) -> None:
    episode = provider.generate(scenario.id, 55)
    assert episode.patient.gestational_age_weeks in range(38, 42)
    assert episode.patient.birth_weight_grams is not None
    assert "days" in episode.patient.age
    assert not episode.procedures
    assert all(code.system != "OPCS-4" for code in episode.codes)


def test_timeline_is_chronological_and_bounded(provider) -> None:
    episode = provider.generate("acute-diverticulitis", 55)
    timestamps = [event.occurred_at for event in episode.timeline]
    assert timestamps == sorted(timestamps)
    assert episode.encounter.admission_at <= timestamps[0]
    assert timestamps[-1] <= episode.encounter.discharge_at
