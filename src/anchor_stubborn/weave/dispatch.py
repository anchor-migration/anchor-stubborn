"""Route pruned graphs to the requested output format."""

from __future__ import annotations

from anchor_stubborn.graph.prune import PrunedGraph
from anchor_stubborn.weave.anchor_dsl import weave_anchor_dsl
from anchor_stubborn.weave.java_stub import weave_java_stub
from anchor_stubborn.weave.options import DEFAULT_WEAVE_OPTIONS, WeaveOptions
from anchor_stubborn.weave.types import WeaveResult

SUPPORTED_FORMATS = frozenset({"java-stub", "anchor-dsl"})


def weave_context(
    graph: PrunedGraph,
    *,
    format: str = "java-stub",
    max_tokens: int | None = None,
    options: WeaveOptions | None = None,
) -> WeaveResult:
    weave_options = options or DEFAULT_WEAVE_OPTIONS
    if format == "java-stub":
        return weave_java_stub(graph, max_tokens=max_tokens, options=weave_options)
    if format == "anchor-dsl":
        return weave_anchor_dsl(graph, max_tokens=max_tokens, options=weave_options)
    raise ValueError(f"Unsupported format: {format!r} (choose: {', '.join(sorted(SUPPORTED_FORMATS))})")
