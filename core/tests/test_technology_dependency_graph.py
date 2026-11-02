import pytest

from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.technology_dossier import TechnologyDossierRegistry
from ssswet_core.technology_dependency_graph import TechnologyDependencyGraph


def make_graph(tmp_path):
    store = SQLiteResearchStore(tmp_path / "dependencies.sqlite3")
    dossiers = TechnologyDossierRegistry(store)
    for technology_id in ("power", "materials", "propulsion"):
        dossiers.create(technology_id=technology_id, title=technology_id.title(),
                        domain="engineering", actor_id="test")
    return TechnologyDependencyGraph(store)


def test_relations_start_as_proposals_and_keep_history(tmp_path):
    graph = make_graph(tmp_path)
    relation = graph.add_relation(
        prerequisite_id="power", dependent_id="propulsion",
        relation_type="prerequisite", rationale="Candidate dependency to investigate.",
        actor_id="researcher",
    )
    assert relation["state"] == "proposed"
    supported = graph.review_relation(
        relation_id=relation["relation_id"], state="supported",
        rationale="Independent review supports the dependency.",
        actor_id="reviewer", verifier_actor_id="independent",
        source_refs=["doi:10.example/source"],
    )
    assert supported["state"] == "supported"
    assert [event["state"] for event in supported["history"]] == ["proposed", "supported"]
    assert graph.graph()["supported_count"] == 1


def test_supported_edges_require_sources_and_independent_verifier(tmp_path):
    graph = make_graph(tmp_path)
    relation = graph.add_relation(
        prerequisite_id="power", dependent_id="propulsion",
        relation_type="prerequisite", rationale="Candidate", actor_id="researcher",
    )
    with pytest.raises(ValueError, match="source references"):
        graph.review_relation(relation_id=relation["relation_id"], state="supported",
                              rationale="Review", actor_id="reviewer",
                              verifier_actor_id="independent")
    with pytest.raises(ValueError, match="distinct independent verifier"):
        graph.review_relation(relation_id=relation["relation_id"], state="supported",
                              rationale="Review", actor_id="reviewer",
                              verifier_actor_id="reviewer", source_refs=["source:1"])


def test_supported_prerequisite_graph_rejects_cycles(tmp_path):
    graph = make_graph(tmp_path)
    first = graph.add_relation(
        prerequisite_id="power", dependent_id="materials",
        relation_type="prerequisite", rationale="Candidate 1", actor_id="researcher",
    )
    graph.review_relation(relation_id=first["relation_id"], state="supported",
                          rationale="Verified 1", actor_id="reviewer",
                          verifier_actor_id="independent", source_refs=["source:1"])
    second = graph.add_relation(
        prerequisite_id="materials", dependent_id="propulsion",
        relation_type="prerequisite", rationale="Candidate 2", actor_id="researcher",
    )
    graph.review_relation(relation_id=second["relation_id"], state="supported",
                          rationale="Verified 2", actor_id="reviewer",
                          verifier_actor_id="independent", source_refs=["source:2"])
    closing = graph.add_relation(
        prerequisite_id="propulsion", dependent_id="power",
        relation_type="prerequisite", rationale="Potential cycle", actor_id="researcher",
    )
    with pytest.raises(ValueError, match="cycle"):
        graph.review_relation(relation_id=closing["relation_id"], state="supported",
                              rationale="Review", actor_id="reviewer",
                              verifier_actor_id="independent", source_refs=["source:3"])
    assert graph.get_relation(closing["relation_id"])["state"] == "proposed"


def test_graph_rejects_unknown_nodes_and_self_edges(tmp_path):
    graph = make_graph(tmp_path)
    with pytest.raises(ValueError, match="unknown technology"):
        graph.add_relation(prerequisite_id="missing", dependent_id="power",
                           relation_type="prerequisite", rationale="No node",
                           actor_id="researcher")
    with pytest.raises(ValueError, match="itself"):
        graph.add_relation(prerequisite_id="power", dependent_id="power",
                           relation_type="informs", rationale="Self",
                           actor_id="researcher")


def test_rejected_relations_remain_in_history_but_are_not_supported(tmp_path):
    graph = make_graph(tmp_path)
    relation = graph.add_relation(
        prerequisite_id="power", dependent_id="propulsion",
        relation_type="enables", rationale="Initial proposal", actor_id="researcher",
    )
    graph.review_relation(relation_id=relation["relation_id"], state="rejected",
                          rationale="Evidence does not support this relation.",
                          actor_id="reviewer", source_refs=["source:negative"])
    assert graph.graph()["rejected_count"] == 1
    assert graph.graph(include_unverified=False)["relation_count"] == 0
