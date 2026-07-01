# Documentation index

| Doc | Audience | Contents |
|-----|----------|----------|
| [POSITIONING.md](POSITIONING.md) | Architects | What Stubborn is / is not; Anchor family placement |
| [INTEGRATION.md](INTEGRATION.md) | Migration teams | How migration-hub consumes Stubborn |
| [SCIP-INGEST.md](SCIP-INGEST.md) | Index authors | Supported SCIP formats and ingest behavior |
| [MCP.md](MCP.md) | Agent / Cursor users | MCP tools, config, workflows |
| [ANCHOR-DSL.md](ANCHOR-DSL.md) | LLM context authors | Anchor-DSL v1 grammar and CLI usage |
| [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt) | Prompt engineers | Short system-prompt snippet for `format=anchor-dsl` |

## Output formats

| Format | CLI / MCP `format` | When to use |
|--------|-------------------|-------------|
| Java stub | `java-stub` (default) | Java / Spring code generation |
| Anchor-DSL | `anchor-dsl` | Lower tokens, graph-first reasoning; includes inline `# Guide` |

Both formats share the same prune step and privacy contract (declarations only, no method bodies).

## Examples

| Path | Description |
|------|-------------|
| [examples/demo-spring](../examples/demo-spring/) | Primary in-repo E2E (~14 files, ~81% savings) |
| [examples/spring-petclinic](../examples/spring-petclinic/) | Scale-up E2E vs upstream PetClinic (~375 symbols, ~90% savings) |
| [examples/migration-bridge](../examples/migration-bridge/) | Legacy migration consumer pattern |
| [docker/README.md](../docker/README.md) | Reproducible Docker toolchain |

## External

- [migration-hub ADR-010](https://github.com/anchor-migration/migration-hub/blob/main/docs/ADR-010-anchor-stubborn-integration.md) — program integration contract
