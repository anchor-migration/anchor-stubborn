# Case: order-service-context

## Goal

Verify that pruning from `OrderService` includes repository, payment, and DTO types but excludes method bodies.

## Command

```bash
anchor-stubborn context metadata/symbols.db \
  --target "<OrderService stable_id>" \
  --out metadata/order-service.stub.java
```

The E2E script resolves the stable id automatically.

## Expected neighbors

Symbols in the pruned graph should include (names may vary by SCIP encoding):

- `OrderRepository` / `InMemoryOrderRepository`
- `PaymentGateway` / `PaymentService`
- `CreateOrderRequest`, `OrderResponse`
- `Order`, `Customer`, `OrderStatus`
- `OrderNotFoundException`

## Metrics to record (manual for now)

| Metric | How |
|--------|-----|
| Symbol count | `anchor-stubborn info` / graph size |
| Stub line count | `wc -l metadata/order-service.stub.java` |
| Token estimate | TBD — v0.3 `max_tokens` enforcement |

## Notes

- Default `--call-depth 2` should reach the repository interface and payment gateway.
- Hub types under `java.lang.*` are excluded by default (`ContextBudget.exclude_patterns`).
