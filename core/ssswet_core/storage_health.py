"""Read-only SQLite health inspection and verified, no-overwrite backups."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import os
import sqlite3
import tempfile

def _readonly_connection(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise ValueError("database file does not exist")
    return sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True, timeout=2.0)

def inspect_sqlite(path: str | Path) -> dict:
    database = Path(path)
    connection = _readonly_connection(database)
    try:
        integrity = [row[0] for row in connection.execute("PRAGMA quick_check").fetchall()]
        page_count = connection.execute("PRAGMA page_count").fetchone()[0]
        freelist_count = connection.execute("PRAGMA freelist_count").fetchone()[0]
        page_size = connection.execute("PRAGMA page_size").fetchone()[0]
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        table_counts = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            sampled = connection.execute(f"SELECT 1 FROM {quoted} LIMIT 1001").fetchall()
            exact = len(sampled) <= 1000
            table_counts.append({"table": table, "row_count": len(sampled) if exact else None,
                                 "sampled_at_least_1001": not exact, "sample_limit": 1000})
        return {
            "database_exists": True, "integrity_check": integrity, "integrity_ok": integrity == ["ok"],
            "page_count": page_count, "freelist_pages": freelist_count, "page_size_bytes": page_size,
            "allocated_page_bytes": page_count * page_size, "file_size_bytes": database.stat().st_size,
            "journal_mode": journal_mode, "user_version": user_version, "tables": table_counts,
            "table_count": len(tables), "database_rows_or_content_exposed": False, "mutated": False,
        }
    finally:
        connection.close()

def backup_sqlite(source_path: str | Path, destination_path: str | Path) -> dict:
    source, destination = Path(source_path), Path(destination_path)
    if source.resolve() == destination.resolve():
        raise ValueError("backup destination must differ from source")
    if destination.exists():
        raise FileExistsError("backup destination already exists; backups are never overwritten")
    if not destination.parent.is_dir():
        raise ValueError("backup destination directory must already exist")
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    os.close(temp_fd)
    temporary = Path(temp_name)
    try:
        source_connection = _readonly_connection(source)
        target_connection = sqlite3.connect(temporary)
        try:
            source_connection.backup(target_connection)
            check = [row[0] for row in target_connection.execute("PRAGMA quick_check").fetchall()]
        finally:
            target_connection.close()
            source_connection.close()
        if check != ["ok"]:
            raise RuntimeError("backup integrity verification failed")
        digest = sha256(temporary.read_bytes()).hexdigest()
        try:
            os.link(temporary, destination)
        except FileExistsError:
            raise
        except OSError:
            descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                with os.fdopen(descriptor, "wb") as output, temporary.open("rb") as source_file:
                    while chunk := source_file.read(1024 * 1024):
                        output.write(chunk)
                    output.flush()
                    os.fsync(output.fileno())
            except Exception:
                destination.unlink(missing_ok=True)
                raise
        temporary.unlink()
        return {
            "backup_path": str(destination), "sha256": digest, "size_bytes": destination.stat().st_size,
            "integrity_check": check, "verified": True, "source_modified": False,
            "existing_backup_overwritten": False, "automatic_retention_deletion": False,
        }
    finally:
        if temporary.exists():
            temporary.unlink()
