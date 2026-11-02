# Context-aware research claim comparison

SSSWET provides a conservative comparison layer for explicitly structured research claims. It identifies review leads without automatically deciding which source is correct.

## Comparison rules

Claims are compared only when normalized subject, predicate, scope, conditions and unit match. Differences in declared scope, test conditions or unit remain in separate groups. No implicit unit conversion is performed.

## Review classifications

- `potential_conflict`: distinct sources report different values in the same declared context.
- `temporal_difference_needs_review`: distinct values have complete, differing observation-date labels. This may indicate change over time, but the comparator does not assume that explanation.

Each result retains source identifiers and reported values. Dates are treated as labels; no chronology or causal interpretation is inferred.

## Limitations

The comparator does not extract claims from prose, normalize physical units, assess measurement uncertainty, test statistical significance, establish source independence, or resolve disagreements. Missing or differently worded context may prevent relevant claims from being compared. Human reviewers must inspect original sources, methods, dates and conditions before revising a research conclusion.