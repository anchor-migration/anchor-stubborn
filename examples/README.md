# Examples

Runnable and planned end-to-end scenarios for Anchor-Stubborn.

| Example | Status | Description |
|---------|--------|-------------|
| [demo-spring](demo-spring/) | **Active** | In-repo Spring Boot 3 demo — primary E2E path |
| [fixtures](fixtures/) | Active | Minimal JSON / binary SCIP for unit tests |
| [spring-petclinic](spring-petclinic/) | **Active** | Scale-up E2E vs official PetClinic (~375 symbols, ~90% savings) |
| [migration-bridge](migration-bridge/) | Active | How anchor-migration consumes Stubborn (Duke's Bank) |

## Recommended first run

**Docker (no local Java toolchain):**

```bash
# from repo root
docker compose build
docker compose run --rm e2e          # demo-spring
docker compose run --rm petclinic-e2e  # spring-petclinic scale-up
```

**Host:**

```bash
cd examples/demo-spring
./scripts/run-e2e.ps1   # Windows PowerShell
# or follow README.md for manual steps
```
