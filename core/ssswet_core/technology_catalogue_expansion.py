"""Systematic expansion of the SSSWET research portfolio.

The expansion adds 394 explicitly generated research programmes to the existing
106-entry core catalogue, producing a 500-entry target portfolio. Entries are
research programmes, not claims of demonstrated or validated technology.
"""
from __future__ import annotations

_FAMILIES = {
    "space": (("orbital", "deep-space", "planetary", "lunar", "interstellar"), ("navigation", "robotics", "habitats", "resource mapping", "radiation monitoring", "communications", "autonomous operations", "precision landing", "thermal control", "life support")),
    "protection": (("civil", "industrial", "rescue", "extreme-environment", "infrastructure"), ("hazard detection", "impact mitigation", "thermal protection", "radiation monitoring", "structural monitoring", "evacuation support", "wearable safety", "decontamination", "emergency power", "environmental sensing")),
    "energy": (("renewable", "grid", "portable", "industrial", "space"), ("generation", "storage", "conversion", "thermal management", "power quality", "load balancing", "energy recovery", "fault detection", "demand forecasting", "microgrid control")),
    "materials": (("advanced", "bioinspired", "structural", "functional", "recyclable"), ("characterization", "self-healing", "damage detection", "thermal management", "lightweighting", "recycling", "surface engineering", "fatigue monitoring", "manufacturing control", "durability prediction")),
    "life": (("cellular", "tissue", "organ", "neural", "assistive"), ("monitoring", "regeneration", "drug delivery", "biocompatibility", "prosthetic control", "rehabilitation", "physiological sensing", "clinical data", "simulation", "safety monitoring")),
    "environment": (("ecosystem", "climate", "marine", "agricultural", "atmospheric"), ("monitoring", "restoration", "forecasting", "water quality", "soil sensing", "biodiversity mapping", "carbon accounting", "pollution detection", "wildfire detection", "resilience planning")),
    "robotics": (("field", "assistive", "industrial", "rescue", "scientific"), ("navigation", "manipulation", "mapping", "inspection", "coordination", "human interaction", "fault recovery", "energy management", "perception", "safe autonomy")),
    "society": (("scientific", "public", "distributed", "secure", "accessible"), ("computing", "communication", "translation", "data provenance", "knowledge discovery", "privacy protection", "education", "health information", "decision support", "research coordination")),
}
_SUBCATEGORIES = {"space":"advancedSpaceSystems", "protection":"protectiveEngineering", "energy":"energySystems", "materials":"advancedMaterials", "life":"lifeSciences", "environment":"environmentalStewardship", "robotics":"roboticsSystems", "society":"knowledgeSystems"}

def _identifier(text: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in text.replace("-", " ").split() if part)

def build_expansion(limit: int = 394) -> list[dict]:
    entries = []
    for domain, (families, capabilities) in _FAMILIES.items():
        for family in families:
            for capability in capabilities:
                entries.append({"technology_id": f"program{_identifier(domain)}{_identifier(family)}{_identifier(capability)}", "title": f"{family.title()} {capability.title()} Research", "domain": domain, "subcategory": _SUBCATEGORIES[domain]})
    return entries[:limit]

TECHNOLOGY_CATALOGUE_EXPANSION = build_expansion()
if len(TECHNOLOGY_CATALOGUE_EXPANSION) != 394:
    raise RuntimeError("SSSWET technology expansion must contain exactly 394 entries.")
