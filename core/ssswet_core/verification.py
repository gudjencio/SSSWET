from dataclasses import replace

from .models import Finding, VerificationState


class VerificationEngine:
    """Conservative evidence and reproduction state machine.

    Evidence strings are retained for traceability, but only distinct,
    explicitly identified sources count as independent evidence.
    """

    def independent_check(
        self,
        finding: Finding,
        evidence: str,
        source_id: str | None = None,
    ) -> Finding:
        if not evidence.strip():
            raise ValueError("evidence must not be empty")

        updated = replace(finding)
        updated.evidence = [*finding.evidence, evidence]
        metadata = dict(finding.metadata)
        records = list(metadata.get("independent_sources", []))

        if source_id and source_id.strip():
            normalized_id = source_id.strip()
            if normalized_id not in records:
                records.append(normalized_id)
        metadata["independent_sources"] = records
        updated.metadata = metadata

        if len(records) >= 2:
            updated.verification = VerificationState.INDEPENDENTLY_VERIFIED
            updated.uncertainty = min(updated.uncertainty, 0.35)
        elif updated.evidence:
            updated.verification = VerificationState.CANDIDATE
            updated.uncertainty = min(updated.uncertainty, 0.7)
            if not source_id:
                note = "Evidence source identity is missing; independence is not established."
                if note not in updated.limitations:
                    updated.limitations = [*updated.limitations, note]
        return updated

    def require_reproduction(
        self,
        finding: Finding,
        reproduction_id: str | None = None,
    ) -> Finding:
        updated = replace(finding)
        source_ids = set(finding.metadata.get("independent_sources", []))
        if len(source_ids) < 2 or not reproduction_id or not reproduction_id.strip():
            note = (
                "Reproduction was not recorded: two distinct evidence sources "
                "and a separate reproduction run identifier are required."
            )
            if note not in updated.limitations:
                updated.limitations = [*updated.limitations, note]
            return updated
        if reproduction_id.strip() in source_ids:
            note = "The reproduction run must be distinct from the evidence sources."
            if note not in updated.limitations:
                updated.limitations = [*updated.limitations, note]
            return updated

        metadata = dict(finding.metadata)
        runs = list(metadata.get("reproduction_runs", []))
        if reproduction_id.strip() not in runs:
            runs.append(reproduction_id.strip())
        metadata["reproduction_runs"] = runs
        updated.metadata = metadata
        updated.verification = VerificationState.REPRODUCED
        updated.uncertainty = min(updated.uncertainty, 0.2)
        return updated

    def mark_real_world_validation_required(self, finding: Finding) -> Finding:
        updated = replace(finding)
        updated.verification = VerificationState.REQUIRES_REAL_WORLD_VALIDATION
        note = (
            "Computational evidence is not a substitute for qualified "
            "real-world validation."
        )
        if note not in updated.limitations:
            updated.limitations = [*updated.limitations, note]
        return updated

    @staticmethod
    def is_publishable(finding: Finding) -> bool:
        return finding.verification in {
            VerificationState.INDEPENDENTLY_VERIFIED,
            VerificationState.REPRODUCED,
        }
