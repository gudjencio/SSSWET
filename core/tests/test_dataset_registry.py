import pytest
from ssswet_core.dataset_registry import DatasetRegistry, DatasetVersion
from ssswet_core.persistence import SQLiteResearchStore


def test_dataset_registry_rejects_invalid_digest(tmp_path):
    store = SQLiteResearchStore(tmp_path / 'datasets.sqlite3')
    registry = DatasetRegistry(store)
    with pytest.raises(ValueError, match='SHA-256'):
        DatasetVersion('d1', 1, 'Title', 'Description', 'campaign-1', 'CC-BY-4.0', (), 'invalid')


from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.dataset_registry import DatasetTransformation


def setup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "datasets.sqlite3")
    for campaign_id in ("campaign-a", "campaign-b"):
        campaign = create_campaign(
            campaign_id, campaign_id, "Dataset provenance research", "data science",
            [CampaignMilestone("m1", "Review", "Review dataset provenance")],
        )
        store.save_campaign(set_campaign_state(campaign, "active"))
    return store, DatasetRegistry(store)


def make_dataset(dataset_id="dataset-1", version=1, campaign="campaign-a",
                 digest="a" * 64, parent=0):
    return DatasetVersion(
        dataset_id, version, "Climate observations", "Declared observation dataset",
        campaign, "CC-BY-4.0", ("source-paper-1",), digest, parent,
        {"format": "CSV", "rows": 120},
    )


def test_dataset_version_is_fingerprinted_and_persisted(tmp_path):
    store, registry = setup(tmp_path)
    saved = registry.register_version(make_dataset())
    assert len(saved["record_fingerprint"]) == 64
    assert store.get_lab_dataset("dataset-1", 1)["license"] == "CC-BY-4.0"
    assert registry.overview()["integrity"]["all_intact"] is True


def test_dataset_versions_must_be_sequential_and_linked(tmp_path):
    _, registry = setup(tmp_path)
    registry.register_version(make_dataset())
    with pytest.raises(ValueError, match="immediately preceding"):
        registry.register_version(make_dataset(version=3, parent=1))
    registry.register_version(make_dataset(version=2, parent=1))
    assert registry.overview()["version_count"] == 2


def test_duplicate_content_digest_is_reported_across_campaigns(tmp_path):
    _, registry = setup(tmp_path)
    registry.register_version(make_dataset(dataset_id="dataset-a", campaign="campaign-a"))
    registry.register_version(make_dataset(dataset_id="dataset-b", campaign="campaign-b"))
    report = registry.overview()
    assert len(report["shared_content_candidates"]) == 1
    assert report["shared_content_candidates"][0]["cross_campaign"] is True
    assert report["scientific_validity_established"] is False


def test_transformation_requires_linked_registered_versions(tmp_path):
    store, registry = setup(tmp_path)
    registry.register_version(make_dataset(version=1))
    registry.register_version(make_dataset(version=2, parent=1))
    saved = registry.record_transformation(DatasetTransformation(
        "transform-1", "dataset-1", 1, 2, "Normalize temperature units",
        {"from": "C", "to": "K"}, "Python 3.12 / pandas", "operator-1",
        "Missing values were not imputed.",
    ))
    assert saved["input_version"] == 1
    assert len(store.lab_dataset_transformation_history()) == 1


def test_transformation_rejects_unlinked_versions(tmp_path):
    _, registry = setup(tmp_path)
    registry.register_version(make_dataset(version=1))
    registry.register_version(make_dataset(version=2, parent=1))
    with pytest.raises(ValueError, match="parent"):
        registry.record_transformation(DatasetTransformation(
            "transform-bad", "dataset-1", 1, 2, "Untracked transform",
            {}, "tool 1", "operator", "No validation performed",
        ))


def test_dataset_versions_are_immutable_in_sqlite(tmp_path):
    store, registry = setup(tmp_path)
    registry.register_version(make_dataset())
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute(
                "UPDATE lab_datasets SET content_fingerprint=? WHERE dataset_id=?",
                ("b" * 64, "dataset-1"),
            )
