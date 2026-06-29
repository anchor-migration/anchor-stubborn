"""Load SCIP index files into in-memory snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from anchor_stubborn.ingest.models import EdgeRecord, IndexSnapshot, SymbolRecord

SCIP_MAGIC = b"\x00scip\x00"


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_scip_index(
    scip_path: str | Path,
    *,
    project_root: str | None = None,
) -> IndexSnapshot:
    """Load a SCIP index file.

    Supports:
    - JSON fixtures (``.json``) for tests and early prototyping
    - Binary SCIP protobuf (``.scip``) — requires generated bindings (v0.2)
    """
    path = Path(scip_path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        return _load_json_fixture(path, project_root=project_root)

    if path.suffix.lower() == ".scip" or path.name.endswith(".scip"):
        return _load_scip_protobuf(path, project_root=project_root)

    raise ValueError(
        f"Unsupported SCIP input: {path}. Use .scip (protobuf) or .json (fixture)."
    )


def _load_json_fixture(path: Path, *, project_root: str | None) -> IndexSnapshot:
    """Load a minimal JSON fixture used by tests and examples."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    symbols = [
        SymbolRecord(
            stable_id=item["stable_id"],
            display_name=item.get("display_name"),
            kind=item.get("kind"),
            signature=item.get("signature"),
            documentation=item.get("documentation"),
        )
        for item in payload.get("symbols", [])
    ]
    edges = [
        EdgeRecord(
            from_stable_id=item["from"],
            to_stable_id=item["to"],
            edge_kind=item.get("edge_kind", "reference"),
        )
        for item in payload.get("edges", [])
    ]
    return IndexSnapshot(
        scip_source=str(path),
        symbols=symbols,
        edges=edges,
        project_root=project_root or payload.get("project_root"),
        scip_hash=_file_hash(path),
        language=payload.get("language"),
    )


def _load_scip_protobuf(path: Path, *, project_root: str | None) -> IndexSnapshot:
    """Parse binary SCIP protobuf. Full parser lands in v0.2."""
    data = path.read_bytes()
    if not data.startswith(SCIP_MAGIC):
        raise ValueError(f"Not a SCIP index file: {path}")

    # Placeholder until scip.proto bindings are vendored
    raise NotImplementedError(
        "Binary SCIP ingest is not implemented yet. "
        "Generate index.scip with scip-java, then convert to JSON fixture, "
        "or wait for v0.2 protobuf support."
    )
