# Beta readiness (Java-first)

**Current: pre-beta `0.9.0a1`** — Java/Spring E2E complete; target-type method signatures shipped in v0.9.

**Next tag: `0.9.0b1`** — formal beta (classifier `Development Status :: 4 - Beta`). Pre-beta lines use `0.9.0aN`; stay on pre-beta until then.

Multi-language and PyPI are not beta blockers.

## Versioning

| Stage | Version example | PyPI classifier |
|-------|-----------------|-----------------|
| Pre-beta (now) | `0.9.0a1` | Alpha |
| Formal beta | `0.9.0b1` | Beta |
| Stable | `1.0.0` | Stable |

## Beta definition

Ship **`0.9.0b1`** when the unchecked item below is done (everything else is complete).

### Core pipeline

- [x] SCIP binary + NDJSON + JSON fixture ingest
- [x] SQLite symbol graph + `index` / `info` / `context` / `metrics` / `diff`
- [x] Type-neighbor pruning with token budget
- [x] `java-stub` and `anchor-dsl` weavers
- [x] MCP server (`get_context`, `list_symbols`, `metrics`)
- [x] Target-type method signatures (v0.9)

### E2E validation

- [x] demo-spring Docker E2E (PR CI) — OrderService, OrderController, payOrder
- [x] spring-petclinic scale-up E2E (weekly / manual)
- [x] Neighbor integration tests in CI (symbols.db artifact)

### Agent / docs

- [x] [ANCHOR-DSL.md](ANCHOR-DSL.md), [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt), [ANCHOR-DSL-GUIDE.md](ANCHOR-DSL-GUIDE.md)
- [x] [docs/README.md](README.md) index
- [x] migration-hub [ADR-010](https://github.com/anchor-migration/migration-hub/blob/main/docs/ADR-010-anchor-stubborn-integration.md) synced

### Quality bar

- [x] `language: java` from SCIP (with path fallback)
- [x] pytest on 3.11 / 3.12 / 3.13
- [x] PR symbol-diff workflow
- [ ] `pyproject.toml` classifier → Beta **at `0.9.0b1` tag only**

## Out of scope for beta

| Item | Target |
|------|--------|
| PyPI publish | Post-beta |
| scip-clang / TypeScript E2E | v1.0+ |
| Method signatures on non-target types | v1.0+ |
| Rich Javadoc in output | v1.0+ (hook exists; sparse in SCIP) |
| Petclinic on every PR | Stays weekly (cost) |

## Known limitations (pre-beta)

1. **Java-first** — validated with scip-java; other indexers best-effort.
2. **Method signatures** — **target type only** (v0.9); neighbors stay declaration stubs.
3. **Token estimate** — chars/4 heuristic.
4. **Anchor-DSL** — prefer `java-stub` for Java codegen ([guide](ANCHOR-DSL-GUIDE.md)).
5. **SCIP is the index** — Stubborn compiles pruned graphs to LLM text.

## KPI baselines

| Example | Target | Symbols | Token savings |
|---------|--------|---------|---------------|
| demo-spring `OrderService` | service layer | ~12 | ~81% |
| demo-spring `OrderController` | web layer | ~9 | ~84% |
| demo-spring `OrderService#payOrder` | method / payment | ~10 | ~80% |
| spring-petclinic `VetController` | scale-up | ~13 | ~90% |

## Checklist to tag `0.9.0b1`

1. Confirm checklist above (classifier only item left)
2. Set `version = "0.9.0b1"` in `pyproject.toml` / `__init__.py`
3. Set `Development Status :: 4 - Beta` in `pyproject.toml`
4. Update README / POSITIONING status to **Beta**

## Related

- [POSITIONING.md](POSITIONING.md)
- [INTEGRATION.md](INTEGRATION.md)
- [examples/demo-spring/cases/](../examples/demo-spring/cases/)
