"""Read symbol graph data from SQLite."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SymbolRecord:
    stable_id: str
    display_name: str | None
    kind: str | None
    signature: str | None


def resolve_db_path(db_path: str | Path | None) -> Path:
    """Resolve DB path from argument or ANCHOR_STUBBORN_DB environment variable."""
    if db_path is not None:
        path = Path(db_path)
    else:
        env = os.environ.get("ANCHOR_STUBBORN_DB")
        if not env:
            raise ValueError(
                "db_path is required (or set ANCHOR_STUBBORN_DB to the symbol graph SQLite file)"
            )
        path = Path(env)
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def _latest_index_run_id(conn: sqlite3.Connection, index_run_id: int | None) -> int:
    if index_run_id is not None:
        return index_run_id
    row = conn.execute("SELECT id FROM index_run ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        raise ValueError("No index runs found in database")
    return int(row[0])


def list_symbols(
    db_path: str | Path,
    *,
    query: str | None = None,
    kind: str | None = None,
    limit: int = 50,
    index_run_id: int | None = None,
) -> list[SymbolRecord]:
    """List symbols from the latest (or specific) index run."""
    if limit < 1:
        raise ValueError("limit must be >= 1")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        run_id = _latest_index_run_id(conn, index_run_id)
        sql = """
            SELECT stable_id, display_name, kind, signature
            FROM scip_symbol
            WHERE index_run_id = ?
        """
        params: list[object] = [run_id]

        if query:
            pattern = f"%{query}%"
            sql += " AND (stable_id LIKE ? OR display_name LIKE ? OR signature LIKE ?)"
            params.extend([pattern, pattern, pattern])

        if kind:
            sql += " AND kind = ?"
            params.append(kind)

        sql += " ORDER BY stable_id LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [
            SymbolRecord(
                stable_id=row["stable_id"],
                display_name=row["display_name"],
                kind=row["kind"],
                signature=row["signature"],
            )
            for row in rows
        ]
    finally:
        conn.close()
