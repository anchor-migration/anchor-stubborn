# Case: order-service-context

## Goal

Verify that pruning from `OrderService` includes repository, payment, and DTO types but excludes method bodies.

## Command

```bash
anchor-stubborn context metadata/symbols.db \
  --target "<OrderService stable_id>" \
  --out metadata/order-service.stub.java

anchor-stubborn metrics metadata/symbols.db \
  --target "<OrderService stable_id>" \
  --sources src/main/java
```

The Docker E2E script resolves the stable id automatically.

## Expected neighbors

Symbols in the pruned graph should include (names may vary by SCIP encoding):

- `OrderRepository` / `InMemoryOrderRepository`
- `PaymentGateway` / `PaymentService`
- `CreateOrderRequest`, `OrderResponse`
- `Order`, `Customer`, `OrderStatus`
- `OrderNotFoundException`

## Baseline KPI (demo-spring, Docker E2E)

Measured after `docker compose run --rm e2e` (Java 21, Spring Boot 3.3, scip-java 0.12.3):

| Metric | Value |
|--------|-------|
| `source_files` | 14 |
| `source_bytes` | 10,020 |
| `source_tokens_est` | 2,423 |
| `stub_symbols` | 11 |
| `stub_tokens_est` | 450 |
| `compression_ratio` | **81.43%** |
| `token_savings` | **81.4%** |

Passes the ≥75% compression target with expanded type-neighbor coverage (PaymentGateway, DTOs).

## Notes

- Pruning seeds **type members** (fields/methods) from the target class, then resolves **signature type refs** (e.g. `PaymentGateway` on `paymentGateway` field).
- Graph expansion after depth 0 keeps **type symbols only** to avoid DTO field noise.
- Default `--call-depth 2` reaches repository, payment, and DTO types.
- Default `--max-tokens 12000` enforces output budget (chars/4 heuristic).
- Hub types under `java.lang.*` are excluded by default (`ContextBudget.exclude_patterns`).
- Constructors are folded into type declarations (not emitted as separate lines).
