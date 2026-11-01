from dataclasses import replace

from .models import Finding, VerificationState


class VerificationEngine:
    """Conservative verification state machine.

    This foundation never treats agent consensus as proof. A finding must
    accumulate independent evidence before it can become publishable.
    """

    def independent_check(self, finding: Finding, evidence: str) -> Finding:
        updated = replace(finding)
        updated.evidence = [*finding.evidence, evidence]
        if len(updated.evidence) >= 2:
            updated.verification = VerificationState.INDEPENDENTLY_VERIFIED
            updated.uncertainty = min(updated.uncertainty, 0.35)
        elif updated.evidence:
            updated.verification = VerificationState.CANDIDATE
            updated.uncertainty = min(updated.uncertainty, 0.7)
        return updated

    def require_reproduction(self, finding: Finding) -> Finding:
        updated = replace(finding)
        updated.verification = VerificationState.REPRODUCED
        updated.uncertainty = min(updated.uncertainty, 0.2)
        return updated

    def mark_real_world_validation_required(self, finding: Finding) -> Finding:
        updated = replace(finding)
        updated.verification = VerificationState.REQUIRES_REAL_WORLD_VALIDATION
        updated.limitations = [
            *finding.limitations,
            "Computational evidence is not a substitute for qualified real-world validation.",
        ]
        return updated

    @staticmethod
    def is_publishable(finding: Finding) -> bool:
        return finding.verification in {
            VerificationState.INDEPENDENTLY_VERIFIED,
            VerificationState.REPRODUCED,
        }
