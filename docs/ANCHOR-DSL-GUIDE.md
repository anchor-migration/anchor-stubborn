# When to use `java-stub` vs `anchor-dsl`

Quick decision guide for agents and prompt authors.

## Decision tree

```
Generating or editing Java/Spring source code?
├─ YES → java-stub (default)
└─ NO  → Is token budget tight or task graph-first (deps, design, migration mapping)?
         ├─ YES → anchor-dsl (+ ANCHOR-DSL-LLM.txt in system prompt)
         └─ NO  → java-stub
```

## Format comparison

| | `java-stub` | `anchor-dsl` |
|---|-------------|--------------|
| **Looks like** | Java declarations | Compact type/edge graph |
| **LLM familiarity** | High (Java syntax) | Medium (3-line `# Guide` in each block) |
| **Token cost** | Higher | Lower on large graphs (~10–30% on demo-spring; fixed Guide overhead on tiny graphs) |
| **Best tasks** | Codegen, refactor in place | Architecture, dependency audit, migration scoping |
| **Method target** | Emits target method line | `member m Type.method sig` |
| **Type target (v0.9+)** | Target class includes method signatures | `members:` block on target type |

## Granularity switches (token vs detail)

Both formats share `--member-signatures` and `--javadoc` (CLI, API, MCP):

| Flag | Values | Default | Effect |
|------|--------|---------|--------|
| `--member-signatures` | `off` \| `target` \| `neighbors` \| `all` | `target` | Which types get method lists |
| `--javadoc` | `off` \| `summary` \| `full` | `summary` (java-stub), `off` (anchor-dsl) | Doc comments in output |

| Task | Suggested flags |
|------|-----------------|
| Codegen on target class | `target` + `summary` |
| Min tokens | `off` + `off` + `anchor-dsl` |
| Understand neighbor APIs | `neighbors` or `all` |
| Business semantics | `summary` or `full` on key types |

## Examples (demo-spring, same index)

| Target | Format | ~tokens | Use when |
|--------|--------|---------|----------|
| `OrderService#` | java-stub | ~463 | Implement service methods |
| `OrderService#` | anchor-dsl | ~350 | See service deps cheaply |
| `OrderController#` | java-stub | ~375 | Add REST endpoints |
| `OrderService#payOrder` | either | ~400 | Narrow payment-flow change |

Run locally:

```bash
anchor-stubborn context metadata/symbols.db --target "<stable_id>" --format java-stub
anchor-stubborn context metadata/symbols.db --target "<stable_id>" --format anchor-dsl
anchor-stubborn metrics metadata/symbols.db --target "<stable_id>" --sources src/main/java
```

## MCP

```json
{ "target": "…OrderService#", "format": "java-stub" }
{ "target": "…OrderService#", "format": "anchor-dsl" }
```

## Rules of thumb

1. **Default to `java-stub`** for Cursor/Copilot Java tasks.
2. **Use `anchor-dsl`** when context is read-only (analysis, mapping, review) or you hit `max_tokens`.
3. **Method targets** (`Type#method`) work in both formats; prefer `java-stub` if the model must edit that method.
4. Paste [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt) once per session when using `anchor-dsl`.

## Related

- [ANCHOR-DSL.md](ANCHOR-DSL.md) — grammar
- [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt) — system prompt snippet
- [BETA.md](BETA.md) — release status
