"""Bounded missing-value profiling for tabular research data."""
from __future__ import annotations

def analyze(rows: list[dict], columns: list[str] | None = None, max_rows: int = 100_000) -> dict:
    if not isinstance(rows, list) or not isinstance(max_rows, int) or max_rows < 1 or len(rows) > max_rows:
        raise ValueError("rows must be a list within the configured positive max_rows limit")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("each row must be a dictionary")
    if columns is None:
        columns = sorted({key for row in rows for key in row})
    if not isinstance(columns, list) or len(columns) > 5000 or any(not isinstance(c, str) or not c for c in columns):
        raise ValueError("columns must contain at most 5000 non-empty names")
    if len(set(columns)) != len(columns):
        raise ValueError("columns must be unique")
    result = {}
    for column in columns:
        missing = sum(1 for row in rows if column not in row or row[column] is None or row[column] == "")
        result[column] = {"missing_count": missing, "observed_count": len(rows) - missing, "missing_rate": missing / len(rows) if rows else 0.0}
    incomplete = sum(1 for row in rows if any(c not in row or row[c] is None or row[c] == "" for c in columns))
    return {"row_count": len(rows), "column_count": len(columns), "columns": result, "incomplete_row_count": incomplete, "data_modified": False}
