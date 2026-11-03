from ssswet_core.evidence_freshness import score as freshness
from ssswet_core.source_independence import group_sources
from ssswet_core.consensus_matrix import build as consensus
from ssswet_core.reproducibility_gap import inspect
from ssswet_core.decision_trace import normalize
from ssswet_core.research_stop_conditions import should_stop
from ssswet_core.agent_load_balancer import rank
from ssswet_core.observation_quality import assess as observation
from ssswet_core.rescue_readiness import assess as rescue
from ssswet_core.virtual_time_confidence import assess as temporal


def test_freshness_half_life():
    assert 0.49 < freshness(30) < 0.51


def test_source_groups_are_deterministic():
    assert group_sources([{"id": "b", "publisher": "X"}, {"id": "a", "publisher": "X"}])["x"] == ["a", "b"]


def test_consensus_counts_normalized_values():
    result = consensus([{"subject": "A", "value": "Yes"}, {"subject": "a", "value": "yes"}])
    assert result["counts"]["a"]["yes"] == 2


def test_reproducibility_gap_is_explicit():
    result = inspect({"protocol_id": "p"})
    assert not result["complete"]
    assert "software_version" in result["missing_fields"]


def test_decision_trace_is_bounded():
    result = normalize([{"type": "review", "decision": "hold"}], max_events=1)
    assert result[0]["sequence"] == 0


def test_stop_conditions_prevent_unbounded_loops():
    assert should_stop(iterations=10, max_iterations=10)["stop"]


def test_load_balancer_prefers_low_load():
    result = rank([{"id": "a", "capabilities": ["x"], "load": 2}, {"id": "b", "capabilities": ["x"], "load": 1}], "x")
    assert result[0]["id"] == "b"


def test_observation_quality_reports_missing_fields():
    assert observation({"source_id": "s"})["score"] == 1 / 3


def test_rescue_readiness_requires_human_dispatch():
    result = rescue({})
    assert not result["ready_for_human_review"]
    assert not result["automated_dispatch"]


def test_virtual_time_confidence_is_observation_bounded():
    result = temporal([{"source_id": "s", "timestamp": "1"}] * 10)
    assert result["label"] == "medium"
    assert not result["unrecorded_history_recovered"]
