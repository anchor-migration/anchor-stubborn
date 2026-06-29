"""Convert parsed SCIP protobuf into Anchor-Stubborn snapshot models."""

from __future__ import annotations

from anchor_stubborn.ingest.models import EdgeRecord, IndexSnapshot, SymbolRecord
from anchor_stubborn.ingest.scip_proto import scip_pb2
from anchor_stubborn.ingest.stream import ParsedIndex

_DEFINITION_ROLE = int(scip_pb2.SymbolRole.Definition)


def parsed_index_to_snapshot(
    parsed: ParsedIndex,
    *,
    scip_source: str,
    scip_hash: str | None,
    project_root: str | None = None,
) -> IndexSnapshot:
    symbols: dict[str, SymbolRecord] = {}
    edges: list[EdgeRecord] = []

    for document in parsed.documents:
        for symbol_info in document.symbols:
            _upsert_symbol(symbols, symbol_info)
            edges.extend(_edges_from_relationships(symbol_info))

        edges.extend(_edges_from_occurrences(document))

    for symbol_info in parsed.external_symbols:
        _upsert_symbol(symbols, symbol_info)
        edges.extend(_edges_from_relationships(symbol_info))

    language = _detect_language(parsed)
    resolved_root = project_root or (parsed.metadata.project_root if parsed.metadata else None)

    return IndexSnapshot(
        scip_source=scip_source,
        symbols=sorted(symbols.values(), key=lambda s: s.stable_id),
        edges=_dedupe_edges(edges),
        project_root=resolved_root or None,
        scip_hash=scip_hash,
        language=language,
    )


def _detect_language(parsed: ParsedIndex) -> str | None:
    for document in parsed.documents:
        if document.language:
            return document.language
    return None


def _kind_name(kind: int) -> str | None:
    if kind == scip_pb2.SymbolInformation.UnspecifiedKind:
        return None
    name = scip_pb2.SymbolInformation.Kind.Name(kind)
    if name == "UnspecifiedKind":
        return None
    return name.lower()


def _signature_text(symbol_info: scip_pb2.SymbolInformation) -> str | None:
    if symbol_info.HasField("signature_documentation"):
        text = symbol_info.signature_documentation.text.strip()
        if text:
            return text
    for line in symbol_info.documentation:
        stripped = line.strip()
        if stripped.startswith("```"):
            continue
        if stripped:
            return stripped
    return None


def _documentation_text(symbol_info: scip_pb2.SymbolInformation) -> str | None:
    prose = [
        line.strip()
        for line in symbol_info.documentation
        if line.strip() and not line.strip().startswith("```")
    ]
    if not prose:
        return None
    return "\n".join(prose)


def _upsert_symbol(store: dict[str, SymbolRecord], symbol_info: scip_pb2.SymbolInformation) -> None:
    if not symbol_info.symbol:
        return
    store[symbol_info.symbol] = SymbolRecord(
        stable_id=symbol_info.symbol,
        display_name=symbol_info.display_name or None,
        kind=_kind_name(symbol_info.kind),
        signature=_signature_text(symbol_info),
        documentation=_documentation_text(symbol_info),
    )


def _edges_from_relationships(symbol_info: scip_pb2.SymbolInformation) -> list[EdgeRecord]:
    if not symbol_info.symbol:
        return []

    edges: list[EdgeRecord] = []
    for relationship in symbol_info.relationships:
        if not relationship.symbol:
            continue
        if relationship.is_type_definition:
            edges.append(
                EdgeRecord(symbol_info.symbol, relationship.symbol, "type")
            )
        if relationship.is_implementation:
            edges.append(
                EdgeRecord(symbol_info.symbol, relationship.symbol, "implementation")
            )
        if relationship.is_reference:
            edges.append(
                EdgeRecord(symbol_info.symbol, relationship.symbol, "reference")
            )
        if relationship.is_definition:
            edges.append(
                EdgeRecord(symbol_info.symbol, relationship.symbol, "definition")
            )
    return edges


def _occurrence_sort_key(occurrence: scip_pb2.Occurrence) -> tuple[int, int]:
    if occurrence.HasField("single_line_range"):
        row = occurrence.single_line_range
        return row.line, row.start_character
    if occurrence.HasField("multi_line_range"):
        row = occurrence.multi_line_range
        return row.start_line, row.start_character
    if len(occurrence.range) >= 2:
        return occurrence.range[0], occurrence.range[1]
    return 0, 0


def _edges_from_occurrences(document: scip_pb2.Document) -> list[EdgeRecord]:
    edges: list[EdgeRecord] = []
    enclosing_stack: list[str] = []

    for occurrence in sorted(document.occurrences, key=_occurrence_sort_key):
        if not occurrence.symbol:
            continue

        is_definition = (occurrence.symbol_roles & _DEFINITION_ROLE) != 0
        if is_definition:
            enclosing_stack.append(occurrence.symbol)
            continue

        if not enclosing_stack:
            continue
        edges.append(
            EdgeRecord(enclosing_stack[-1], occurrence.symbol, "reference")
        )

    return edges


def _dedupe_edges(edges: list[EdgeRecord]) -> list[EdgeRecord]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[EdgeRecord] = []
    for edge in edges:
        key = (edge.from_stable_id, edge.to_stable_id, edge.edge_kind)
        if key in seen:
            continue
        seen.add(key)
        unique.append(edge)
    return unique
