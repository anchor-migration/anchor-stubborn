# Beta readiness (Java-first)

**Current release: pre-beta (`0.8.0a1`)** — Java/Spring path validated; not yet the formal `0.8.0-beta1` tag.

Anchor-Stubborn targets **v0.8-beta**: a stable Java/Spring context compiler for LLM agents. Multi-language and PyPI distribution are not beta blockers.

## Beta definition

Ship **v0.8.0-beta** when all items below are checked.

### Core pipeline

- [x] SCIP binary + NDJSON + JSON fixture ingest
- [x] SQLite symbol graph + `index` / `info` / `context` / `metrics` / `diff`
- [x] Type-neighbor pruning with token budget
- [x] `java-stub` and `anchor-dsl` weavers
- [x] MCP server (`get_context`, `list_symbols`, `metrics`)

### E2E validation

- [x] demo-spring Docker E2E (PR CI)
- [x] spring-petclinic scale-up E2E (weekly / manual)
- [x] **OrderController** case + verify guard (web → service)
- [x] Neighbor integration tests run in CI **without skip** (symbols.db artifact)

### Agent / docs

- [x] [ANCHOR-DSL.md](ANCHOR-DSL.md) + [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt)
- [x] [docs/README.md](README.md) index
- [x] migration-hub [ADR-010](https://github.com/anchor-migration/migration-hub/blob/main/docs/ADR-010-anchor-stubborn-integration.md) synced to v0.7
- [x] Integration + MCP docs current

### Quality bar

- [x] `anchor-stubborn info` shows `language: java` for scip-java indexes (path fallback when SCIP field empty)
- [x] pytest green on 3.11 / 3.12 / 3.13 (with CI symbols.db artifact)
- [x] PR symbol-diff workflow
- [ ] `pyproject.toml` classifier → `Development Status :: 4 - Beta` (at tag time)

## Out of scope for beta

| Item | Target |
|------|--------|
| PyPI publish | Post-beta or optional `0.8.0b1` |
| scip-clang / TypeScript E2E | v0.9+ |
| Full neighbor method signatures in stub | v0.8+ stretch |
| Javadoc prose in woven output | v0.9+ |
| Petclinic on every PR | Stays weekly (cost) |

## Known limitations (beta)

1. **Java-first** — validated with scip-java; other SCIP indexers are best-effort.
2. **Types in stub text** — neighbor fields/methods expand the graph but are not listed individually in output (except method targets).
3. **Token estimate** — chars/4 heuristic, not a real tokenizer.
4. **Anchor-DSL** — newer format; prefer `java-stub` for Java codegen unless token budget is tight.
5. **SCIP is the index** — Stubborn does not replace SCIP; it compiles pruned graphs to LLM text.

## KPI baselines

| Example | Target | Symbols | Token savings |
|---------|--------|---------|---------------|
| demo-spring `OrderService` | service layer | ~12 | ~81% |
| demo-spring `OrderController` | web layer | ~9 | ~84% (≥75% gate) |
| spring-petclinic `VetController` | scale-up | ~13 | ~90% |

## Checklist to tag `v0.8.0-beta`

1. Complete unchecked items above (`Development Status :: 4 - Beta` at tag)
2. Bump version `0.8.0-beta1` in `pyproject.toml` / `__init__.py`
3. Update [POSITIONING.md](POSITIONING.md) status line
4. Short release note in README roadmap

## Related

- [POSITIONING.md](POSITIONING.md)
- [INTEGRATION.md](INTEGRATION.md)
- [examples/demo-spring/cases/](../examples/demo-spring/cases/)
