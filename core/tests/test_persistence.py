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
