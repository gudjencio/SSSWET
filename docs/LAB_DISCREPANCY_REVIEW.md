# Digital-lab discrepancy review

The local read-only endpoint `GET /api/lab-discrepancies` screens stored digital-lab comparison records and exposes three review categories:

- **Recorded result divergence:** the comparison explicitly marks the runs comparable and records outputs outside the stated tolerance.
- **Incompatible conditions:** the comparison explicitly marks the runs as not comparable.
- **Incomplete comparison data:** the record does not contain enough explicit fields to classify the outcome.

The analyzer does not compare raw scientific claims, infer missing relationships, create dispute cases, launch experiments, or change verification states. It only uses saved comparison records and their linked run metadata.

A recorded divergence is not proof of a scientific contradiction. Differences may arise from measurement uncertainty, implementation details, unrecorded confounders, data quality, or limitations in the comparison method. Simulation records remain simulations and are never treated as real-world observations.

Every finding requires human review. No result is selected as correct, and scientific validity is never established by this endpoint.
