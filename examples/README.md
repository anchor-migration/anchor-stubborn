# Examples

Runnable and planned end-to-end scenarios for Anchor-Stubborn.

| Example | Status | Description |
|---------|--------|-------------|
| [demo-spring](demo-spring/) | **Active** | In-repo Spring Boot 3 demo — primary E2E path |
| [fixtures](fixtures/) | Active | Minimal JSON / binary SCIP for unit tests |
| [spring-petclinic](spring-petclinic/) | Planned | Scale-up E2E against the official PetClinic repo |
| [migration-bridge](migration-bridge/) | Active | How anchor-migration consumes Stubborn (Duke's Bank) |

## Recommended first run

**Docker (no local Java toolchain):**

```bash
# from repo root
docker compose build
docker compose run --rm e2e
```

**Host:**

```bash
cd examples/demo-spring
./scripts/run-e2e.ps1   # Windows PowerShell
# or follow README.md for manual steps
```
