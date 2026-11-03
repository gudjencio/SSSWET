"""1000-entry public technology portfolio registry (legacy module name retained)."""
from __future__ import annotations

from .technology_catalogue import TECHNOLOGY_CATALOGUE as CORE_TECHNOLOGY_CATALOGUE
from .technology_catalogue_expansion import TECHNOLOGY_CATALOGUE_EXPANSION
from .technology_catalogue_additions import ADDITIONAL_TECHNOLOGIES
from .technology_catalogue_expansion_2 import TECHNOLOGY_CATALOGUE_EXPANSION_2
from .technology_dossier import TechnologyDossierRegistry

def _complete_research_record(item: dict) -> dict:
    """Ensure every public catalogue entry states a scope and its limitations."""
    record = dict(item)
    scope = record.get("research_scope")
    if not isinstance(scope, list) or not scope:
        record["research_scope"] = [
            "Define a testable research question, measurable outcomes and reproducible methods",
            "Compare evidence, simulations and alternative explanations with explicit uncertainty",
            "Assess safety, accessibility, lifecycle impact and independent review before deployment",
        ]
    limitations = record.get("scientific_limitations")
    if not isinstance(limitations, list) or not limitations:
        record["scientific_limitations"] = [
            "Catalogue inclusion records a research objective only; it does not establish feasibility, readiness or validation",
            "Distinguish measured evidence, model assumptions, simulations, hypotheses and unverified claims",
            "Any prototype or field study requires qualified oversight, documented risk assessment and applicable legal review",
        ]
    return record


TECHNOLOGY_CATALOGUE = [
    _complete_research_record(item)
    for item in (
        *CORE_TECHNOLOGY_CATALOGUE,
        *TECHNOLOGY_CATALOGUE_EXPANSION,
        *ADDITIONAL_TECHNOLOGIES,
        *TECHNOLOGY_CATALOGUE_EXPANSION_2,
    )
]
if len(TECHNOLOGY_CATALOGUE) != 1000:
    raise RuntimeError(f"SSSWET technology catalogue must contain 1000 entries; found {len(TECHNOLOGY_CATALOGUE)}")


def register_catalogue(registry: TechnologyDossierRegistry, actor_id: str = "catalogue") -> dict:
    """Idempotently register all 1000 research programmes as unvalidated dossiers."""
    created = []
    updated_scope = []
    existing = {item["technology_id"] for item in registry.list_dossiers(limit=1000)}
    for item in TECHNOLOGY_CATALOGUE:
        is_new = item["technology_id"] not in existing
        if is_new:
            registry.create(technology_id=item["technology_id"], title=item["title"], domain=item["domain"], actor_id=actor_id)
        dossier = registry.get(item["technology_id"]) if not is_new else None
        already_recorded = bool(dossier) and any(
            event.get("payload", {}).get("catalogue_subcategory") == item["subcategory"]
            and event.get("payload", {}).get("research_scope") == item.get("research_scope", [])
            for event in dossier.get("events", [])
        )
        if already_recorded:
            continue
        registry.append_event(
            technology_id=item["technology_id"],
            event_type="research_note",
            payload={
                "catalogue_subcategory": item["subcategory"],
                "catalogue_registration": True,
                "research_status": "not_assessed",
                "research_scope": item.get("research_scope", []),
                "scientific_limitations": item.get("scientific_limitations", []),
            },
            actor_id=actor_id,
        )
        if is_new:
            created.append(item["technology_id"])
        else:
            updated_scope.append(item["technology_id"])
    return {"catalogue_size": 1000, "created_count": len(created), "already_registered_count": 1000 - len(created), "updated_scope_count": len(updated_scope), "updated_scope_ids": updated_scope, "created_ids": created, "research_status": "not_assessed"}
