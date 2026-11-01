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
