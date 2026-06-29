# orders-demo — Anchor-Stubborn E2E

A **small, modern** Spring Boot 3 application used as the primary end-to-end example for Anchor-Stubborn.

| | |
|---|---|
| Java | 21 |
| Framework | Spring Boot 3.3 |
| Build | Maven |
| Domain | Orders API (controller → service → repository) |
| Source files | ~14 Java classes |

Designed to be extended with additional **cases** under [`cases/`](cases/) without growing into a monolith.

## Layout

```text
com.example.orders
├── OrdersApplication
├── web/          OrderController, OrderExceptionHandler
├── service/      OrderService, PaymentService, PaymentGateway
├── repository/   OrderRepository, InMemoryOrderRepository
├── domain/       Order, Customer, OrderStatus
├── dto/          CreateOrderRequest, OrderResponse
└── exception/    OrderNotFoundException
```

## Prerequisites

Choose **one** path:

### A. Docker (recommended — no local JDK/Maven/scip-java)

From the **anchor-stubborn repo root**:

```bash
docker compose build
docker compose run --rm e2e
```

See [docker/README.md](../../docker/README.md).

### B. Host toolchain

- **JDK 21+**
- **Maven 3.9+**
- **[scip-java](https://github.com/sourcegraph/scip-java)** on `PATH`
- **Anchor-Stubborn** installed: `pip install -e ".[dev]"` from repo root

## Quick E2E (PowerShell, host)

```powershell
cd examples/demo-spring
./scripts/run-e2e.ps1
```

Outputs:

- `index.scip` — SCIP index from scip-java
- `metadata/symbols.db` — Anchor-Stubborn SQLite graph
- `metadata/order-service.stub.java` — pruned LLM context for `OrderService`

## Manual steps

```bash
# 1. Compile (scip-java index also compiles via Maven)
mvn -q -DskipTests package

# 2. Generate SCIP index
scip-java index
# → index.scip

# 3. Ingest into Anchor-Stubborn
anchor-stubborn index --scip index.scip --out metadata/symbols.db
anchor-stubborn info metadata/symbols.db

# 4. Resolve target symbol (display name → stable_id)
#    Then emit context — exact stable_id depends on scip-java output, e.g.:
anchor-stubborn context metadata/symbols.db \
  --target "<OrderService stable_id from index>" \
  --out metadata/order-service.stub.java
```

Use the E2E script to resolve `OrderService` automatically from the SQLite index.

## Run the app (optional)

```bash
mvn spring-boot:run
curl -X POST http://localhost:8080/api/orders \
  -H 'Content-Type: application/json' \
  -d '{"customerEmail":"ada@example.com","customerName":"Ada","total":42.50}'
```

## Adding cases

See [`cases/README.md`](cases/README.md) for the case catalog pattern. New scenarios (e.g. pay flow, exception paths) should add focused docs and optional expected stub snippets — not more framework boilerplate.

## Related examples

| Example | Role |
|---------|------|
| [spring-petclinic](../spring-petclinic/) | Planned scale-up against the official PetClinic repo |
| [migration-bridge](../migration-bridge/) | Legacy migration integration (Duke's Bank) |
| [fixtures](../fixtures/) | Minimal SCIP files for unit tests |
