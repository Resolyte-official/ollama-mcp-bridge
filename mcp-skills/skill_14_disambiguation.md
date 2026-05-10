# SKILL-14: Disambiguating Vague User Requests

## When
The user's request is unclear, missing a filter, or could match multiple tables.

## Rule
Never guess. Ask one specific clarifying question before writing any query.

## Common Ambiguities and What to Ask

### Vague entity
User: "Show me the orders"
Problem: Which orders? All of them? By which customer? Which status?
Ask: "Sure — do you want all orders, or filtered by a specific customer, status, or date range?"

### Missing time range
User: "Show me revenue"
Problem: Revenue for what period?
Ask: "Which time period? For example: this month, last quarter, or a specific date range?"

### Ambiguous table
User: "Show me users"
Problem: Tables might be `customers`, `users`, `accounts`, or `staff`
Action: Call list_tables(), find the best match, confirm:
"I found a table called `customers`. Is that what you mean by users?"

### Multiple possible interpretations
User: "Top products"
Problem: Top by revenue? By quantity sold? By rating?
Ask: "Top products by what — total revenue, number of orders, or current stock?"

## Format for Asking
Keep it short. Ask only one question. Offer 2–3 options when possible.

Good: "Do you want orders filtered by status (pending / shipped / delivered), or all statuses?"
Bad: "Could you please clarify what you mean by orders and also specify the time range and the customer and the status you are interested in?"
