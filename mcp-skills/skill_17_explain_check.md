# SKILL-17: Use EXPLAIN to Check Query Safety

## When
Before running any query on a table you suspect is large (> 10,000 rows).

## Rule
Run EXPLAIN (without ANALYZE) first. It is read-only and does not execute the query.
Check for Seq Scan on large tables — this means the query will be slow.

## How to Run
```sql
EXPLAIN
SELECT order_id, total
FROM orders
WHERE customer_id = 42;
```

## What to Look For

| Plan node seen         | Meaning                                   | Action                        |
|------------------------|-------------------------------------------|-------------------------------|
| Index Scan             | Using an index — fast                     | Safe to run                   |
| Index Only Scan        | Reading from index only — very fast       | Safe to run                   |
| Seq Scan               | Scanning entire table — potentially slow  | Add filter or warn user       |
| Nested Loop + Seq Scan | Repeated full scans in a join             | Rewrite join or add index     |
| Hash Join              | In-memory hash — usually acceptable       | Check row estimates            |

## Row Estimate Check
Look for `rows=NNNN` in the EXPLAIN output.
If estimated rows > 10,000 on a Seq Scan — warn the user before executing.

## Do Not
Run EXPLAIN ANALYZE on unknown queries — it actually executes the query and can be slow.
Use plain EXPLAIN for safety checks.
