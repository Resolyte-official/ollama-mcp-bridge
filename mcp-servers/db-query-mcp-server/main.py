from mcp.server.fastmcp import FastMCP
from typing import Any
import json

from query import build_select_query, execute_query

mcp = FastMCP("db-tools")


@mcp.tool()
async def dynamic_select_query(
    table: str,
    projection: list[str],
    where: dict[str, Any] | None = None,
    joins: list[str] | None = None,
    group_by: list[str] | None = None,
    having: str | None = None,
    order_by: list[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> str:
    """
    Execute a safe dynamic SELECT query.

    Rules:
    - Only SELECT queries allowed
    - All filters are parameterized
    - projection must be explicit, if user didnt provide any fetch all columns you think might be relevant
    - limit max = 100
    """

    if not isinstance(projection, list) or not all(isinstance(x, str) for x in projection):
        raise ValueError("projection must be list[str]")

    if where and not isinstance(where, dict):
        raise ValueError("where must be dict")

    if joins and not isinstance(joins, list):
        raise ValueError("joins must be list[str]")

    if group_by and not isinstance(group_by, list):
        raise ValueError("group_by must be list[str]")

    if order_by and not isinstance(order_by, list):
        raise ValueError("order_by must be list[str]")

    # Build query
    sql, params = build_select_query(
        table=table,
        projection=projection,
        where=where,
        joins=joins,
        group_by=group_by,
        having=having,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )

    print("SQL:", sql)
    print("PARAMS:", params)

    dsn = "postgresql://mcpserver:open-db@db:5432/school-db"

    try:
        rows = await execute_query(dsn, sql, params)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "row_count": len(rows),
        "rows": rows[:100]  # safety cap
    }, default=str)

if __name__ == "__main__":
    mcp.run(transport="stdio")
