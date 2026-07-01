"""Emit Java stub text from a pruned symbol graph."""

from __future__ import annotations

from anchor_stubborn.graph.prune import PrunedGraph, PrunedSymbol
from anchor_stubborn.tokens import estimate_tokens
from anchor_stubborn.weave._shared import (
    kind_bucket,
    select_type_symbols,
    short_name,
    sort_key,
    trim_for_token_budget,
)
from anchor_stubborn.weave.types import WeaveResult

_METHOD_KINDS = frozenset({"method", "constructor", "abstractmethod", "staticmethod"})


def weave_java_stub(graph: PrunedGraph, *, max_tokens: int | None = None) -> WeaveResult:
    """Render pruned symbols as compact Java-like declarations (no method bodies)."""
    selected = select_type_symbols(graph.symbols, graph.target_stable_id)
    dropped = 0

    if max_tokens is not None:
        selected, dropped = trim_for_token_budget(
            selected,
            graph,
            max_tokens,
            weave_java_stub,
        )

    lines: list[str] = [
        "// Anchor-Stubborn context — declarations only, no method bodies",
        f"// target: {_short_name(graph.target_stable_id)}",
        "",
    ]

    type_symbols = [s for s in selected if kind_bucket(s) == "type"]
    other_symbols = [s for s in selected if kind_bucket(s) != "type"]

    for symbol in sorted(type_symbols, key=sort_key):
        header = _format_type_declaration(symbol)
        if header:
            lines.append(header)
            lines.append("")

    for symbol in sorted(other_symbols, key=sort_key):
        header = _format_member_declaration(symbol)
        if header:
            lines.append(header)
            lines.append("")

    stable_ids = {s.stable_id for s in selected}
    pruned_edges = [
        edge for edge in graph.edges if edge[0] in stable_ids and edge[1] in stable_ids
    ]
    if pruned_edges:
        lines.append("// --- dependencies ---")
        for from_id, to_id, edge_kind in sorted(pruned_edges):
            lines.append(f"// {edge_kind}: {_short_name(from_id)} -> {_short_name(to_id)}")

    text = "\n".join(lines).rstrip() + "\n"
    return WeaveResult(
        text=text,
        symbol_count=len(selected),
        estimated_tokens=estimate_tokens(text),
        dropped_for_budget=dropped,
    )


def _short_name(stable_id: str) -> str:
    return short_name(stable_id)


def _is_constructor(symbol: PrunedSymbol) -> bool:
    if (symbol.kind or "").lower() == "constructor":
        return True
    return "<init>" in symbol.stable_id or symbol.display_name == "<init>"


def _is_method(symbol: PrunedSymbol) -> bool:
    kind = (symbol.kind or "").lower()
    return kind in _METHOD_KINDS or "#" in symbol.stable_id and "(" in symbol.stable_id.split("#", 1)[-1]


def _is_annotation_only(symbol: PrunedSymbol) -> bool:
    signature = (symbol.signature or "").strip()
    if not signature.startswith("@"):
        return False
    lowered = signature.lower()
    return not any(
        keyword in lowered
        for keyword in (" class ", " interface ", " enum ", " record ", "class ", "\nclass ")
    )


def _format_type_declaration(symbol: PrunedSymbol) -> str | None:
    signature = (symbol.signature or symbol.display_name or _short_name(symbol.stable_id)).strip()
    if not signature or _is_annotation_only(symbol):
        return None
    if "{ /* stub */ }" in signature:
        return signature
    if signature.endswith("}"):
        return signature
    return f"{signature} {{ /* stub */ }}"


def _format_member_declaration(symbol: PrunedSymbol) -> str | None:
    if _is_constructor(symbol):
        return None

    signature = (symbol.signature or "").strip()
    if not signature:
        name = symbol.display_name or _short_name(symbol.stable_id)
        kind = (symbol.kind or "symbol").lower()
        if kind in _METHOD_KINDS:
            return f"// {kind}: {name};"
        return f"// {kind}: {name}"

    if _is_annotation_only(symbol):
        return None

    if signature.endswith(";") or signature.endswith("}"):
        return signature
    if (symbol.kind or "").lower() in _METHOD_KINDS:
        return f"{signature};"
    return signature
