# SKILL-19: Structuring the Final Response to the User

## When
Every time you have a query result and are about to reply to the user.

## Response Structure

### 1 — Direct answer first
State what was found in one sentence before showing data.
"Found 12 pending orders from the last 7 days."

### 2 — Data table (if ≤ 20 rows)
Show a clean markdown table with human-readable column headers.
Never use raw database column names (customer_id → Customer, ordered_at → Order Date).

### 3 — Key insight (optional but valuable)
One sentence highlighting the most important pattern in the data.
"The largest order is from Alice Martin at $890."

### 4 — Offer next step
One short offer to go deeper.
"Want me to filter by a specific customer or date range?"

## Example

User: "Show me top 5 customers by spending"

Response:
> Here are your top 5 customers by total spending:
>
> | Customer       | Orders | Total Spent |
> |----------------|--------|-------------|
> | Alice Martin   | 14     | $4,320.00   |
> | Bob Tanaka     | 9      | $3,875.50   |
> | Carla Russo    | 11     | $2,990.00   |
> | David Chen     | 7      | $2,150.75   |
> | Eva Müller     | 6      | $1,880.00   |
>
> Alice Martin leads with $4,320 across 14 orders.
> Want a breakdown by product category for any of these customers?

## Do Not
- Return raw JSON or SQL result objects.
- Use database column names as headers.
- End the response without offering a follow-up action.
