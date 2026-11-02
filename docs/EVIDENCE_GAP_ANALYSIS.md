# Evidence Gap Analysis

The evidence-gap analyzer produces a deterministic checklist from an assembled evidence dossier and an optional list of structured review records.

## Scope

It can identify missing source, run, dataset, protocol and comparison records; multiple recorded review verdicts; and review evidence-reference identifiers that do not match the records supplied in the dossier.

These are record-completeness observations, not claims that evidence does not exist elsewhere. An unmatched identifier may refer to a valid record outside the dossier and should be reconciled with its originating system.

## Python usage

```python
from ssswet_core.evidence_gap_analysis import EvidenceGapAnalyzer

report = EvidenceGapAnalyzer().analyze(dossier, reviews)
```

The report includes prioritized gaps, counts, unmatched reference identifiers and explicit safeguards. The analyzer is read-only: it does not modify dossiers, review events, verification states or research campaigns.

## Interpretation

Competing verdicts trigger a follow-up item, not an automatic winner or consensus. Reviewers should compare the recorded rationales, methods assessments, limitations and evidence references, then identify what additional source inspection or independent observation could distinguish the interpretations.

The analyzer does not establish scientific validity, assess source quality from identifiers alone, authorize experiments, or certify safety or readiness.
