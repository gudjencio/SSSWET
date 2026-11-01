import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

import pytest

from ssswet_core.priority_framework import (
    CRITERION_KEYS, framework_definition, rank_assessments, score_assessment,
)


def complete_scores(value=3):
    return {key: value for key in CRITERION_KEYS}


def test_framework_weights_sum_to_one_hundred_and_requires_human_review():
    framework = framework_definition()
    assert framework["weight_total"] == 100
    assert sum(item["weight"] for item in framework["criteria"]) == 100
    assert framework["human_review_required"] is True
    assert framework["scientific_validity_established"] is False


def test_complete_assessment_is_normalized_to_zero_to_one_hundred():
    result = score_assessment("clean-water", complete_scores(5))
    assert result["score"] == 100
    assert result["coverage_percent"] == 100
    assert result["rank_eligible"] is True


def test_incomplete_assessment_is_not_given_a_comparable_score():
    scores = complete_scores(4)
    scores["evidence_maturity"] = None
    result = score_assessment("clean-water", scores)
    assert result["score"] is None
    assert result["assessment_status"] == "incomplete"
    assert result["missing_criteria"] == ["evidence_maturity"]
    assert result["coverage_percent"] == 85


def test_ranking_excludes_incomplete_programmes_and_is_deterministic():
    incomplete = complete_scores(5)
    incomplete["safety_legal_readiness"] = None
    report = rank_assessments([
        {"programme_id": "zeta", "scores": complete_scores(4)},
        {"programme_id": "alpha", "scores": complete_scores(4)},
        {"programme_id": "not-ready", "scores": incomplete},
    ])
    assert [item["programme_id"] for item in report["ranked"]] == ["alpha", "zeta"]
    assert report["ranked"][0]["rank"] == 1
    assert report["incomplete"][0]["programme_id"] == "not-ready"
    assert report["automatic_funding_decisions"] is False


@pytest.mark.parametrize("value", [-1, 5.1, True, "4"])
def test_invalid_scores_are_rejected(value):
    scores = complete_scores()
    scores["technical_feasibility"] = value
    with pytest.raises(ValueError):
        score_assessment("test", scores)


def test_unknown_criteria_and_duplicate_programmes_are_rejected():
    with pytest.raises(ValueError, match="unknown criteria"):
        score_assessment("test", {"unlisted": 4})
    with pytest.raises(ValueError, match="unique"):
        rank_assessments([
            {"programme_id": "same", "scores": complete_scores()},
            {"programme_id": "same", "scores": complete_scores()},
        ])


def test_priority_framework_endpoint_is_read_only_and_explains_limits(tmp_path):
    from ssswet_core.engine import SSSWETEngine
    from ssswet_core.persistence import SQLiteResearchStore
    from ssswet_core.server import make_handler

    store = SQLiteResearchStore(tmp_path / "priority-framework.sqlite3")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(SSSWETEngine(store=store), store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/research-priority-framework") as response:
            payload = json.loads(response.read())
        assert payload["weight_total"] == 100
        assert payload["automatic_funding_decisions"] is False
        assert payload["scientific_validity_established"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
