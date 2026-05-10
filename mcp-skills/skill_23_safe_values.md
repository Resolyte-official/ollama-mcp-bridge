# SKILL-23: Handle User-Provided Values Safely

## When
The user provides a specific value to search for: a name, ID, date, status, etc.

## Rule
Never interpolate user values directly into raw SQL strings inside the tool.
Pass values as query parameters. If the tool only accepts a full SQL string,
wrap string values in single quotes and cast to the correct type.

## Safe Pattern (parameterised — preferred)
```python
execute_sql("SELECT id, name FROM customers WHERE email = %s", [user_email])
```

## Safe Pattern (if only raw SQL is supported)
```sql
SELECT id, name
FROM customers
WHERE email = 'alice@example.com'
  AND country = 'US';
```

## Dangerous Pattern — Never Do This
```python
query = f"SELECT * FROM customers WHERE name = {user_input}"
# If user_input is: ' OR '1'='1  → SQL injection
```

## Sanitisation Rules When Using Raw SQL
- Wrap all string values in single quotes: `'value'`
- Cast numeric user input explicitly: `WHERE id = 42::integer`
- Cast date user input explicitly: `WHERE date = '2024-01-01'::date`
- Never put user input directly after SQL keywords (FROM, WHERE column name, etc.)

## What to Do If Input Looks Suspicious
If user input contains: `'`, `;`, `--`, `/*`, `DROP`, `DELETE`, `INSERT`
→ Do not query. Tell the user: "That input contains characters that cannot be used in a query."
