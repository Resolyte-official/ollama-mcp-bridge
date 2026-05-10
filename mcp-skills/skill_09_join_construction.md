# SKILL-09: JOIN Construction Rules

## When
User needs data from more than one table.

## Step-by-Step
1. Call get_schema() on each table involved.
2. Identify the foreign key relationship.
3. Choose the correct JOIN type.
4. Select only needed columns, prefixed with table alias.

## JOIN Type Decision

| Situation                                         | JOIN to use    |
|---------------------------------------------------|----------------|
| Only want rows that match in both tables          | INNER JOIN     |
| Want all rows from left, NULLs if no right match  | LEFT JOIN      |
| Checking for missing relationships                | LEFT JOIN + IS NULL |
| Never needed for retrieval agent                  | CROSS JOIN     |

## Template
```sql
SELECT
    o.order_id,
    c.name   AS customer_name,
    o.total,
    o.status
FROM orders AS o
INNER JOIN customers AS c ON c.id = o.customer_id
WHERE o.status = 'pending'
LIMIT 50;
```

## Rules
- Always alias every table (AS o, AS c).
- Always prefix every column with its alias (o.total, c.name).
- Never rely on implicit column resolution across tables.
- Add the JOIN filter (ON clause) before the WHERE clause.
- Apply LIMIT after all joins, not before.

## Three or More Tables
Join one table at a time. Verify each ON condition against the schema before adding the next join.
