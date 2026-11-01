# Reproducibility intelligence

The local read-only endpoint `GET /api/reproducibility-intelligence` summarizes recorded digital-laboratory comparisons by protocol and version.

## Evidence index

The reproducibility evidence index is an evidence-record completeness indicator, not a scientific-quality score or probability. Each recorded comparison contributes up to 100 points across five equally weighted binary dimensions:

| Dimension | Points | Recorded condition |
|---|---:|---|
| Record integrity | 20 | Both run fingerprints verify |
| Comparability | 20 | The comparison explicitly records comparable conditions |
| Output consistency | 20 | Comparable outputs match within the recorded tolerance |
| Independent verification | 20 | Independent verification is explicitly recorded and campaigns differ |
| Provenance separation | 20 | Provenance groups differ and no source or dataset identifiers are shared |

A protocol index is the arithmetic mean of its recorded comparison indices. Missing comparisons produce no index (`null`), not a zero. An index is not a measure of truth, causal validity, safety, external reproducibility or scientific merit.

## Classifications

- `no_recorded_comparisons`
- `insufficient_data`
- `insufficient_record_integrity` (comparison-level)
- `incomplete_comparison`
- `incomparable_conditions`
- `recorded_output_divergence`
- `matching_outputs_not_independently_verified`
- `independently_verified_match_recorded`

A matching output is not treated as independent verification. The comparison workflow currently records independent verification as false until a separate human review process explicitly records it.

## Parameter sensitivity

The current run schema does not define normalized parameter sweeps or sensitivity models. The service therefore reports parameter sensitivity as `not_assessed`; it does not infer sensitivity from arbitrary differences in parameters or outputs. A future sensitivity module will require explicit parameter ranges, units, controlled designs, repeated measurements and uncertainty metadata.

## Limits and safeguards

The service reads existing protocol, run and comparison histories. It does not alter research records, create tasks, schedule or execute experiments, or promote simulations to real observations. Fingerprint verification checks record integrity against the stored hash; it does not prove that the original observation is true or that its source is trustworthy. Every report keeps `scientific_validity_established` false and requires human review.
