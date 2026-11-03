from ssswet_core.localization_quality import audit_translation_catalogue


def test_localization_audit_reports_coverage_and_missing_keys():
    report = audit_translation_catalogue({"a": "A", "b": "B"}, {"en": {"a": "A", "b": "B"}, "fr": {"a": "Un"}})
    assert report["en"]["coverage"] == 1.0
    assert report["fr"]["coverage"] == 0.5
    assert report["fr"]["missing"] == ["b"]
