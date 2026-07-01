"""Route pruned graphs to the requested output format."""

from __future__ import annotations

from anchor_stubborn.graph.prune import PrunedGraph
from anchor_stubborn.weave.anchor_dsl import weave_anchor_dsl
from anchor_stubborn.weave.java_stub import weave_java_stub
from anchor_stubborn.weave.types import WeaveResult

SUPPORTED_FORMATS = frozenset({"java-stub", "anchor-dsl"})


def weave_context(
    graph: PrunedGraph,
    *,
    format: str = "java-stub",
    max_tokens: int | None = None,
) -> WeaveResult:
    if format == "java-stub":
        return weave_java_stub(graph, max_tokens=max_tokens)
    if format == "anchor-dsl":
        return weave_anchor_dsl(graph, max_tokens=max_tokens)
    raise ValueError(f"Unsupported format: {format!r} (choose: {', '.join(sorted(SUPPORTED_FORMATS))})")
