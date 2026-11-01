import pytest
from ssswet_core.dataset_registry import DatasetRegistry, DatasetVersion
from ssswet_core.persistence import SQLiteResearchStore


def test_dataset_registry_rejects_invalid_digest(tmp_path):
    store = SQLiteResearchStore(tmp_path / 'datasets.sqlite3')
    registry = DatasetRegistry(store)
    with pytest.raises(ValueError, match='SHA-256'):
        DatasetVersion('d1', 1, 'Title', 'Description', 'campaign-1', 'CC-BY-4.0', (), 'invalid')
