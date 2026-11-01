from ssswet_core.engine import SSSWETEngine
from ssswet_core.memory import MemoryItem
from ssswet_core.persistence import SQLiteResearchStore


def test_engine_restores_shared_knowledge_and_preserves_validation_state(tmp_path):
    store = SQLiteResearchStore(tmp_path / "knowledge.sqlite3")
    first = SSSWETEngine(store=store)
    candidate = MemoryItem(
        key="candidate-1",
        statement="A candidate result awaiting independent verification.",
        source="local-corpus:doc-1",
        validated=False,
    )
    verified = MemoryItem(
        key="verified-1",
        statement="A result supported by completed independent checks.",
        source="reproduction:run-42",
        validated=True,
    )
    first.remember_knowledge(candidate)
    first.remember_knowledge(verified)

    restarted = SSSWETEngine(store=SQLiteResearchStore(tmp_path / "knowledge.sqlite3"))
    assert restarted.memory.search("candidate")[0].validated is False
    assert restarted.memory.validated()[0].key == "verified-1"
    assert len(restarted.memory.export()) == 2
