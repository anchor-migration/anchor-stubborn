# Anchor-DSL v1

Compact, language-neutral context format for LLMs and agents. Same privacy contract as Java stubs: **declarations and signatures only — no method bodies**.

## When to use

| Format | Best for |
|--------|----------|
| `java-stub` | Java/Spring codegen, familiar syntax |
| `anchor-dsl` | Lower token cost, cross-language agents, graph-first reasoning |

## LLM system prompt

Copy [ANCHOR-DSL-LLM.txt](ANCHOR-DSL-LLM.txt) into the agent system prompt when using `format=anchor-dsl`.

Every woven `anchor-dsl` block also embeds a 3-line `# Guide` header so the model sees the legend inline (~30 tokens).

## Grammar (v1)

Line-oriented text. Lines starting with `#` are comments (reserved for future use).

```
anchor-dsl/1.0
target <Type[.member]>
policy declarations-only

member m <Type.member> <signature>    # only when target is a method

types:
  <kind> <Name> [@Annotation ...]

edges:
  <edge-kind> <From> -> <To>
```

### Type kind codes

| Code | SCIP kind |
|------|-----------|
| `c` | class |
| `i` | interface |
| `e` | enum |
| `r` | record |

### Edge kind abbreviations

| Abbrev | SCIP edge |
|--------|-----------|
| `ref` | reference |
| `type` | type |
| `impl` | implementation |
| `def` | definition |

## Example

Target: `OrderService` (demo-spring)

```
anchor-dsl/1.0
target OrderService
policy declarations-only

types:
  c OrderService @Service
  i OrderRepository
  c OrderController @RestController @RequestMapping("/api/orders")
  c Order
  c InMemoryOrderRepository @Repository

edges:
  impl InMemoryOrderRepository -> OrderRepository
  ref OrderRepository -> Order
  ref OrderService -> OrderRepository
  ref OrderController -> OrderService
```

## CLI / API

```bash
anchor-stubborn context ./metadata/symbols.db \
  --target "…OrderService#" \
  --format anchor-dsl \
  --out ./context/order-service.anchor-dsl
```

```python
from anchor_stubborn.api import get_context

result = get_context("…OrderService#", format="anchor-dsl")
print(result.text)
```

MCP `get_context` accepts `format: "anchor-dsl"` the same way.

## Determinism

Same SCIP index + same prune budget → same Anchor-DSL output. Symbol order is stable (depth, then stable_id).

## Versioning

The first line must be `anchor-dsl/<major.minor>`. Breaking grammar changes bump the minor version and add a new weaver branch in code.

## Related

- [POSITIONING.md](POSITIONING.md) — privacy and pipeline
- [MCP.md](MCP.md) — agent integration
