from ssswet_core.persistence import SQLiteResearchStore


def _plan(store, sql, params=()):
    with store._connect() as connection:
        return " ".join(str(row["detail"]) for row in connection.execute(
            "EXPLAIN QUERY PLAN " + sql, params
        ).fetchall())


def test_collective_memory_unfiltered_order_uses_updated_index(tmp_path):
    store = SQLiteResearchStore(tmp_path / "query-plan.sqlite3")
    plan = _plan(
        store,
        "SELECT * FROM collective_memory ORDER BY updated_at DESC LIMIT ?",
        (100,),
    )
    assert "idx_collective_memory_updated" in plan
    assert "TEMP B-TREE" not in plan.upper()


def test_collective_memory_campaign_order_uses_compound_index(tmp_path):
    store = SQLiteResearchStore(tmp_path / "query-plan.sqlite3")
    plan = _plan(
        store,
        "SELECT * FROM collective_memory WHERE campaign_id = ? ORDER BY updated_at DESC LIMIT ?",
        ("campaign-a", 100),
    )
    assert "idx_collective_memory_campaign_updated" in plan
    assert "TEMP B-TREE" not in plan.upper()


def test_collective_memory_campaign_status_order_uses_compound_index(tmp_path):
    store = SQLiteResearchStore(tmp_path / "query-plan.sqlite3")
    plan = _plan(
        store,
        "SELECT * FROM collective_memory WHERE campaign_id = ? AND status = ? ORDER BY updated_at DESC LIMIT ?",
        ("campaign-a", "reviewed", 100),
    )
    assert "idx_collective_memory_campaign_status_updated" in plan
    assert "TEMP B-TREE" not in plan.upper()


def test_collective_memory_status_order_uses_compound_index(tmp_path):
    store = SQLiteResearchStore(tmp_path / "query-plan.sqlite3")
    plan = _plan(
        store,
        "SELECT * FROM collective_memory WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
        ("reviewed", 100),
    )
    assert "idx_collective_memory_status_updated" in plan
    assert "TEMP B-TREE" not in plan.upper()
