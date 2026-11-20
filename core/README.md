# SSSWET Core

This directory contains software components used by the SSSWET research environment.

The core is experimental software intended to support structured research records, evidence review, computational work and project operations. Its presence in this public repository does not mean that every component is production-ready or suitable for safety-critical use.

## Dataset governance and release checks

The ssswet_core.dataset_governance module provides ten bounded, in-memory helpers for licence-use declarations, consent/purpose scope, field-level release dispositions, aggregate small-cell suppression, schema compatibility, lineage DAG validation, group/time split leakage, retention review dates, consolidated release readiness and deterministic metadata-only release manifests. See the dataset governance guide at ../docs/DATASET_GOVERNANCE_2026-11-10.md for acceptance criteria, examples, benchmark scope and limitations.

These helpers do not inspect raw participant values, interpret law, grant ethics approval, delete data, or authorize publication. A successful policy gate means only that the supplied declarations satisfy the implemented checks; accountable human review remains mandatory.

## Development

Use the project-level installation and contribution instructions supplied with the current source distribution. Keep local databases, private datasets, credentials, unpublished research material and operational records outside version control.

## Evidence and safety

Stored records and generated summaries are not automatically verified scientific findings. Simulations are not physical observations. Human review, domain expertise and appropriate safety, ethical and legal assessment remain necessary before any real-world application.

## Disclosure boundary

This public repository is not the authoritative location for confidential research plans, unpublished technical designs, private operational procedures or trade secrets. Do not add such material to commits, issues, pull requests, examples, logs or test fixtures.

See the public information and disclosure policy at ../docs/PUBLICATION_POLICY.md for the project's publication boundary.
