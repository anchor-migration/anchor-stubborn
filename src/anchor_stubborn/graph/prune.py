"""Graph pruning for bounded LLM context."""

from __future__ import annotations

import sqlite3
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from anchor_stubborn.config import ContextBudget, DEFAULT_CONTEXT_BUDGET


@dataclass(frozen=True)
class PrunedSymbol:
    stable_id: str
    display_name: str | None
    kind: str | None
    signature: str | None
    documentation: str | None
    depth: int


@dataclass
class PrunedGraph:
    target_stable_id: str
    symbols: list[PrunedSymbol]
    edges: list[tuple[str, str, str]]


def _should_exclude(stable_id: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in stable_id for pattern in patterns)


def prune_context(
    db_path: str | Path,
    target_stable_id: str,
    budget: ContextBudget | None = None,
    *,
    index_run_id: int | None = None,
) -> PrunedGraph:
    """BFS prune from target symbol using call/type edge kinds."""
    budget = budget or DEFAULT_CONTEXT_BUDGET
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if index_run_id is None:
            row = conn.execute(
                "SELECT id FROM index_run ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row is None:
                raise ValueError(f"No index runs found in {db_path}")
            index_run_id = row["id"]

        symbols_by_id: dict[int, sqlite3.Row] = {}
        stable_to_id: dict[str, int] = {}
        for row in conn.execute(
            """
            SELECT id, stable_id, display_name, kind, signature, documentation
            FROM scip_symbol
            WHERE index_run_id = ?
            """,
            (index_run_id,),
        ):
            symbols_by_id[row["id"]] = row
            stable_to_id[row["stable_id"]] = row["id"]

        if target_stable_id not in stable_to_id:
            raise ValueError(f"Symbol not found in index: {target_stable_id}")

        adjacency: dict[int, list[tuple[int, str]]] = {}
        for row in conn.execute(
            """
            SELECT from_symbol_id, to_symbol_id, edge_kind
            FROM scip_edge
            WHERE index_run_id = ?
            """,
            (index_run_id,),
        ):
            adjacency.setdefault(row["from_symbol_id"], []).append(
                (row["to_symbol_id"], row["edge_kind"])
            )
            adjacency.setdefault(row["to_symbol_id"], []).append(
                (row["from_symbol_id"], row["edge_kind"])
            )

        start_id = stable_to_id[target_stable_id]
        seen: dict[int, int] = {start_id: 0}
        queue: deque[int] = deque([start_id])

        while queue and len(seen) < budget.max_symbols:
            current_id = queue.popleft()
            current_depth = seen[current_id]
            for neighbor_id, edge_kind in adjacency.get(current_id, []):
                if neighbor_id in seen:
                    continue

                neighbor = symbols_by_id[neighbor_id]
                if _should_exclude(neighbor["stable_id"], budget.exclude_patterns):
                    continue

                limit = budget.call_closure_depth
                if edge_kind in ("type", "implementation"):
                    limit = budget.type_closure_depth or budget.max_symbols

                if limit is not None and current_depth + 1 > limit:
                    continue

                seen[neighbor_id] = current_depth + 1
                queue.append(neighbor_id)

        pruned_symbols: list[PrunedSymbol] = []
        for symbol_id, depth in sorted(seen.items(), key=lambda item: item[1]):
            row = symbols_by_id[symbol_id]
            pruned_symbols.append(
                PrunedSymbol(
                    stable_id=row["stable_id"],
                    display_name=row["display_name"],
                    kind=row["kind"],
                    signature=row["signature"],
                    documentation=row["documentation"],
                    depth=depth,
                )
            )

        stable_ids = {s.stable_id for s in pruned_symbols}
        pruned_edges: list[tuple[str, str, str]] = []
        for row in conn.execute(
            """
            SELECT fs.stable_id, ts.stable_id, e.edge_kind
            FROM scip_edge e
            JOIN scip_symbol fs ON fs.id = e.from_symbol_id
            JOIN scip_symbol ts ON ts.id = e.to_symbol_id
            WHERE e.index_run_id = ?
            """,
            (index_run_id,),
        ):
            if row[0] in stable_ids and row[1] in stable_ids:
                pruned_edges.append((row[0], row[1], row[2]))

        return PrunedGraph(
            target_stable_id=target_stable_id,
            symbols=pruned_symbols,
            edges=pruned_edges,
        )
    finally:
        conn.close()
