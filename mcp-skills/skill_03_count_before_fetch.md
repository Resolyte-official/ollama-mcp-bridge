# SKILL-03: Count Before Fetch

## When
Any time the query might return many rows — especially without a tight WHERE filter.

## Rule
Before running a data SELECT, run a COUNT version of the same query.
If COUNT > 200, do not fetch raw rows. Summarise instead.

## Step 1 — Run count
```sql
SELECT COUNT(*)
FROM orders
WHERE customer_id = 42;
```

## Step 2a — Count is small (≤ 200): fetch rows
```sql
SELECT order_id, total, status, ordered_at
FROM orders
WHERE customer_id = 42
LIMIT 200;
```

## Step 2b — Count is large (> 200): summarise
Do not fetch all rows. Instead run an aggregation:
```sql
SELECT status, COUNT(*) AS n, SUM(total) AS revenue
FROM orders
WHERE customer_id = 42
GROUP BY status;
```
Then tell the user: "There are 3,847 orders for this customer. Here is a breakdown by status."

## Exception
Skip the COUNT step only when the WHERE clause is on a unique/primary key column, because at most 1 row can be returned.
