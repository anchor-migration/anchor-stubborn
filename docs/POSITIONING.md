# Positioning

## One-liner

**Anchor-Stubborn** compiles symbol graphs into deterministic, privacy-safe LLM context.

## What it is

A **code context compiler**:

1. **Ingest** — SCIP symbol index → SQLite dependency graph
2. **Prune** — BFS from a target symbol with token/graph budgets
3. **Weave** — Emit declaration context (no method bodies)
4. **Reconcile** — Diff symbol sets for CI / migration guardrails

## Output formats (v0.7)

| Format | Description |
|--------|-------------|
| `java-stub` | Java-like declarations; best for codegen |
| `anchor-dsl` | Compact type/edge graph; best for token savings and cross-language agents |

Both use the same prune step. See [ANCHOR-DSL.md](ANCHOR-DSL.md) and [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt).

## What it is not

- Not a vector database or embedding RAG
- Not a multi-language parser (use scip-java, scip-clang, etc.)
- Not an AST rewrite engine (that's OpenRewrite / java-ast-ssot)
- Not migration-only
- Not a replacement for SCIP (SCIP is the machine index; Stubborn is the LLM-facing compiler output)

## Anchor family placement

```
anchor-migration org
├── db-metadata        → data layer SSOT
├── java-ast-ssot      → full Java AST SSOT (migration depth)
├── anchor-stubborn    → LLM context compiler (any live repo)  ← this
├── rewrite-recipes    → OpenRewrite migration recipes
└── migration-hub      → program docs (Stubborn = horizontal, not a pipeline layer)
```

**Same philosophy** as db-metadata: SQLite snapshots, stable IDs, reconcile reports.  
**Different consumer**: LLMs and agents, not schema explorers.

## vs java-ast-ssot

| | java-ast-ssot | anchor-stubborn |
|---|---------------|-----------------|
| Question answered | "What's in this project?" | "What does the AI need right now?" |
| Parser | JavaParser | SCIP (industry standard) |
| Languages | Java | Java first; SCIP-multi-language path |
| Output | Full AST SQLite | Pruned stub **text** (`java-stub` or `anchor-dsl`) |
| Token awareness | No | Core KPI |

They complement each other. Stubborn does not replace java-ast-ssot for migration crosswalk or Explorer.

## Privacy contract

**Included:** declarations, signatures, optional Javadoc first line  
**Excluded:** method bodies, field initializers, annotation attribute values with business data

## Status

**Pre-beta (v0.8.0a1, Java-first)** — feature-complete for Java/Spring E2E; one checklist item remains before the `0.8.0-beta1` tag ([BETA.md](BETA.md)). PyPI classifier stays Alpha until beta tag.
