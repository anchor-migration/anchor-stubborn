"""Emit Java stub text from a pruned symbol graph."""

from __future__ import annotations

from dataclasses import dataclass

from anchor_stubborn.graph.prune import PrunedGraph, PrunedSymbol
from anchor_stubborn.tokens import estimate_tokens

_TYPE_KINDS = frozenset({"class", "interface", "enum", "record"})
_METHOD_KINDS = frozenset({"method", "constructor", "abstractmethod", "staticmethod"})


@dataclass(frozen=True)
class WeaveResult:
    text: str
    symbol_count: int
    estimated_tokens: int
    dropped_for_budget: int = 0


def weave_java_stub(graph: PrunedGraph, *, max_tokens: int | None = None) -> WeaveResult:
    """Render pruned symbols as compact Java-like declarations (no method bodies)."""
    selected = _select_symbols(graph.symbols, graph.target_stable_id)
    dropped = 0

    if max_tokens is not None:
        selected, dropped = _trim_for_token_budget(selected, graph, max_tokens)

    lines: list[str] = [
        "// Anchor-Stubborn context — declarations only, no method bodies",
        f"// target: {_short_name(graph.target_stable_id)}",
        "",
    ]

    type_symbols = [s for s in selected if _kind_bucket(s) == "type"]
    other_symbols = [s for s in selected if _kind_bucket(s) != "type"]

    for symbol in sorted(type_symbols, key=_sort_key):
        header = _format_type_declaration(symbol)
        if header:
            lines.append(header)
            lines.append("")

    for symbol in sorted(other_symbols, key=_sort_key):
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


def _trim_for_token_budget(
    symbols: list[PrunedSymbol],
    graph: PrunedGraph,
    max_tokens: int,
) -> tuple[list[PrunedSymbol], int]:
    selected = list(symbols)
    dropped = 0
    target_id = graph.target_stable_id

    while selected:
        preview = weave_java_stub(
            PrunedGraph(target_stable_id=graph.target_stable_id, symbols=selected, edges=graph.edges),
            max_tokens=None,
        )
        if preview.estimated_tokens <= max_tokens:
            return selected, dropped

        removable = [s for s in selected if s.stable_id != target_id]
        if not removable:
            return selected, dropped

        removable.sort(key=lambda s: (-s.depth, s.stable_id))
        selected.remove(removable[0])
        dropped += 1

    return selected, dropped


def _select_symbols(symbols: list[PrunedSymbol], target_stable_id: str) -> list[PrunedSymbol]:
    selected: list[PrunedSymbol] = []
    for symbol in symbols:
        if _is_annotation_only(symbol):
            continue
        if _kind_bucket(symbol) != "type":
            continue
        if _is_enum_constant(symbol):
            continue
        selected.append(symbol)

    if not any(s.stable_id == target_stable_id for s in selected):
        for symbol in symbols:
            if symbol.stable_id == target_stable_id:
                selected.insert(0, symbol)
                break

    return selected


def _is_enum_constant(symbol: PrunedSymbol) -> bool:
    if not symbol.stable_id.endswith("#"):
        return False
    suffix = symbol.stable_id.split("#", 1)[-1]
    return bool(suffix)


def _kind_bucket(symbol: PrunedSymbol) -> str:
    kind = (symbol.kind or "").lower()
    if kind in _TYPE_KINDS or symbol.stable_id.endswith("#"):
        return "type"
    return "member"


def _sort_key(symbol: PrunedSymbol) -> tuple[int, str]:
    return (symbol.depth, symbol.stable_id)


def _short_name(stable_id: str) -> str:
    if " " in stable_id:
        return stable_id.split(" ", 1)[1]
    if "#" in stable_id:
        return stable_id.split("#", 1)[-1] or stable_id
    return stable_id


def _enclosing_type_id(stable_id: str) -> str:
    if "#" not in stable_id:
        return stable_id
    return stable_id.split("#", 1)[0] + "#"


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
