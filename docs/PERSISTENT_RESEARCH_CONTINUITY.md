# Persistent research-continuity workflows

The continuity service connects the bounded helpers to SSSWET's existing SQLite
collective-memory store. It reads stored records without silently changing their
review status, merging duplicates, resolving disagreements or upgrading claims.

## Python API

```python
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_continuity import ResearchContinuityService

continuity = ResearchContinuityService(SQLiteResearchStore("research.sqlite3"))
overview = continuity.overview(campaign_id="thermal-coating")
matches = continuity.search("thermal cycling", campaign_id="thermal-coating")
handoff = continuity.handoff("thermal cycling", campaign_id="thermal-coating")
snapshot = continuity.snapshot(campaign_id="thermal-coating")
```

## Integrated workflows

1. Read bounded records from persistent collective memory.
2. Filter retrieval by campaign and review status while preserving provenance.
3. Prepare size-bounded agent hand-offs with explicit human-review constraints.
4. Group exact duplicates for review without merging or deleting records.
5. Flag opposite-polarity wording as a candidate conflict, never a verdict.
6. Produce deterministic, checksummed, versioned memory exports.
7. Validate snapshot schema, record count, unique identifiers and digest.
8. Query explicitly supplied observations over inclusive UTC windows.
9. Screen expected observation cadence slots while stating that gaps do not prove event absence.
10. Compare shared-source timelines while retaining combined timestamp uncertainty.

The overview endpoint is read-only. Timeline functions operate only on observations
explicitly supplied by the caller; they do not infer missing data or reconstruct
unrecorded events. SHA-256 detects accidental or subsequent payload changes but
is not a digital signature or proof of origin. Retrieval scores are not scientific
confidence scores. All apparent conflicts and downstream decisions require human
review against original sources and methods.
