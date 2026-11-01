from ssswet_core.knowledge_graph import KnowledgeEdge, KnowledgeNode
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_gaps import ResearchGapAnalyzer


def add_node(store, node_id, kind, state="unverified"):
    store.add_knowledge_node(KnowledgeNode(
        node_id=node_id, node_type=kind, label=node_id,
        verification_state=state,
    ))


def test_gap_analyzer_finds_missing_support_tests_and_pending_verification(tmp_path):
    store = SQLiteResearchStore(tmp_path / "gaps.sqlite3")
    add_node(store, "hypothesis-a", "hypothesis")
    report = ResearchGapAnalyzer().report(store.knowledge_graph())
    categories = {gap["category"] for gap in report["gaps"]}
    assert {"missing_support", "untested_hypothesis", "verification_pending"} <= categories
    assert report["priority_counts"]["high"] == 1
    assert "not proof" in report["notice"]


def test_gap_analyzer_flags_unresolved_support_and_contradiction(tmp_path):
    store = SQLiteResearchStore(tmp_path / "conflict.sqlite3")
    add_node(store, "hypothesis", "hypothesis")
    add_node(store, "paper-1", "source")
    add_node(store, "paper-2", "source")
    store.add_knowledge_edge(KnowledgeEdge("paper-1", "hypothesis", "supports"))
    store.add_knowledge_edge(KnowledgeEdge("paper-2", "hypothesis", "contradicts"))
    gaps = ResearchGapAnalyzer().analyze(store.knowledge_graph())
    assert "unresolved_contradiction" in {gap.category for gap in gaps}
    assert "missing_support" not in {gap.category for gap in gaps}


def test_gap_analyzer_finds_unanswered_questions_and_orphan_findings(tmp_path):
    store = SQLiteResearchStore(tmp_path / "orphan-findings.sqlite3")
    add_node(store, "question", "question")
    add_node(store, "finding", "finding")
    gaps = ResearchGapAnalyzer().analyze(store.knowledge_graph())
    assert {gap.category for gap in gaps} == {
        "unanswered_question", "finding_without_provenance"
    }


def test_gap_analyzer_respects_recorded_experiment_and_verification(tmp_path):
    store = SQLiteResearchStore(tmp_path / "complete-links.sqlite3")
    add_node(store, "hypothesis", "hypothesis", "independently_verified")
    add_node(store, "paper", "source")
    add_node(store, "experiment", "experiment")
    store.add_knowledge_edge(KnowledgeEdge("paper", "hypothesis", "supports"))
    store.add_knowledge_edge(KnowledgeEdge("experiment", "hypothesis", "tests"))
    gaps = ResearchGapAnalyzer().analyze(store.knowledge_graph())
    assert not any(g.category in {
        "missing_support", "untested_hypothesis", "verification_pending"
    } for g in gaps)


def test_gap_analyzer_does_not_mutate_graph_state(tmp_path):
    store = SQLiteResearchStore(tmp_path / "immutable-state.sqlite3")
    add_node(store, "hypothesis", "hypothesis", "candidate")
    before = store.knowledge_graph()["nodes"][0]["verification_state"]
    ResearchGapAnalyzer().report(store.knowledge_graph())
    after = store.knowledge_graph()["nodes"][0]["verification_state"]
    assert before == after == "candidate"
