import pytest

from ssswet_core.agent_identity import AgentIdentityRegistry, PROFILES
from ssswet_core.persistence import SQLiteResearchStore


def test_profiles_are_distinct_and_stable(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "identity.sqlite3"))
    first = registry.profile("independent_verifier")
    second = registry.profile("INDEPENDENT_VERIFIER")
    assert first == second
    assert first["name"] == "Elias Varenne"
    assert len(PROFILES) >= 8
    assert len({profile["name"] for profile in PROFILES.values()}) == len(PROFILES)


def test_memories_persist_with_provenance_and_are_append_only(tmp_path):
    store = SQLiteResearchStore(tmp_path / "identity.sqlite3")
    registry = AgentIdentityRegistry(store)
    item = registry.remember(
        agent_id="bot-001", role="general_researcher",
        content="The previous analysis identified an unresolved materials question.",
        source_reference="task:research-123",
    )
    assert registry.memories("bot-001")[0]["memory_id"] == item["memory_id"]
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute(
                "UPDATE agent_identity_memories SET content='fabricated' WHERE memory_id=?",
                (item["memory_id"],),
            )


def test_relationship_history_records_observable_events_not_emotions(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "identity.sqlite3"))
    record = registry.record_collaboration(
        agent_id="bot-001", other_agent_id="bot-002",
        event_type="disagreement", evidence_reference="task:review-42",
        note="Different interpretations were submitted for independent review.",
    )
    overview = registry.overview()
    assert record["event_type"] == "disagreement"
    assert overview["relationship_data_is_observational"] is True
    assert overview["persistent_agent_records"][0]["collaboration_history"][0]["observable_event"] == "disagreement"


def test_unknown_roles_and_unreferenced_memories_are_rejected(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "identity.sqlite3"))
    with pytest.raises(ValueError, match="unknown agent role"):
        registry.profile("invented_role")
    with pytest.raises(ValueError, match="source reference"):
        registry.remember(agent_id="bot-1", role="general_researcher", content="A note", source_reference="")


def test_memory_search_prioritizes_relevant_source_linked_notes(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "memory-search.sqlite3"))
    relevant = registry.remember(
        agent_id="bot-search", role="general_researcher",
        content="Black hole observation requires relativistic models and event-horizon imaging.",
        source_reference="doi:10.example/black-hole-review",
    )
    registry.remember(
        agent_id="bot-search", role="general_researcher",
        content="Regenerative agriculture can improve soil health and water retention.",
        source_reference="doi:10.example/agriculture-review",
    )
    ranked = registry.search_memories("bot-search", "black hole event horizon observation", limit=5)
    assert ranked
    assert ranked[0]["memory_id"] == relevant["memory_id"]
    assert ranked[0]["retrieval_method"] == "source_linked_lexical_relevance"
    assert ranked[0]["matched_terms"]


def test_team_memory_search_retrieves_across_agents_without_losing_provenance(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "team-memory.sqlite3"))
    mira = registry.remember(
        agent_id="mira-01", role="general_researcher",
        content="Thermal protection requires testing heat transfer and insulation ageing.",
        source_reference="doi:10.example/thermal-protection",
    )
    registry.remember(
        agent_id="asha-01", role="data_analyst",
        content="Urban water monitoring needs calibrated sensors and uncertainty estimates.",
        source_reference="doi:10.example/water-monitoring",
    )
    results = registry.search_team_memories("thermal protection insulation ageing", limit=5)
    assert results
    assert results[0]["memory_id"] == mira["memory_id"]
    assert results[0]["agent_id"] == "mira-01"
    assert results[0]["source_reference"] == "doi:10.example/thermal-protection"
    assert results[0]["retrieval_scope"] == "team"


def test_team_memory_search_validates_bounds_and_agent_filters(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "team-memory-validation.sqlite3"))
    with pytest.raises(ValueError, match="limit"):
        registry.search_team_memories("materials", limit=0)
    with pytest.raises(ValueError, match="agent_ids"):
        registry.search_team_memories("materials", agent_ids=[])


def test_memory_search_matches_accented_and_unaccented_terms(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "accent-search.sqlite3"))
    saved = registry.remember(
        agent_id="bot-accent", role="general_researcher",
        content="L’efficacité énergétique dépend de mesures répétables et de données fiables.",
        source_reference="doi:10.example/efficacite",
    )
    results = registry.search_memories(
        "bot-accent", "efficacite energetique donnees fiables", limit=5
    )
    assert results
    assert results[0]["memory_id"] == saved["memory_id"]
    assert "efficacite" in results[0]["matched_terms"]


def test_memory_review_state_is_visible_in_retrieval_and_append_only(tmp_path):
    store = SQLiteResearchStore(tmp_path / "memory-review.sqlite3")
    registry = AgentIdentityRegistry(store)
    memory = registry.remember(agent_id="mira-review", role="general_researcher",
        content="A coating retained adhesion after thermal cycling.",
        source_reference="doi:10.example/coating-test")
    initial = registry.search_memories("mira-review", "coating adhesion thermal cycling")[0]
    assert initial["source_review_status"] == "unreviewed"
    event = registry.record_memory_review(memory_id=memory["memory_id"],
        status="recheck_required", rationale="A newer standard may change the test method.",
        reviewer_id="elias", evidence_reference="standard:revision-notice")
    found = registry.search_team_memories("coating adhesion thermal cycling")[0]
    assert found["source_review_status"] == "recheck_required"
    assert found["source_review_reference"] == "standard:revision-notice"
    assert found["source_reviewed_by"] == "elias"
    with pytest.raises(Exception, match="append-only"):
        with store._connect() as connection:
            connection.execute("UPDATE agent_memory_review_events SET rationale='erased' WHERE event_id=?", (event["event_id"],))


def test_memory_review_transitions_require_existing_memory_and_preserve_history(tmp_path):
    registry = AgentIdentityRegistry(SQLiteResearchStore(tmp_path / "memory-review-flow.sqlite3"))
    memory = registry.remember(agent_id="asha-review", role="data_analyst",
        content="Sensor calibration drift was measured.", source_reference="dataset:calibration-1")
    with pytest.raises(ValueError, match="does not exist"):
        registry.record_memory_review(memory_id="missing", status="revalidated",
            rationale="Checked again.", reviewer_id="asha", evidence_reference="audit:1")
    registry.record_memory_review(memory_id=memory["memory_id"], status="recheck_required",
        rationale="Calibration protocol has changed.", reviewer_id="jun", evidence_reference="protocol:v2")
    registry.record_memory_review(memory_id=memory["memory_id"], status="revalidated",
        rationale="The original measurements were re-evaluated against the new protocol.",
        reviewer_id="asha", evidence_reference="audit:recheck-2")
    with pytest.raises(ValueError, match="invalid"):
        registry.record_memory_review(memory_id=memory["memory_id"], status="revalidated",
            rationale="Duplicate transition.", reviewer_id="asha", evidence_reference="audit:3")
    result = registry.search_memories("asha-review", "sensor calibration drift")[0]
    assert result["source_review_status"] == "revalidated"
    assert result["source_review_reference"] == "audit:recheck-2"
