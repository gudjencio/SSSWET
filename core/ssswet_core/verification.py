from dataclasses import replace

from .models import Finding, VerificationState


class VerificationEngine:
    """Conservative evidence and reproduction state machine.

    Distinct identifiers alone do not establish independence. A reviewer must
    explicitly confirm the provenance group for each source. Likewise, a run
    identifier alone is not proof that a reproduction was actually completed.
    """

    def independent_check(
        self,
        finding: Finding,
        evidence: str,
        source_id: str | None = None,
        *,
        independence_group: str | None = None,
        independence_confirmed: bool = False,
    ) -> Finding:
        if not evidence.strip():
            raise ValueError("evidence must not be empty")

        updated = replace(finding)
        updated.evidence = [*finding.evidence, evidence]
        metadata = dict(finding.metadata)
        records = list(metadata.get("independent_sources", []))
        groups = dict(metadata.get("independence_groups", {}))
        confirmed = set(metadata.get("independence_confirmed_sources", []))

        normalized_id = source_id.strip() if source_id and source_id.strip() else ""
        normalized_group = (
            independence_group.strip()
            if independence_group and independence_group.strip()
            else ""
        )

        if normalized_id:
            if normalized_id not in records:
                records.append(normalized_id)
            if normalized_group:
                groups[normalized_id] = normalized_group
            if independence_confirmed and normalized_group:
                confirmed.add(normalized_id)

        metadata["independent_sources"] = records
        metadata["independence_groups"] = groups
        metadata["independence_confirmed_sources"] = sorted(confirmed)
        updated.metadata = metadata

        verified_groups = {
            groups[source]
            for source in confirmed
            if source in groups and groups[source]
        }
        if len(verified_groups) >= 2:
            updated.verification = VerificationState.INDEPENDENTLY_VERIFIED
            updated.uncertainty = min(updated.uncertainty, 0.35)
        else:
            if updated.evidence:
                updated.verification = VerificationState.CANDIDATE
                updated.uncertainty = min(updated.uncertainty, 0.7)
            if not normalized_id:
                note = "Evidence source identity is missing; independence is not established."
            elif not normalized_group or not independence_confirmed:
                note = (
                    "Source independence has not been explicitly assessed; "
                    "distinct identifiers alone are insufficient."
                )
            else:
                note = (
                    "At least two explicitly assessed, distinct provenance groups "
                    "are required for independent verification."
                )
            if note not in updated.limitations:
                updated.limitations = [*updated.limitations, note]
        return updated

    def require_reproduction(
        self,
        finding: Finding,
        reproduction_id: str | None = None,
        *,
        reproduction_confirmed: bool = False,
    ) -> Finding:
        updated = replace(finding)
        metadata = dict(finding.metadata)
        groups = dict(metadata.get("independence_groups", {}))
        confirmed = set(metadata.get("independence_confirmed_sources", []))
        independent_groups = {
            groups[source]
            for source in confirmed
            if source in groups and groups[source]
        }
        if (
            len(independent_groups) < 2
            or not reproduction_id
            or not reproduction_id.strip()
            or not reproduction_confirmed
        ):
            note = (
                "Reproduction was not recorded: two assessed independent provenance "
                "groups, a separate run identifier, and explicit confirmation that "
                "the reproduction was completed are required."
            )
            if note not in updated.limitations:
                updated.limitations = [*updated.limitations, note]
            return updated

        run_id = reproduction_id.strip()
        source_ids = set(finding.metadata.get("independent_sources", []))
        if run_id in source_ids:
            note = "The reproduction run must be distinct from the evidence sources."
            if note not in updated.limitations:
                updated.limitations = [*updated.limitations, note]
            return updated

        runs = list(metadata.get("reproduction_runs", []))
        if run_id not in runs:
            runs.append(run_id)
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
