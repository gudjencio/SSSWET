# Evidence Quality Matrix

The Evidence Quality Matrix organizes the evidence metadata and review coverage already attached to SSSWET evidence dossiers.

## What it reports

- Counts of source, protocol, run, dataset, comparison and review records.
- A transparent source-metadata rubric using the existing source assessor.
- Explicit provenance overlap signals and contextual author or institution overlaps.
- Recorded reviewer count, verdict positions and conflict declarations.
- Evidence categories with no records attached to the selected dossier.

## API

```http
GET /api/evidence-quality-matrix?limit=100
GET /api/evidence-quality-matrix?dossier_id=YOUR_DOSSIER_ID
```

The list limit must be from 1 to 200. The dossier-specific form returns one dossier report.

## Interpretation

Source rubric scores concern declared source metadata, not truth, correctness or the quality of a dossier as a whole. A source may be primary and peer reviewed yet still contain errors or limitations. A lack of recorded provenance overlap does not establish independence. Multiple reviewer verdicts are shown as competing recorded positions, not resolved automatically.

The matrix is read-only. It does not change verification states, infer missing data, adjudicate disagreements or establish scientific validity, technical feasibility, safety or readiness for deployment.
