from __future__ import annotations

from dataclasses import dataclass

from .models import Track


@dataclass(frozen=True)
class Scenario:
    id: str
    track: Track
    title: str
    short_label: str
    diagnosis: str
    presentation: str
    examination: str
    investigation: str
    treatment: str
    outcome: str
    procedure: str | None
    code_evidence: dict[str, tuple[str, ...]]
    clinical_source_url: str


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("acute-appendicitis", Track.GENERAL_SURGERY, "Acute appendicitis", "Appendicitis", "Acute appendicitis without peritonitis", "A 24-hour history of central abdominal pain migrating to the right iliac fossa, anorexia and nausea.", "Focal right iliac fossa tenderness with guarding; NEWS2 remains low risk.", "Raised inflammatory markers and ultrasound appearances consistent with uncomplicated acute appendicitis.", "Emergency appendicectomy following antibiotics, analgesia and shared consent.", "Mobilising, tolerating diet and discharged with safety-net advice.", "Emergency appendicectomy", {"K35.8": ("assessment-diagnosis", "imaging-result"), "H01.1": ("operation-procedure",)}, "https://www.nhs.uk/conditions/appendicitis/"),
    Scenario("acute-cholecystitis", Track.GENERAL_SURGERY, "Acute calculous cholecystitis", "Cholecystitis", "Gallbladder calculus with acute cholecystitis", "Persistent right upper-quadrant pain, fever and vomiting beginning after an evening meal.", "Right upper-quadrant tenderness and a positive Murphy sign without jaundice.", "Ultrasound shows gallstones, gallbladder wall thickening and pericholecystic fluid.", "Antibiotics and total cholecystectomy after surgical review and consent.", "Pain controlled, oral intake restored and discharge advice understood.", "Total cholecystectomy", {"K80.0": ("assessment-diagnosis", "imaging-result"), "J18.3": ("operation-procedure",)}, "https://www.nhs.uk/conditions/acute-cholecystitis/"),
    Scenario("inguinal-hernia", Track.GENERAL_SURGERY, "Symptomatic inguinal hernia", "Inguinal hernia", "Unilateral inguinal hernia without obstruction or gangrene", "An intermittently uncomfortable groin swelling that reduces when supine, with no vomiting or obstructive symptoms.", "A reducible unilateral inguinal swelling with a cough impulse; abdomen soft and non-distended.", "Clinical assessment confirms a reducible inguinal hernia without obstruction or gangrene.", "Elective primary mesh repair after discussion of benefits, risks and alternatives.", "Comfortable after repair, passing urine and discharged with wound and activity advice.", "Primary mesh repair of inguinal hernia", {"K40.9": ("assessment-diagnosis",), "T20.2": ("operation-procedure",)}, "https://www.nhs.uk/conditions/inguinal-hernia-repair/"),
    Scenario("acute-diverticulitis", Track.GENERAL_SURGERY, "Uncomplicated acute diverticulitis", "Diverticulitis", "Diverticular disease of large intestine without perforation or abscess", "Two days of constant left lower-quadrant pain, altered bowel habit and low-grade fever.", "Localised left lower-quadrant tenderness without generalised guarding or haemodynamic compromise.", "CT demonstrates sigmoid diverticular inflammation without perforation, collection or abscess.", "Conservative management with fluids, analgesia, diet progression and observation.", "Symptoms and inflammatory markers improve; outpatient follow-up and safety-netting arranged.", None, {"K57.3": ("assessment-diagnosis", "imaging-result")}, "https://www.nice.org.uk/guidance/ng147"),
    Scenario("perianal-abscess", Track.GENERAL_SURGERY, "Perianal abscess", "Perianal abscess", "Perianal abscess", "Progressive perianal pain and swelling with fever, making sitting uncomfortable.", "Tender fluctuant perianal swelling with surrounding erythema and no systemic instability.", "Surgical examination confirms a drainable perianal collection; no further imaging required.", "Examination under anaesthesia and drainage of the perianal abscess.", "Pain improved after drainage; wound care and recurrence safety-net advice provided.", "Drainage of perianal abscess", {"K61.0": ("assessment-diagnosis",), "H58.2": ("operation-procedure",)}, "https://www.nhs.uk/conditions/anal-fistula/"),
    Scenario("healthy-newborn", Track.WELL_BABY, "Healthy term newborn", "Healthy newborn", "Singleton born in hospital", "Term singleton born in hospital following an uncomplicated labour, admitted for routine newborn care.", "Normal cardiorespiratory transition, tone, temperature and newborn examination.", "Routine observations and newborn physical examination are reassuring.", "Skin-to-skin contact, feeding support, vitamin K and routine newborn care.", "Feeding established with normal observations; discharged with routine safety-net advice.", None, {"Z38.0": ("birth-summary", "assessment-diagnosis")}, "https://www.nhs.uk/conditions/baby/newborn-screening/physical-examination/"),
    Scenario("neonatal-jaundice", Track.WELL_BABY, "Neonatal jaundice", "Jaundice", "Neonatal jaundice", "A term newborn develops visible jaundice during the birth admission while remaining alert and feeding.", "Visible jaundice with normal hydration, tone and cardiorespiratory observations.", "Bilirubin assessment confirms neonatal jaundice; observations remain below escalation thresholds in this synthetic pathway.", "Feeding support, bilirubin monitoring and safety-net education for caregivers.", "Bilirubin trend and feeding are satisfactory for discharge with planned follow-up.", None, {"P59.9": ("assessment-diagnosis", "imaging-result"), "Z38.0": ("birth-summary",)}, "https://www.nice.org.uk/guidance/cg98"),
    Scenario("feeding-difficulty", Track.WELL_BABY, "Breastfeeding difficulty", "Feeding support", "Neonatal difficulty in feeding at breast", "A term newborn has difficulty sustaining attachment at the breast during the birth admission.", "Clinically well newborn with normal observations, hydration and oral examination.", "Observed feed identifies shallow attachment and ineffective transfer without another acute illness.", "Infant feeding assessment, positioning support, hand-expression plan and monitored feeds.", "Effective attachment demonstrated and a community feeding follow-up arranged.", None, {"P92.5": ("assessment-diagnosis", "imaging-result"), "Z38.0": ("birth-summary",)}, "https://www.nhs.uk/start-for-life/baby/feeding-your-baby/breastfeeding/how-to-breastfeed/positioning-and-attachment/"),
    Scenario("neonatal-hypoglycaemia", Track.WELL_BABY, "Transient neonatal hypoglycaemia", "Hypoglycaemia", "Transitory neonatal hypoglycaemia", "An at-risk term newborn is screened during the birth admission and has a low pre-feed glucose result.", "Alert newborn with normal temperature and cardiorespiratory observations and no seizures.", "Repeat bedside glucose confirms transient neonatal hypoglycaemia, improving after feeding intervention.", "Supported feeding, glucose gel according to local protocol and serial glucose monitoring.", "Pre-feed glucose values stabilise and feeding is effective before discharge.", None, {"P70.4": ("assessment-diagnosis", "imaging-result"), "Z38.0": ("birth-summary",)}, "https://www.bapm.org/resources/identification-and-management-of-neonatal-hypoglycaemia-in-the-full-term-infant-a-framework-for-practice"),
    Scenario("infant-diabetic-mother", Track.WELL_BABY, "Infant of a diabetic mother", "Maternal diabetes", "Syndrome of infant of a diabetic mother", "A term infant born to a mother with pre-existing diabetes is admitted for risk-based observation.", "Well-appearing newborn with normal transition and no respiratory distress.", "Risk assessment documents maternal pre-existing diabetes; serial glucose measurements remain acceptable.", "Early feeding plan, thermal care and protocol-based glucose observation.", "Observation completed without complication; routine follow-up and safety-net advice given.", None, {"P70.1": ("assessment-diagnosis", "imaging-result"), "Z38.0": ("birth-summary",)}, "https://www.nice.org.uk/guidance/ng3"),
)

SCENARIO_BY_ID = {scenario.id: scenario for scenario in SCENARIOS}


def scenario_catalogue() -> list[dict[str, str]]:
    return [
        {"id": item.id, "track": item.track.value, "title": item.title, "short_label": item.short_label}
        for item in SCENARIOS
    ]
