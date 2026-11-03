# Research Delivery Cadence

SSSWET uses ambitious throughput targets while preserving evidence quality and public safety.

## Targets

- Major improvements: target up to **1,000 per day**, where engineering capacity permits.
- Bug fixes: target up to **100 per hour**, where verified defects are actually available.

These are targets, not fabricated quotas. A change counts only when it is substantive, tested, measurable, and does not knowingly regress existing capabilities.

## Acceptance rules

A major improvement should have:

1. a clearly identified previous behaviour;
2. a measurable acceptance criterion;
3. regression coverage;
4. evidence of the observed result;
5. public-facing documentation when the feature affects users;
6. explicit limitations where scientific claims remain uncertain.

A bug fix should have a reproducible defect, a regression test where practical, and verification that the correction does not introduce a known downgrade.

## Throughput accounting

When actual throughput is below a target, the project reports the shortfall rather than manufacturing work units. Multiple cosmetic edits, duplicated commits, or documentation-only changes do not count as major improvements.

Safety, scientific review, privacy, cybersecurity, legal and ethical constraints always take precedence over throughput.
