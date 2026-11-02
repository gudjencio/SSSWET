# Technology dossier and evidence timeline

Each technology can have a persistent dossier identified by a stable technology ID. The dossier stores its title, research domain, and an append-only event history.

## Recorded event types

Research notes, evidence, experiments, simulations, peer reviews, risk updates, cost estimates, milestones, corrections, negative results, status changes and decisions can be recorded. Events preserve the actor, timestamp, payload and source references.

Negative and failed results are first-class records. They are retained as useful research context rather than silently overwritten.

## Scientific status

The register supports concept, hypothesis, research, simulation, candidate, independently verified, reproduced, real-world validation, validated, paused and rejected states. A state is a recorded assertion, not a scientific certification. Transitions to independently verified, reproduced or validated require source references, but the registry does not inspect those sources or certify their quality.

## Integrity and limitations

Dossier events are append-only and protected against updates and deletions at the SQLite layer. The register does not infer feasibility, calculate risk scores, authorize experiments, establish safety, or declare commercial readiness. A future review workflow must inspect the referenced source material and independently attest to any scientific conclusion.

Implementation: `core/ssswet_core/technology_dossier.py`.
Tests: `core/tests/test_technology_dossier.py`.
