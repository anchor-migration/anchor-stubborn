# MCP server

Anchor-Stubborn exposes three MCP tools over **stdio** for Cursor, Claude Desktop, and other MCP clients.

## Install

```bash
pip install -e ".[mcp]"
# or for development
pip install -e ".[dev]"
```

## Tools

| Tool | Purpose |
|------|---------|
| `get_context` | Prune symbol graph → LLM context (`format`: `java-stub` or `anchor-dsl`) |
| `list_symbols` | Browse/search indexed symbols to pick a target |
| `metrics` | Compression KPI: stub vs full Java `sources` tree |

### Database path

Pass `db_path` on each call, or set a default:

```bash
export ANCHOR_STUBBORN_DB=/path/to/metadata/symbols.db
```

## Run

```bash
anchor-stubborn mcp
# or
anchor-stubborn-mcp
```

The server uses stdio transport (default for local IDE integration).

## Cursor configuration

Add to `.cursor/mcp.json` (project) or Cursor MCP settings:

```json
{
  "mcpServers": {
    "anchor-stubborn": {
      "command": "anchor-stubborn-mcp",
      "env": {
        "ANCHOR_STUBBORN_DB": "${workspaceFolder}/examples/demo-spring/metadata/symbols.db"
      }
    }
  }
}
```

If the CLI is not on `PATH`, use the module entry:

```json
{
  "mcpServers": {
    "anchor-stubborn": {
      "command": "python",
      "args": ["-m", "anchor_stubborn.mcp_server.server"],
      "env": {
        "ANCHOR_STUBBORN_DB": "${workspaceFolder}/metadata/symbols.db"
      }
    }
  }
}
```

### Typical agent workflow

1. `anchor-stubborn index --scip index.scip --out metadata/symbols.db`
2. Configure MCP with `ANCHOR_STUBBORN_DB` pointing at that file
3. Agent calls `list_symbols` with `query: "OrderService"` to find `stable_id`
4. Agent calls `get_context` with the target stable_id before generating code
   - `format: "java-stub"` — default; Java-like declarations
   - `format: "anchor-dsl"` — compact graph; see [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt)
5. Optional: `metrics` with `sources: src/main/java` for compression reporting

## Parameters (get_context)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target` | required | SCIP stable_id |
| `db_path` | `ANCHOR_STUBBORN_DB` | Symbol graph SQLite file |
| `max_tokens` | 12000 | Output token budget (chars/4) |
| `max_symbols` | 200 | Graph prune cap |
| `call_depth` | 2 | Reference closure depth |
| `format` | `java-stub` | `java-stub` or `anchor-dsl` ([grammar](ANCHOR-DSL.md), [LLM prompt snippet](ANCHOR-DSL-LLM.txt)) |

## Related

- [ANCHOR-DSL.md](ANCHOR-DSL.md) — compact output format
- [INTEGRATION.md](INTEGRATION.md) — how migration programs consume Stubborn
- [migration-hub ADR-010](https://github.com/anchor-migration/migration-hub/blob/main/docs/ADR-010-anchor-stubborn-integration.md)
