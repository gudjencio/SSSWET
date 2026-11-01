from .models import Finding, VerificationState


class SafetyGate:
    """High-level safety gate for research publication.

    The gate is deliberately conservative. It does not provide instructions
    for harmful construction or deployment; it only decides whether a result
    is eligible for a public research summary.
    """

    HIGH_RISK_DOMAINS = {"medical", "biological", "aerospace", "human_subjects"}

    def assess(self, finding: Finding) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        domain = str(finding.metadata.get("domain", "")).lower()

        if finding.verification == VerificationState.REJECTED:
            reasons.append("finding rejected")
        if finding.verification not in {
            VerificationState.INDEPENDENTLY_VERIFIED,
            VerificationState.REPRODUCED,
            VerificationState.REQUIRES_REAL_WORLD_VALIDATION,
        }:
            reasons.append("insufficient verification")
        if domain in self.HIGH_RISK_DOMAINS and finding.verification != VerificationState.REPRODUCED:
            reasons.append("qualified real-world validation remains required")

        return (not reasons, reasons)
