from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SubtaskSpec:
    objective: str
    role: str
    domain: str
    priority: int = 5


class TaskDecomposer:
    """Create small, independently checkable research units.

    This is intentionally deterministic. A future model provider can propose
    decompositions, but the orchestrator should validate their structure before
    accepting them.
    """

    ROLE_RULES = (
        ("math", "mathematician"),
        ("physics", "physicist"),
        ("engineering", "engineer"),
        ("medical", "medical_researcher"),
        ("biology", "biologist"),
        ("materials", "materials_scientist"),
        ("aerospace", "aerospace_researcher"),
        ("software", "software_researcher"),
    )

    def decompose(self, objective: str, domain: str = "general") -> list[SubtaskSpec]:
        text = re.sub(r"\s+", " ", objective.strip())
        if not text:
            raise ValueError("A research objective is required.")

        role = self._role_for(domain, text)
        base = [SubtaskSpec(text, role, domain)]

        # Independent verification is represented as a separate unit so that
        # the first researcher cannot be its own sole verifier.
        base.append(
            SubtaskSpec(
                f"Independently challenge and check the claim: {text}",
                "independent_verifier",
                domain,
                6,
            )
        )
        return base

    def _role_for(self, domain: str, objective: str) -> str:
        normalized = f"{domain} {objective}".lower()
        for keyword, role in self.ROLE_RULES:
            if keyword in normalized:
                return role
        return "general_researcher"
