# Spring PetClinic — planned scale-up E2E

**Status:** placeholder — not yet automated in this repo.

## Why PetClinic later

| | demo-spring | spring-petclinic |
|---|-------------|------------------|
| Size | ~14 Java files | ~80+ files |
| Index time | seconds | minutes |
| Purpose | Fast regression, docs, CI-friendly | Realistic multi-package Spring app |
| Maintenance | In-repo | External clone |

Use **demo-spring** for day-to-day development. Use **PetClinic** to validate scale, richer graphs, and cross-package pruning.

## Planned workflow

Prefer the Docker toolchain from repo root (`docker compose`) when PetClinic automation lands.

```bash
# 1. Clone upstream (pin a tag for reproducibility)
git clone --depth 1 --branch main https://github.com/spring-projects/spring-petclinic.git upstream
cd upstream

# 2. Index
scip-java index

# 3. Anchor-Stubborn (from anchor-stubborn repo root)
anchor-stubborn index --scip upstream/index.scip --out examples/spring-petclinic/metadata/symbols.db
anchor-stubborn context examples/spring-petclinic/metadata/symbols.db \
  --target "<OwnerController or VetController stable_id>" \
  --out examples/spring-petclinic/metadata/vet-context.stub.java
```

## Planned cases (./cases/)

| Case | Target | Notes |
|------|--------|-------|
| vet-controller | `VetController` | Web → service → repository chain |
| owner-visit-flow | `VisitController` | Multi-entity graph |
| token-budget-stress | TBD | Measure compression vs full sources |

## TODO

- [ ] Pin PetClinic commit SHA in this README
- [ ] Add `scripts/run-e2e.ps1` (optional clone + index)
- [ ] Add `cases/` entries with expected symbol neighbors
- [ ] Document token compression baseline vs `demo-spring`
- [ ] Optional CI job (manual / scheduled) — not on every PR

## Upstream

- https://github.com/spring-projects/spring-petclinic
- Spring Boot 3.x, Java 17+
