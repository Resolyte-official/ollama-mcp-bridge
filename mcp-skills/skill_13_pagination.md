# SKILL-13: Pagination

## When
User wants to browse through results, or asks for "next page" / "more records".

## PostgreSQL Pagination Pattern

### Offset-based (simple, use for small datasets)
```sql
SELECT order_id, customer_id, total, status
FROM orders
ORDER BY ordered_at DESC
LIMIT 20 OFFSET 0;   -- page 1

LIMIT 20 OFFSET 20;  -- page 2
LIMIT 20 OFFSET 40;  -- page 3
```

### Keyset / cursor-based (use for large datasets — faster)
Instead of OFFSET, track the last seen value:
```sql
-- Page 1
SELECT order_id, total, ordered_at
FROM orders
ORDER BY ordered_at DESC, order_id DESC
LIMIT 20;

-- Page 2 — pass last values from page 1
SELECT order_id, total, ordered_at
FROM orders
WHERE (ordered_at, order_id) < ('2024-10-15', 1042)
ORDER BY ordered_at DESC, order_id DESC
LIMIT 20;
```

## When to Use Which
| Dataset size   | Method        |
|----------------|---------------|
| < 10,000 rows  | OFFSET        |
| ≥ 10,000 rows  | Keyset/cursor |

## Always Tell the User
- Current page number
- Total count (from COUNT query)
- Whether there are more pages

Example: "Showing records 21–40 of 340. Say 'next page' for more."

## Do Not
Use OFFSET on tables with millions of rows — OFFSET 1000000 forces the DB to scan and discard 1M rows.
