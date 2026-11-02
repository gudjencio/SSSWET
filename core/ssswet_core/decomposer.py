from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SubtaskSpec:
    objective: str
    role: str
    domain: str
    priority: int = 5


class TaskDecomposer:
    """Create deterministic, independently checkable research units.

    Straightforward questions keep a two-agent path. Clearly multi-faceted
    objectives receive narrowly scoped complementary work, while an
    independent verifier remains a separate final challenge.
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

    COMPLEXITY_SIGNALS = (
        "design", "architecture", "system",
        "evaluate", "evaluation", "trade-off", "tradeoff", "optimise",
        "optimize", "integrate", "integration", "multi-disciplinary",
        "multidisciplinary", "feasibility",
    )
    RISK_SIGNALS = (
        "human", "medical", "clinical", "patient", "biological",
        "radiation", "exposure", "safety", "weapon", "survival",
        "implant", "treatment", "autonomous",
    )

    def decompose(self, objective: str, domain: str = "general") -> list[SubtaskSpec]:
        text = re.sub(r"\s+", " ", str(objective).strip())
        if not text:
            raise ValueError("A research objective is required.")

        normalized = f"{domain} {text}".lower()
        role = self._role_for(domain, text)
        tasks = [SubtaskSpec(text, role, domain)]

        # Add a distinct systems lens only when the objective explicitly
        # signals integration, comparison, design or feasibility work.
        if any(signal in normalized for signal in self.COMPLEXITY_SIGNALS):
            tasks.append(
                SubtaskSpec(
                    "Assess system architecture, technical dependencies, "
                    "resource constraints and practical feasibility for this objective: "
                    + text,
                    "systems_engineer",
                    domain,
                    5,
                )
            )

        # Human-impact or high-consequence topics receive a separate safety
        # and ethics lens; this is a review task, not an approval.
        if any(signal in normalized for signal in self.RISK_SIGNALS):
            tasks.append(
                SubtaskSpec(
                    "Identify safety, ethical, legal and human-impact risks, "
                    "including unresolved safeguards, for this objective: "
                    + text,
                    "ethics_reviewer",
                    domain,
                    6,
                )
            )

        # The verifier is deliberately last and remains distinct from every
        # primary research assignment.
        tasks.append(
            SubtaskSpec(
                f"Independently challenge the assumptions, evidence quality, "
                f"uncertainties and conclusions for this objective: {text}",
                "independent_verifier",
                domain,
                7,
            )
        )
        return tasks

    def _role_for(self, domain: str, objective: str) -> str:
        normalized = f"{domain} {objective}".lower()
        for keyword, role in self.ROLE_RULES:
            if keyword in normalized:
                return role
        return "general_researcher"
