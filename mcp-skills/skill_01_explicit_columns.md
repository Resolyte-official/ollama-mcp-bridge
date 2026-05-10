# SKILL-01: Always Name Columns Explicitly

## When
Before writing any SELECT query.

## Rule
Never use SELECT *. Always list only the columns the user actually needs.

## Why
SELECT * on a large table sends every column to the model context. Most columns are irrelevant and waste the token budget.

## Do
```sql
SELECT order_id, customer_name, total, status
FROM orders
WHERE status = 'pending';
```

## Do Not
```sql
SELECT * FROM orders WHERE status = 'pending';
```

## If You Do Not Know the Columns
Call get_schema(table_name) first. Then choose only relevant columns.
