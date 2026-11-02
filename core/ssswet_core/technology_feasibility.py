"""Evidence-led, read-only feasibility observatory for SSSWET technology themes."""
from __future__ import annotations
from collections import Counter
from typing import Any
from .research_journal import ResearchJournal, TECHNOLOGIES
TECHNOLOGY_LABELS = {"cellular":"Cellular improvement","longevity":"Longevity","armor":"Protective armor","jetpack":"Jetpacks","translator":"Human–alien translators","spacetime":"Spacetime physics","timetravel":"Time travel","cleanenergy":"Clean energy systems","energyStorage":"Advanced energy storage","water":"Clean water and desalination","foodSystems":"Sustainable food systems","climate":"Climate adaptation","biodiversity":"Biodiversity protection","wildlife":"Wildlife protection","oceans":"Ocean and marine restoration","reforestation":"Reforestation and habitat restoration","agriculture":"Regenerative agriculture","circularEconomy":"Circular economy and recycling","airQuality":"Clean air technologies","mobility":"Sustainable mobility","accessibility":"Assistive and accessibility technology","disasterResilience":"Disaster prevention and response","publicHealth":"Public health and prevention","sanitation":"Sanitation and waste-water treatment","education":"Open science and education","animalHealth":"Animal health and welfare","materials":"Sustainable and safer materials","carbonMonitoring":"Carbon and ecosystem monitoring","pollinators":"Pollinator protection","artificialGravity":"Artificial gravity","medicalNanotechnology":"Medical nanotechnology","atmosphericRestoration":"Atmospheric restoration","neurointerfaces":"Brain–computer interfaces","quantumNetworks":"Quantum communication networks","fusionEnergy":"Fusion energy","spaceLifeSupport":"Closed-loop space life-support","autonomousLabs":"Autonomous research laboratories","roboticsExoskeletons":"Advanced robotics and exoskeletons","planetaryMonitoring":"Planetary monitoring and asteroid risk assessment","advancedComputing":"Advanced computing and scientific AI"}
NEXT_STEPS = {
"literature":"Collect and critically assess primary scientific literature and authoritative technical standards.",
"feasibility":"Write a bounded feasibility assessment covering physical principles, assumptions, resources and known constraints.",
"simulation":"If useful, define a reproducible simulation with explicit model limits; do not treat its output as an observation.",
"prototype":"If a safe and lawful design path exists, document a bounded prototype specification and qualified oversight before construction.",
"test":"Define measurable acceptance criteria and a safe, documented test protocol before interpreting prototype performance.",
"independent_review":"Seek an independent review with disclosed expertise, methods, provenance and conflicts of interest.",
"references":"Attach traceable primary references or existing record identifiers to substantive claims.",
"delivery":"Before any product offer, separately assess safety, legal compliance, manufacturability, quality control, maintenance, support and delivery capability."}
class TechnologyFeasibilityObservatory:
    """Summarize recorded research maturity without assigning a feasibility score."""
    def __init__(self, store) -> None:
        self.journal = ResearchJournal(store)
    def build(self, technology: str | None = None) -> dict[str, Any]:
        if technology and technology not in TECHNOLOGIES: raise ValueError("unknown technology")
        all_entries = self.journal.overview(technology=technology, limit=500)["entries"]
        reports = []
        for key in ([technology] if technology else sorted(TECHNOLOGIES)):
            entries = [entry for entry in all_entries if entry["technology"] == key]
            classes = Counter(entry["classification"] for entry in entries)
            events = Counter(entry["event_type"] for entry in entries)
            refs = sorted({ref for entry in entries for ref in entry.get("evidence_refs", [])})
            missing = []
            if not classes["literature"]: missing.append("literature")
            if not events["feasibility_assessment"]: missing.append("feasibility")
            if not classes["simulation"]: missing.append("simulation")
            if not classes["prototype"]: missing.append("prototype")
            if not events["test"]: missing.append("test")
            if not classes["independent_review"] and not events["independent_review"]: missing.append("independent_review")
            if not refs: missing.append("references")
            missing.append("delivery")
            if not entries: maturity = "no_project_records"
            elif classes["independent_review"] or events["independent_review"]: maturity = "independent_review_recorded"
            elif classes["prototype"] or events["prototype"]: maturity = "prototype_recorded_not_validated"
            elif classes["simulation"] or events["simulation"]: maturity = "simulation_recorded_not_validated"
            elif classes["literature"] or events["literature_review"]: maturity = "literature_recorded"
            else: maturity = "early_research_records"
            reports.append({"technology":key,"label":TECHNOLOGY_LABELS[key],"record_count":len(entries),
                "classification_counts":dict(sorted(classes.items())),"event_type_counts":dict(sorted(events.items())),
                "evidence_reference_count":len(refs),"evidence_references":refs,
                "latest_recorded_at":max((entry["created_at"] for entry in entries),default=None),
                "recorded_maturity":maturity,"technical_feasibility":"not_assessed","delivery_readiness":"not_assessed",
                "missing_review_areas":missing,"suggested_next_steps":[NEXT_STEPS[x] for x in missing],
                "requires_qualified_human_review":True})
        integrity=self.journal.verify_chain()
        return {"technologies":reports,"count":len(reports),
            "method":"deterministic review of explicitly classified local research-journal entries",
            "read_only":True,"automatic_task_creation":False,"scientific_validity_established":False,
            "technical_feasibility_established":False,"delivery_authorized":False,"journal_chain_integrity":integrity,
            "limitations":["Absence of a journal entry does not prove absence of external scientific work.",
            "Recorded literature, simulations, prototypes and observations remain distinct evidence classes.",
            "A prototype or successful test record does not by itself establish safety, legal compliance, manufacturability or product readiness.",
            "This observatory does not autonomously discover, perform or verify experiments.",
            "All next steps require human review and qualified expertise appropriate to the technology."]}
