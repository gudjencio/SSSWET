from ssswet_core.models import ResearchEvent, Task, TaskStatus
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.pipeline import ResearchPipeline
from ssswet_core.providers import CorpusDocument, LocalCorpusProvider


def test_sqlite_store_persists_pipeline_runs_and_marks_outputs_unverified(tmp_path):
    database = tmp_path / "history.sqlite3"
    store = SQLiteResearchStore(database)
    provider = LocalCorpusProvider([
        CorpusDocument("doc-1", "Wave propagation", "Wave propagation is studied in physics.")
    ])
    pipeline = ResearchPipeline(provider=provider, store=store)

    task_id, steps = pipeline.start("Study wave propagation in physics", "physics")

    tasks = store.recent_tasks()
    assert len(tasks) == 1
    assert tasks[0]["task_id"] == task_id
    assert tasks[0]["status"] == TaskStatus.COMPLETE.value

    saved_steps = store.recent_steps()
    assert len(saved_steps) == len(steps) == 2
    assert all(item["classification"] == "unverified" for item in saved_steps)
    assert any("doc-1" in item["source_ids"] for item in saved_steps)

    event_kinds = {event["kind"] for event in store.recent_events(100)}
    assert "task_created" in event_kinds
    assert "group_created" in event_kinds
    assert "research_pass" in event_kinds


def test_store_updates_task_state_without_losing_database(tmp_path):
    store = SQLiteResearchStore(tmp_path / "state.sqlite3")
    task = Task(id="task-1", objective="Persist a checkpoint", status=TaskStatus.QUEUED)
    store.save_run(task, [ResearchEvent("checkpoint", "Initial checkpoint.", task.id)])

    task.status = TaskStatus.BLOCKED
    task.attempts = 1
    task.strategy_history.append("alternate")
    store.save_run(task, [ResearchEvent("blocked", "Task retained.", task.id)])

    tasks = store.recent_tasks()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "blocked"
    assert tasks[0]["strategy_history"] == ["alternate"]
    assert len(store.recent_events()) == 2


from ssswet_core.sources import SourceRecord


def test_source_registry_round_trip_and_doi_lookup(tmp_path):
    store = SQLiteResearchStore(tmp_path / "sources.sqlite3")
    source = SourceRecord(
        source_id="paper-a",
        title="A study",
        doi="10.1234/ABC",
        url="https://example.org/a",
        authors=("A. Researcher", "B. Scientist"),
        institutions=("Example University",),
        dataset_ids=("dataset-7",),
        related_source_ids=("paper-b",),
        provenance_group="lab-alpha",
        limitations=("small sample",),
    )
    store.register_source(source)
    loaded = store.get_source("paper-a")
    assert loaded["doi"] == "10.1234/ABC"
    assert loaded["authors"] == ["A. Researcher", "B. Scientist"]
    assert loaded["dataset_ids"] == ["dataset-7"]
    assert loaded["metadata"]["limitations"] == ["small sample"]
    assert store.find_sources_by_doi("https://doi.org/10.1234/abc")[0]["source_id"] == "paper-a"


def test_dependency_report_detects_shared_dataset_and_provenance(tmp_path):
    store = SQLiteResearchStore(tmp_path / "dependencies.sqlite3")
    store.register_source(SourceRecord(
        source_id="paper-a", title="A", dataset_ids=("shared-1",),
        provenance_group="lab-alpha",
    ))
    store.register_source(SourceRecord(
        source_id="paper-b", title="B", dataset_ids=("shared-1",),
        provenance_group="lab-alpha",
    ))
    report = store.source_dependency_report("paper-a")
    assert report["found"] is True
    assert report["dependencies"] == [{
        "source_id": "paper-b",
        "reasons": ["same_provenance_group", "shared_dataset:shared-1"],
    }]


def test_duplicate_doi_can_be_discovered_across_source_ids(tmp_path):
    store = SQLiteResearchStore(tmp_path / "duplicate.sqlite3")
    store.register_source(SourceRecord(source_id="crossref:1", title="Paper", doi="10.55/X"))
    store.register_source(SourceRecord(source_id="openalex:1", title="Paper", doi="10.55/x"))
    matches = store.find_sources_by_doi("10.55/x")
    assert {item["source_id"] for item in matches} == {"crossref:1", "openalex:1"}


def test_source_dependency_report_handles_unknown_source(tmp_path):
    store = SQLiteResearchStore(tmp_path / "missing.sqlite3")
    assert store.source_dependency_report("unknown") == {
        "source_id": "unknown", "found": False, "dependencies": [],
    }


def test_experiment_plan_and_records_persist_separately(tmp_path):
    from ssswet_core.experimentation import (
        draft_experiment_plan, make_experiment_record,
    )
    store = SQLiteResearchStore(tmp_path / "experiments.sqlite3")
    plan = draft_experiment_plan("exp-a", "hyp-a", "A measurable hypothesis")
    store.save_experiment_plan(plan)
    simulated = make_experiment_record(
        "sim-a", "exp-a", "simulation", {"result": 1.2}, "toy model"
    )
    observed = make_experiment_record(
        "obs-a", "exp-a", "real_observation", {"result": 1.1}, "instrument log"
    )
    store.save_experiment_record(simulated)
    store.save_experiment_record(observed)
    saved = store.get_experiment_plan("exp-a")
    records = store.experiment_records("exp-a")
    assert saved["state"] == "draft"
    assert {record["kind"] for record in records} == {"simulation", "real_observation"}
    assert len(store.experiment_overview()) == 1


def test_experiment_record_requires_existing_plan(tmp_path):
    from ssswet_core.experimentation import make_experiment_record
    store = SQLiteResearchStore(tmp_path / "orphan-record.sqlite3")
    record = make_experiment_record("record-a", "missing-plan", "simulation", {}, "model")
    try:
        store.save_experiment_record(record)
    except ValueError as exc:
        assert "plan must be saved" in str(exc)
    else:
        raise AssertionError("An orphan experiment record must be rejected")


def test_adaptive_cycle_history_persists_proposal_only_state(tmp_path):
    from ssswet_core.adaptive_cycle import propose_from_study
    from ssswet_core.simulation_study import MultiModelSimulationRunner, SimulationScenario

    study = MultiModelSimulationRunner().run(
        "persisted-study", "Toy study",
        [SimulationScenario("a", {"x": 0}), SimulationScenario("b", {"x": 1})],
        {
            "one": ("local", lambda p: {"score": p["x"]}),
            "two": ("local", lambda p: {"score": p["x"] + 1}),
        },
    )
    cycle = propose_from_study(
        study,
        [SimulationScenario("a", {"x": 0}), SimulationScenario("b", {"x": 1})],
        {"a": 0.0},
    )
    store = SQLiteResearchStore(tmp_path / "adaptive.sqlite3")
    store.save_adaptive_cycle("cycle-001", cycle)

    saved = store.get_adaptive_cycle("cycle-001")
    history = store.adaptive_cycle_history("persisted-study")
    assert saved["study_id"] == "persisted-study"
    assert saved["execution_state"] == "proposal_only"
    assert saved["requires_human_approval_before_execution"] is True
    assert history[0]["cycle_id"] == "cycle-001"



def test_autonomous_worker_heartbeat_round_trip(tmp_path):
    store = SQLiteResearchStore(tmp_path / "worker-state.sqlite3")
    state = {
        "worker": "autonomous_research",
        "status": "running",
        "current_technology": "cleanenergy",
        "completed_programmes": 7,
        "total_programmes": 32,
        "active_agents": [{"id": "bot-001", "role": "independent_verifier", "task_id": "task-1"}],
    }
    store.save_research_worker_state(state)

    loaded = store.research_worker_state()
    assert loaded["status"] == "running"
    assert loaded["current_technology"] == "cleanenergy"
    assert loaded["completed_programmes"] == 7
    assert loaded["active_agents"][0]["id"] == "bot-001"
    assert loaded["updated_at"]



def test_agent_messages_are_persisted_as_immutable_review_handoffs(tmp_path):
    import sqlite3
    store = SQLiteResearchStore(tmp_path / "agent-messages.sqlite3")
    message_id = store.publish_agent_message(
        task_id="task-peer",
        sender_agent_id="bot-researcher",
        sender_role="general_researcher",
        recipient_agent_id="bot-verifier",
        recipient_role="independent_verifier",
        message_type="peer_review_request",
        content="Please examine this unverified research summary.",
    )
    messages = store.recent_agent_messages(task_id="task-peer")
    assert len(messages) == 1
    assert messages[0]["id"] == message_id
    assert messages[0]["sender_agent_id"] == "bot-researcher"
    assert messages[0]["recipient_agent_id"] == "bot-verifier"
    assert messages[0]["review_state"] == "awaiting_review"
    with sqlite3.connect(store.path) as connection:
        try:
            connection.execute("UPDATE agent_messages SET content='approved' WHERE id=?", (message_id,))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Agent handoff history must be immutable")


def test_agent_message_rejects_self_delivery_and_empty_content(tmp_path):
    store = SQLiteResearchStore(tmp_path / "agent-message-validation.sqlite3")
    import pytest
    with pytest.raises(ValueError):
        store.publish_agent_message(
            task_id="t", sender_agent_id="same", sender_role="researcher",
            recipient_agent_id="same", recipient_role="researcher",
            message_type="peer_review_request", content="Review",
        )
    with pytest.raises(ValueError):
        store.publish_agent_message(
            task_id="t", sender_agent_id="a", sender_role="researcher",
            recipient_agent_id="b", recipient_role="verifier",
            message_type="peer_review_request", content=" ",
        )
