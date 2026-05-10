# SKILL-20: Avoid the N+1 Query Pattern

## What It Is
N+1 means: running 1 query to get a list, then running 1 more query per row in that list.
For 100 rows this is 101 queries. For 1,000 rows it is 1,001 queries.
This is a critical performance mistake.

## Example of N+1 (Wrong)
```
1. SELECT id FROM orders LIMIT 50;         -- returns 50 order IDs
2. SELECT name FROM customers WHERE id = 1 -- for order 1
3. SELECT name FROM customers WHERE id = 2 -- for order 2
... 50 more queries
```

## Correct: One JOIN Instead
```sql
SELECT
    o.order_id,
    c.name   AS customer_name,
    o.total,
    o.status
FROM orders AS o
INNER JOIN customers AS c ON c.id = o.customer_id
LIMIT 50;
```

## Correct: IN clause for a known list
If you already have a list of IDs:
```sql
SELECT id, name
FROM customers
WHERE id IN (1, 2, 3, 4, 5);
```

## Rule
If you find yourself planning to loop over results and query for each row — stop.
Rewrite it as a single JOIN or a single IN query.

## One Tool Call Per User Request (Agent Rule)
The agent should answer each user question in at most 2–3 tool calls total:
1. Optional COUNT or schema check
2. One final data query

Never plan more than 3 sequential queries for a single user request.
