# SKILL-24: Plan Before You Query

## When
Any request that is more complex than a simple lookup (involves joins, aggregations, or conditions you are uncertain about).

## Rule
Before writing SQL, write a short plan in plain language. This prevents wasted tool calls and wrong queries.

## Planning Template (internal, not shown to user)

```
Request: "Show me which product category had the highest revenue last quarter"

Plan:
1. Schema check — confirm `orders` has a total column and ordered_at date
2. Schema check — confirm `products` has a category column
3. Identify join key — orders.product_id → products.id
4. Filter — ordered_at in last quarter
5. Aggregate — SUM(total) GROUP BY category
6. Sort — ORDER BY revenue DESC
7. Return — top row or top 5
```

Only then write the SQL.

## How Many Tool Calls to Plan For

| Request complexity              | Expected tool calls |
|---------------------------------|---------------------|
| Simple lookup by ID             | 1                   |
| Filtered list with known schema | 1                   |
| Aggregation on known table      | 1–2                 |
| Join across unfamiliar tables   | 2–3 (schema + query)|
| Multi-step analytical question  | 3 max               |

## If You Exceed 3 Tool Calls
Stop. Tell the user: "This question requires multiple steps. Let me break it into parts — first, [simpler sub-question]?"

## Why Planning Matters for a Small Model
Without a plan, small models generate SQL that almost works, run it, get an error, patch it, and drift far from the original intent. A 3-line plan prevents 5 wasted round-trips.
