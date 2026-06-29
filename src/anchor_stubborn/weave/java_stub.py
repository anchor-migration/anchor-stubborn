"""Emit Java stub text from a pruned symbol graph."""

from __future__ import annotations

from anchor_stubborn.graph.prune import PrunedGraph


def weave_java_stub(graph: PrunedGraph) -> str:
    """Render pruned symbols as compact Java-like declarations (no method bodies)."""
    lines: list[str] = [
        "// Anchor-Stubborn context — declarations only, no method bodies",
        f"// target: {graph.target_stable_id}",
        "",
    ]

    for symbol in sorted(graph.symbols, key=lambda s: s.stable_id):
        header = _format_symbol_header(symbol)
        if header:
            lines.append(header)
            lines.append("")

    if graph.edges:
        lines.append("// --- dependencies ---")
        for from_id, to_id, edge_kind in sorted(graph.edges):
            lines.append(f"// {edge_kind}: {_short_name(from_id)} -> {_short_name(to_id)}")

    return "\n".join(lines).rstrip() + "\n"


def _short_name(stable_id: str) -> str:
    marker = " "
    if marker in stable_id:
        return stable_id.split(marker, 1)[1]
    return stable_id


def _format_symbol_header(symbol) -> str:
    kind = (symbol.kind or "symbol").lower()
    name = symbol.display_name or _short_name(symbol.stable_id)
    signature = symbol.signature or name

    if kind in ("class", "interface", "enum", "record"):
        return f"{signature} {{ /* stub */ }}"
    if kind in ("method", "constructor"):
        return f"{signature};"
    if kind in ("field", "property"):
        return f"{signature};"
    return f"// {kind}: {signature}"
