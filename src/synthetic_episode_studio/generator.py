from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Protocol

from .models import (
    ClinicalConcept,
    ClinicalDocument,
    CodeAssignment,
    Encounter,
    Episode,
    EpisodeMetadata,
    Passage,
    Patient,
    TimelineEvent,
    Track,
)
from .references import ICD_VERSION, OPCS_VERSION, REFERENCE_BY_KEY
from .scenarios import SCENARIO_BY_ID, Scenario
from .validator import validate_episode


class EpisodeProvider(Protocol):
    """Provider seam for deterministic generation now and an API provider later."""

    def generate(self, scenario_id: str, seed: int) -> Episode: ...


class DeterministicTemplateProvider:
    adult_sexes = ("Female", "Male")
    baby_sexes = ("Female", "Male")

    def generate(self, scenario_id: str, seed: int) -> Episode:
        if scenario_id not in SCENARIO_BY_ID:
            raise KeyError(f"Unknown scenario: {scenario_id}")

        scenario = SCENARIO_BY_ID[scenario_id]
        rng = random.Random(seed)
        admission = datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc) + timedelta(
            days=seed % 24,
            hours=rng.randint(0, 8),
            minutes=rng.choice((0, 10, 20, 30, 40, 50)),
        )
        duration_hours = rng.randint(24, 52) if scenario.track == Track.GENERAL_SURGERY else rng.randint(24, 38)
        discharge = admission + timedelta(hours=duration_hours)

        patient = self._patient(scenario, seed, rng)
        documents = self._documents(scenario, admission, discharge, rng)
        timeline = self._timeline(scenario, admission, discharge)
        codes = self._codes(scenario)

        episode = Episode(
            metadata=EpisodeMetadata(
                episode_id=f"SES-{scenario.track.value[:2].upper()}-{scenario.id.upper()}-{seed:06d}",
                scenario_id=scenario.id,
                track=scenario.track,
                seed=seed,
                generated_at=discharge + timedelta(minutes=5),
                classification_versions={"ICD-10": ICD_VERSION, "OPCS-4": OPCS_VERSION},
            ),
            patient=patient,
            encounter=Encounter(
                admission_at=admission,
                discharge_at=discharge,
                specialty="General Surgery" if scenario.track == Track.GENERAL_SURGERY else "Neonatal care",
                care_setting="Synthetic NHS-style inpatient episode",
                discharge_destination="Usual place of residence with safety-net advice",
            ),
            encounter_summary=(
                f"{scenario.title}: {scenario.presentation} "
                f"{scenario.treatment} {scenario.outcome}"
            ),
            timeline=timeline,
            documents=documents,
            diagnoses=[ClinicalConcept(name=scenario.diagnosis, category="primary diagnosis")],
            procedures=(
                [ClinicalConcept(name=scenario.procedure, category="principal procedure")]
                if scenario.procedure
                else []
            ),
            procedure_note=(
                "A classified intervention is documented for this episode."
                if scenario.procedure
                else "No classifiable OPCS-4 intervention is documented; no procedure code has been fabricated."
            ),
            codes=codes,
        )
        return episode.model_copy(update={"validation": validate_episode(episode)})

    def _patient(self, scenario: Scenario, seed: int, rng: random.Random) -> Patient:
        if scenario.track == Track.WELL_BABY:
            gestation = rng.choice((38, 39, 40, 41))
            weight = rng.randrange(2850, 4210, 10)
            return Patient(
                synthetic_identifier=f"SYN-BABY-{seed:06d}",
                display_name=f"Synthetic newborn {seed % 1000:03d}",
                age=f"{rng.randint(0, 2)} days",
                sex=rng.choice(self.baby_sexes),
                gestational_age_weeks=gestation,
                birth_weight_grams=weight,
            )
        age = rng.randint(22, 77)
        return Patient(
            synthetic_identifier=f"SYN-ADULT-{seed:06d}",
            display_name=f"Synthetic adult {seed % 1000:03d}",
            age=f"{age} years",
            sex=rng.choice(self.adult_sexes),
        )

    def _documents(
        self,
        scenario: Scenario,
        admission: datetime,
        discharge: datetime,
        rng: random.Random,
    ) -> list[ClinicalDocument]:
        documents: list[ClinicalDocument] = []
        if scenario.track == Track.WELL_BABY:
            documents.append(
                ClinicalDocument(
                    id="birth-record",
                    document_type="Birth record",
                    title="Synthetic birth summary",
                    authored_at=admission,
                    author_role="Midwife",
                    passages=[Passage(id="birth-summary", text="Live singleton born in hospital at term and admitted to the postnatal ward for newborn care.")],
                )
            )

        documents.extend(
            [
                ClinicalDocument(
                    id="admission-assessment",
                    document_type="Admission note",
                    title="Initial clinical assessment",
                    authored_at=admission + timedelta(hours=1),
                    author_role="Specialty clinician",
                    passages=[
                        Passage(id="presentation-history", text=scenario.presentation),
                        Passage(id="assessment-examination", text=scenario.examination),
                        Passage(id="assessment-diagnosis", text=f"Clinical impression: {scenario.diagnosis}."),
                    ],
                ),
                ClinicalDocument(
                    id="investigation-review",
                    document_type="Results review",
                    title="Investigation and observation review",
                    authored_at=admission + timedelta(hours=4),
                    author_role="Reviewing clinician",
                    passages=[Passage(id="imaging-result", text=scenario.investigation)],
                ),
            ]
        )

        if scenario.procedure:
            documents.append(
                ClinicalDocument(
                    id="operative-record",
                    document_type="Procedure record",
                    title="Synthetic operative note",
                    authored_at=admission + timedelta(hours=8),
                    author_role="Operating surgeon",
                    passages=[
                        Passage(id="operation-procedure", text=f"Procedure completed: {scenario.procedure}. No immediate complication documented."),
                        Passage(id="operation-plan", text=scenario.treatment),
                    ],
                )
            )
        else:
            documents.append(
                ClinicalDocument(
                    id="management-plan",
                    document_type="Care plan",
                    title="Management plan",
                    authored_at=admission + timedelta(hours=8),
                    author_role="Multidisciplinary team",
                    passages=[Passage(id="management-plan-text", text=scenario.treatment)],
                )
            )

        documents.append(
            ClinicalDocument(
                id="discharge-summary",
                document_type="Discharge summary",
                title="Discharge and safety-net summary",
                authored_at=discharge - timedelta(hours=1),
                author_role="Discharging clinician",
                passages=[
                    Passage(id="discharge-outcome", text=scenario.outcome),
                    Passage(id="discharge-safety", text=f"Synthetic record only. Review trigger reference {rng.randint(100, 999)}; not for patient care."),
                ],
            )
        )
        return documents

    def _timeline(self, scenario: Scenario, admission: datetime, discharge: datetime) -> list[TimelineEvent]:
        middle_title = "Procedure completed" if scenario.procedure else "Care plan reviewed"
        middle_detail = scenario.procedure or scenario.treatment
        return [
            TimelineEvent(occurred_at=admission, title="Episode opened", detail=scenario.presentation, status="admitted"),
            TimelineEvent(occurred_at=admission + timedelta(hours=4), title="Assessment complete", detail=scenario.investigation, status="reviewed"),
            TimelineEvent(occurred_at=admission + timedelta(hours=8), title=middle_title, detail=middle_detail, status="complete"),
            TimelineEvent(occurred_at=discharge, title="Discharged", detail=scenario.outcome, status="complete"),
        ]

    def _codes(self, scenario: Scenario) -> list[CodeAssignment]:
        assignments: list[CodeAssignment] = []
        for code, evidence_ids in scenario.code_evidence.items():
            system = "OPCS-4" if code[0] in {"H", "J", "T", "Y", "Z"} and code != "Z38.0" else "ICD-10"
            reference = REFERENCE_BY_KEY[(system, code)]
            rationale = (
                f"The documented procedure supports {reference.code} ({reference.display})."
                if system == "OPCS-4"
                else f"The episode documentation supports {reference.code} ({reference.display})."
            )
            assignments.append(
                CodeAssignment(
                    system=reference.system,
                    version=reference.version,
                    code=reference.code,
                    display=reference.display,
                    rationale=rationale,
                    evidence_passage_ids=list(evidence_ids),
                    source_url=reference.source_url,
                )
            )
        return assignments
