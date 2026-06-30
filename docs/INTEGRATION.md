# Integration with anchor-migration

Anchor-Stubborn is a **horizontal capability**. The migration program is one consumer, not the owner.

## When migration uses Stubborn

Before asking an LLM to propose rewrite mappings or recipe changes:

```bash
# 1. Generate SCIP (scip-java in the target repo)
# 2. Index
anchor-stubborn index --scip index.scip --out metadata/code-context.db

# 3. Context for a migration target class
anchor-stubborn context metadata/code-context.db \
  --target "semanticdb maven com/sun/ebank/ejb/account/AccountControllerBean#" \
  --out /tmp/account-controller.stub.java
```

Feed `/tmp/account-controller.stub.java` to the LLM instead of raw sources.

Or use the MCP server (`anchor-stubborn mcp`) so agents call `get_context` directly — see [MCP.md](MCP.md).

## When migration does NOT use Stubborn

- Full AST export for Explorer → **java-ast-ssot**
- Schema ↔ code crosswalk → **java-ast-ssot crosswalk** + **db-metadata**
- Applying rewrites → **rewrite-recipes** + OpenRewrite
- Parity testing → **parity-verify** (planned)

## Pipeline diagram (consumer view)

```
                    ┌─────────────────────┐
                    │   anchor-stubborn   │
                    └──────────┬──────────┘
                               │ stub context text
     ┌─────────────────────────┼─────────────────────────┐
     ▼                         ▼                         ▼
 LLM mapping draft      rewrite-recipes design      PR diff CI
```

Stubborn is **not** drawn inside migration-hub Layers 1–4. It sits above them as shared infrastructure.

## Future: migration-hub ADR

Program integration is documented in [migration-hub ADR-010](https://github.com/anchor-migration/migration-hub/blob/main/docs/ADR-010-anchor-stubborn-integration.md). This file remains repo-local workflow detail.

## Weak coupling rules

1. **No compile-time dependency** from Stubborn → rewrite-recipes or java-ast-ssot
2. **Shared conventions only**: stable IDs, SQLite snapshot pattern, reconcile vocabulary
3. **Optional** in any migration runbook — teams can use java-ast-ssot alone until Stubborn matures
