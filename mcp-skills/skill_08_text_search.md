# SKILL-08: Text Search in PostgreSQL

## When
User asks to find records by name, description, or any text field.

## Options by Use Case

### Case-insensitive exact word match
Use ILIKE (PostgreSQL-specific, case-insensitive LIKE):
```sql
SELECT id, name FROM products WHERE name ILIKE '%keyboard%';
```

### Starts with
```sql
SELECT id, name FROM customers WHERE name ILIKE 'ali%';
```

### Full-text search on long text columns
Use to_tsvector and to_tsquery for performance on large text:
```sql
SELECT id, title
FROM articles
WHERE to_tsvector('english', body) @@ to_tsquery('english', 'database & performance')
LIMIT 20;
```

### Multiple terms (OR)
```sql
SELECT id, name FROM products
WHERE name ILIKE '%laptop%' OR name ILIKE '%notebook%';
```

## Performance Warning
LIKE '%term%' (leading wildcard) cannot use a standard B-Tree index — it forces a seq scan.
If the table is large, warn the user the query may be slow, or use full-text search instead.

## Do Not
Use LIKE when ILIKE is needed — LIKE is case-sensitive in PostgreSQL.
