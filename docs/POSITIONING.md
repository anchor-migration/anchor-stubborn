# Positioning

## One-liner

**Anchor-Stubborn** compiles symbol graphs into deterministic, privacy-safe LLM context.

## What it is

A **code context compiler**:

1. **Ingest** — SCIP symbol index → SQLite dependency graph
2. **Prune** — BFS from a target symbol with token/graph budgets
3. **Weave** — Emit declaration stubs (no method bodies)
4. **Reconcile** — Diff symbol sets for CI / migration guardrails

## What it is not

- Not a vector database or embedding RAG
- Not a multi-language parser (use scip-java, scip-clang, etc.)
- Not an AST rewrite engine (that's OpenRewrite / java-ast-ssot)
- Not migration-only

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
| Output | Full AST SQLite | Pruned stub **text** |
| Token awareness | No | Core KPI |

They complement each other. Stubborn does not replace java-ast-ssot for migration crosswalk or Explorer.

## Privacy contract

**Included:** declarations, signatures, optional Javadoc first line  
**Excluded:** method bodies, field initializers, annotation attribute values with business data

## Status

Alpha (v0.2). Binary SCIP ingest supports scip-java `index.scip` output. MCP server planned for v0.3.
