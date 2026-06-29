# Migration bridge example

How [anchor-migration](https://github.com/anchor-migration/migration-hub) can consume Anchor-Stubborn without tight coupling.

## Scenario

Migrating `AccountControllerBean` (EJB session) → Spring `@Service`. The LLM needs surrounding types but not full method bodies.

## Steps

```bash
# In the legacy Java repo (with scip-java configured)
scip-java index --targetroot /path/to/bank
# produces index.scip

# Index into Stubborn SQLite
anchor-stubborn index --scip index.scip --out metadata/context.db

# Emit privacy-safe context
anchor-stubborn context metadata/context.db \
  --target "semanticdb maven com/sun/ebank/ejb/account/AccountControllerBean#" \
  --out account-controller.stub.java
```

Paste `account-controller.stub.java` into your agent prompt instead of entire source trees.

## What stays in migration repos

| Task | Tool |
|------|------|
| Full code SSOT + EJB profiles | java-ast-ssot |
| Schema SSOT | db-metadata |
| Crosswalk + Explorer | java-ast-ssot + anchor-explorer |
| **LLM context only** | **anchor-stubborn** |
| Apply rewrites | rewrite-recipes |

## CI hook (planned v0.3)

```yaml
- run: anchor-stubborn diff metadata/before.db metadata/after.db --in-scope scope.txt
```

Fails the PR if in-scope symbols disappear after migration.

See [docs/INTEGRATION.md](../../docs/INTEGRATION.md).
