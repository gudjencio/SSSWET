# Dataset provenance registry

The local read-only endpoint `/api/digital-lab/datasets` exposes an append-only
registry of dataset metadata and version history.

Register a version using `DatasetRegistry` and `DatasetVersion`:

```python
from ssswet_core.dataset_registry import DatasetRegistry, DatasetVersion

registry = DatasetRegistry(store)
registry.register_version(DatasetVersion(
    dataset_id="observations-001",
    version=1,
    title="Illustrative observation dataset",
    description="A documented collection of measurements",
    campaign_id="campaign-001",
    license="CC-BY-4.0",
    source_ids=("source-paper-001",),
    content_sha256="replace-with-the-64-character-file-digest",
    metadata={"format": "CSV", "unit_system": "SI"},
))
```

Versions are sequential and immutable. A later version identifies its
immediate parent. Transformations record input and output versions, operation,
parameters, software, operator and limitations. Both versions must exist, and
the output version must declare the input as its parent.

Repeated content digests across campaigns are reported as shared-content
candidates. A matching digest identifies byte-identical content only when
computed from the same bytes; it does not establish scientific equivalence,
data quality, independence or truth. Metadata fingerprints detect record
changes but are not digital signatures.

The registry stores metadata and declared digests, not uploaded data files.
Compute the digest locally from the exact file bytes when available.
