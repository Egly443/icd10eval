from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Track(StrEnum):
    GENERAL_SURGERY = "general-surgery"
    WELL_BABY = "well-baby"


class CodeSystem(StrEnum):
    ICD10 = "ICD-10"
    OPCS4 = "OPCS-4"


class EpisodeMetadata(BaseModel):
    episode_id: str
    scenario_id: str
    track: Track
    seed: int = Field(ge=0, le=999_999_999)
    synthetic: bool = True
    generated_at: datetime
    generator: str = "deterministic-template-v1"
    classification_versions: dict[str, str]
    intended_use: str = "AI product evaluation and demonstration"


class Patient(BaseModel):
    synthetic_identifier: str
    display_name: str
    age: str
    sex: str
    gestational_age_weeks: int | None = Field(default=None, ge=22, le=44)
    birth_weight_grams: int | None = Field(default=None, ge=300, le=6000)


class Encounter(BaseModel):
    admission_at: datetime
    discharge_at: datetime
    specialty: str
    care_setting: str
    discharge_destination: str


class TimelineEvent(BaseModel):
    occurred_at: datetime
    title: str
    detail: str
    status: str


class Passage(BaseModel):
    id: str
    text: str


class ClinicalDocument(BaseModel):
    id: str
    document_type: str
    title: str
    authored_at: datetime
    author_role: str
    passages: list[Passage]


class ClinicalConcept(BaseModel):
    name: str
    category: str
    status: str = "confirmed"


class CodeAssignment(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    system: CodeSystem
    version: str
    code: str
    display: str
    rationale: str
    evidence_passage_ids: list[str] = Field(min_length=1)
    source_url: str


class ValidationCheck(BaseModel):
    name: str
    status: str
    message: str


class ValidationSummary(BaseModel):
    valid: bool
    evidence_coverage_percent: int = Field(ge=0, le=100)
    checks: list[ValidationCheck]


class Episode(BaseModel):
    schema_version: str = "1.0.0"
    metadata: EpisodeMetadata
    patient: Patient
    encounter: Encounter
    encounter_summary: str
    timeline: list[TimelineEvent]
    documents: list[ClinicalDocument]
    diagnoses: list[ClinicalConcept]
    procedures: list[ClinicalConcept]
    procedure_note: str
    codes: list[CodeAssignment]
    validation: ValidationSummary | None = None
    safety_notice: str = "Synthetic demonstration data. Not clinically validated and not for patient care."

    @model_validator(mode="after")
    def chronology_is_valid(self) -> "Episode":
        if self.encounter.discharge_at < self.encounter.admission_at:
            raise ValueError("Discharge cannot precede admission")
        if any(
            event.occurred_at < self.encounter.admission_at
            or event.occurred_at > self.encounter.discharge_at
            for event in self.timeline
        ):
            raise ValueError("Timeline event falls outside the encounter")
        if self.timeline != sorted(self.timeline, key=lambda event: event.occurred_at):
            raise ValueError("Timeline must be chronological")
        return self


class GenerateRequest(BaseModel):
    scenario_id: str
    seed: int = Field(default=42, ge=0, le=999_999_999)
