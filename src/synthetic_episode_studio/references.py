from __future__ import annotations

from dataclasses import dataclass

from .models import CodeSystem


ACCESSED = "2026-07-18"
ICD_VERSION = "ICD-10 5th Edition 2026"
OPCS_VERSION = "OPCS-4.11 (2026)"


@dataclass(frozen=True)
class CodeReference:
    system: CodeSystem
    version: str
    code: str
    display: str
    scenarios: tuple[str, ...]
    source_url: str
    accessed: str = ACCESSED
    provenance_note: str = "Checked against the NHS England Classifications Browser; limited demonstration subset."


ICD_BASE = "https://classbrowser.nhs.uk/ICD-10-5TH-Edition/vol1/"
OPCS_BASE = "https://classbrowser.nhs.uk/"


REFERENCES: tuple[CodeReference, ...] = (
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "K35.8", "Acute appendicitis, other and unspecified", ("acute-appendicitis",), f"{ICD_BASE}block-k35-k38.htm"),
    CodeReference(CodeSystem.OPCS4, OPCS_VERSION, "H01.1", "Emergency excision of abnormal appendix", ("acute-appendicitis",), OPCS_BASE),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "K80.0", "Calculus of gallbladder with acute cholecystitis", ("acute-cholecystitis",), f"{ICD_BASE}block-k80-k87.htm"),
    CodeReference(CodeSystem.OPCS4, OPCS_VERSION, "J18.3", "Total cholecystectomy NEC", ("acute-cholecystitis",), OPCS_BASE),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "K40.9", "Unilateral or unspecified inguinal hernia, without obstruction or gangrene", ("inguinal-hernia",), f"{ICD_BASE}block-k40-k46.htm"),
    CodeReference(CodeSystem.OPCS4, OPCS_VERSION, "T20.2", "Primary repair of inguinal hernia using insert of prosthetic material", ("inguinal-hernia",), OPCS_BASE),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "K57.3", "Diverticular disease of large intestine without perforation or abscess", ("acute-diverticulitis",), f"{ICD_BASE}block-k55-k64.htm"),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "K61.0", "Anal abscess", ("perianal-abscess",), f"{ICD_BASE}block-k55-k64.htm"),
    CodeReference(CodeSystem.OPCS4, OPCS_VERSION, "H58.2", "Drainage of perianal abscess", ("perianal-abscess",), OPCS_BASE),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "Z38.0", "Singleton, born in hospital", ("healthy-newborn", "neonatal-jaundice", "feeding-difficulty", "neonatal-hypoglycaemia", "infant-diabetic-mother"), f"{ICD_BASE}block-z30-z39.htm"),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "P59.9", "Neonatal jaundice, unspecified", ("neonatal-jaundice",), f"{ICD_BASE}block-p50-p61.htm"),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "P92.5", "Neonatal difficulty in feeding at breast", ("feeding-difficulty",), f"{ICD_BASE}block-p90-p96.htm"),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "P70.4", "Other neonatal hypoglycaemia", ("neonatal-hypoglycaemia",), f"{ICD_BASE}block-p70-p74.htm"),
    CodeReference(CodeSystem.ICD10, ICD_VERSION, "P70.1", "Syndrome of infant of a diabetic mother", ("infant-diabetic-mother",), f"{ICD_BASE}block-p70-p74.htm"),
)

REFERENCE_BY_KEY = {(item.system.value, item.code): item for item in REFERENCES}


def references_for_scenario(scenario_id: str) -> list[CodeReference]:
    return [item for item in REFERENCES if scenario_id in item.scenarios]
