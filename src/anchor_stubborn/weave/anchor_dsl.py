"""Emit Anchor-DSL v1 text from a pruned symbol graph."""

from __future__ import annotations

import re

from anchor_stubborn.graph.prune import PrunedGraph, PrunedSymbol
from anchor_stubborn.tokens import estimate_tokens
from anchor_stubborn.weave._shared import (
    is_annotation_only,
    kind_bucket,
    select_type_symbols,
    short_name,
    short_target_name,
    sort_key,
    trim_for_token_budget,
)
from anchor_stubborn.weave.anchor_dsl_llm import LLM_GUIDE_LINES
from anchor_stubborn.weave.members import method_members_for_type, normalize_method_signature
from anchor_stubborn.weave.types import WeaveResult

_ANCHOR_DSL_VERSION = "1.0"
_ANNOTATION_RE = re.compile(r"@[\w.]+(?:\([^)]*\))?")
_TYPE_DECL_RE = re.compile(r"\b(class|interface|enum|record)\s+(\w+)")
_METHOD_KINDS = frozenset({"method", "constructor", "abstractmethod", "staticmethod"})
_KIND_CODES = {
    "class": "c",
    "interface": "i",
    "enum": "e",
    "record": "r",
}
_EDGE_ABBREV = {
    "reference": "ref",
    "type": "type",
    "implementation": "impl",
    "definition": "def",
}


def weave_anchor_dsl(graph: PrunedGraph, *, max_tokens: int | None = None) -> WeaveResult:
    """Render pruned symbols as compact Anchor-DSL v1 (declarations only)."""
    selected = select_type_symbols(graph.symbols, graph.target_stable_id)
    dropped = 0

    if max_tokens is not None:
        selected, dropped = trim_for_token_budget(
            selected,
            graph,
            max_tokens,
            weave_anchor_dsl,
        )

    target_label = short_target_name(graph.target_stable_id)
    lines: list[str] = [
        f"anchor-dsl/{_ANCHOR_DSL_VERSION}",
        *LLM_GUIDE_LINES,
        f"target {target_label}",
        "policy declarations-only",
        "",
    ]

    target_symbol = next(
        (s for s in graph.symbols if s.stable_id == graph.target_stable_id),
        None,
    )
    if target_symbol is not None and _is_method_like(target_symbol):
        member_line = _format_member_line(target_symbol)
        if member_line:
            lines.append(member_line)
            lines.append("")

    type_symbols = [s for s in selected if kind_bucket(s) == "type"]

    if type_symbols:
        lines.append("types:")
        for symbol in sorted(type_symbols, key=sort_key):
            type_line = _format_type_line(symbol)
            if type_line:
                lines.append(f"  {type_line}")
        lines.append("")

    target_type_id = graph.target_stable_id if graph.target_stable_id.endswith("#") else None
    if target_type_id:
        type_methods = method_members_for_type(graph.symbols, target_type_id)
        if type_methods:
            lines.append("members:")
            for method in type_methods:
                label = short_target_name(method.stable_id)
                sig = normalize_method_signature(method)
                lines.append(f"  m {label} {sig}")
            lines.append("")

    stable_ids = {s.stable_id for s in selected}
    if target_symbol is not None and _is_method_like(target_symbol):
        stable_ids.add(target_symbol.stable_id)

    pruned_edges = [
        edge for edge in graph.edges if edge[0] in stable_ids and edge[1] in stable_ids
    ]
    if pruned_edges:
        lines.append("edges:")
        for from_id, to_id, edge_kind in sorted(pruned_edges):
            abbrev = _EDGE_ABBREV.get(edge_kind, edge_kind)
            lines.append(
                f"  {abbrev} {short_target_name(from_id)} -> {short_target_name(to_id)}"
            )

    text = "\n".join(lines).rstrip() + "\n"
    return WeaveResult(
        text=text,
        symbol_count=len(selected) + (1 if target_symbol and _is_method_like(target_symbol) else 0),
        estimated_tokens=estimate_tokens(text),
        dropped_for_budget=dropped,
    )


def _is_method_like(symbol: PrunedSymbol) -> bool:
    kind = (symbol.kind or "").lower()
    if kind in _METHOD_KINDS:
        return True
    if "#" in symbol.stable_id:
        member = symbol.stable_id.split("#", 1)[1]
        return "(" in member
    return False


def _kind_code(symbol: PrunedSymbol) -> str:
    kind = (symbol.kind or "").lower()
    if kind in _KIND_CODES:
        return _KIND_CODES[kind]
    signature = (symbol.signature or "").lower()
    for keyword, code in _KIND_CODES.items():
        if keyword in signature:
            return code
    return "c"


def _extract_annotations(signature: str) -> str:
    return " ".join(_ANNOTATION_RE.findall(signature))


def _extract_type_name(symbol: PrunedSymbol) -> str:
    signature = symbol.signature or ""
    match = _TYPE_DECL_RE.search(signature)
    if match:
        return match.group(2)
    return symbol.display_name or short_name(symbol.stable_id).split("(", 1)[0] or "Unknown"


def _normalize_signature(signature: str) -> str:
    text = " ".join(signature.split())
    for prefix in ("public ", "protected ", "private ", "static ", "final ", "abstract "):
        while text.startswith(prefix):
            text = text[len(prefix) :]
    return text


def _format_type_line(symbol: PrunedSymbol) -> str | None:
    if is_annotation_only(symbol):
        return None

    name = _extract_type_name(symbol)
    code = _kind_code(symbol)
    annotations = _extract_annotations(symbol.signature or "")
    if annotations:
        return f"{code} {name} {annotations}".rstrip()
    return f"{code} {name}"


def _format_member_line(symbol: PrunedSymbol) -> str | None:
    if (symbol.kind or "").lower() == "constructor":
        return None

    signature = _normalize_signature((symbol.signature or "").strip())
    if not signature:
        name = short_target_name(symbol.stable_id)
        return f"member m {name}"

    label = short_target_name(symbol.stable_id)
    return f"member m {label} {signature}"
