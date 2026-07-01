"""Method signature helpers for weavers (v0.9)."""

from __future__ import annotations

from anchor_stubborn.graph.prune import PrunedSymbol
from anchor_stubborn.weave._shared import sort_key

_METHOD_KINDS = frozenset({"method", "abstractmethod", "staticmethod"})


def enclosing_type_stable_id(stable_id: str) -> str | None:
    if not stable_id.endswith("#") and "#" in stable_id:
        return stable_id.split("#", 1)[0] + "#"
    if stable_id.endswith("#"):
        return stable_id
    return None


def is_constructor_symbol(symbol: PrunedSymbol) -> bool:
    if (symbol.kind or "").lower() == "constructor":
        return True
    return "<init>" in symbol.stable_id or symbol.display_name == "<init>"


def is_method_symbol(symbol: PrunedSymbol) -> bool:
    kind = (symbol.kind or "").lower()
    if kind in _METHOD_KINDS:
        return True
    if "#" not in symbol.stable_id:
        return False
    member = symbol.stable_id.split("#", 1)[1]
    return "(" in member and not is_constructor_symbol(symbol)


def method_members_for_type(
    symbols: list[PrunedSymbol],
    type_stable_id: str,
) -> list[PrunedSymbol]:
    if not type_stable_id.endswith("#"):
        return []
    return sorted(
        [
            symbol
            for symbol in symbols
            if symbol.stable_id.startswith(type_stable_id)
            and symbol.stable_id != type_stable_id
            and is_method_symbol(symbol)
        ],
        key=sort_key,
    )


def normalize_method_signature(symbol: PrunedSymbol) -> str:
    signature = (symbol.signature or "").strip()
    if not signature:
        name = symbol.display_name or symbol.stable_id.split("#", 1)[-1]
        return f"void {name}()"
    text = " ".join(signature.split())
    if text.endswith(";"):
        return text[:-1].strip()
    if text.endswith("}"):
        return text
    return text


def javadoc_first_line(documentation: str | None) -> str | None:
    if not documentation:
        return None
    for line in documentation.splitlines():
        stripped = line.strip().removeprefix("/**").removeprefix("*").removesuffix("*/").strip()
        if stripped and not stripped.startswith("@"):
            return stripped
    return None
