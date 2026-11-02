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
