from dataclasses import dataclass


@dataclass(frozen=True)
class RescueAction:
    action: str
    safety_gate: str
    evidence_required: bool = True


SAFE_ACTIONS = {
    "hazard_assessment": RescueAction("hazard_assessment", "human_approval", True),
    "remote_sensing": RescueAction("remote_sensing", "automated_review", True),
    "communications_relay": RescueAction("communications_relay", "human_approval", True),
    "resource_mapping": RescueAction("resource_mapping", "automated_review", True),
    "evacuation_support": RescueAction("evacuation_support", "human_approval", True),
}


def build_rescue_workflow(actions: list[str]) -> dict:
    selected = []
    rejected = []
    for action in actions:
        item = SAFE_ACTIONS.get(action)
        if item is None:
            rejected.append({"action": action, "reason": "not in the conservative rescue action allowlist"})
        else:
            selected.append(item.__dict__.copy())
    return {
        "actions": selected,
        "rejected": rejected,
        "requires_human_approval": any(a["safety_gate"] == "human_approval" for a in selected),
        "evidence_required": any(a["evidence_required"] for a in selected),
    }
