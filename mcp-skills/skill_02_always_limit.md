# SKILL-02: Always Add LIMIT to Every SELECT

## When
Every SELECT query without exception.

## Rule
Always append LIMIT N to every SELECT. Default limit is 50. Never execute a SELECT without a LIMIT unless you are running COUNT or a scalar aggregation.

## Thresholds
| User intent            | LIMIT to use |
|------------------------|--------------|
| Show me some records   | 10           |
| General retrieval      | 50           |
| Explicit "all records" | 200 max, then summarise |
| COUNT / SUM / AVG      | No LIMIT needed |

## Do
```sql
SELECT product_name, price
FROM products
WHERE category = 'electronics'
LIMIT 50;
```

## Do Not
```sql
SELECT product_name, price
FROM products
WHERE category = 'electronics';
```

## If User Asks for "All Records"
Run COUNT first. If count > 200, tell the user how many records exist and return a summary instead of raw rows.
