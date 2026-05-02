from mcp.server.fastmcp import FastMCP
from typing import Any, List
import json

from query import build_select_query, execute_query, _validate_identifier

mcp = FastMCP("db-tools")


@mcp.tool()
async def dynamic_select_query(
    table: str,
    projection: list[str],
    where: dict[str, Any] | None = None,
    joins: List[dict[str, str]] | None = None,
    group_by: list[str] | None = None,
    having: str | None = None,
    order_by: list[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> str:

    if not isinstance(projection, list):
        raise ValueError("projection must be list[str]")

    if where and not isinstance(where, dict):
        raise ValueError("where must be dict")

    if joins and not isinstance(joins, list):
        raise ValueError("joins must be list[dict]")

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

    dsn = "postgresql://mcpserver:open-db@db:5432/school-db"

    try:
        rows = await execute_query(dsn, sql, params)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "row_count": len(rows),
        "rows": rows[:100]
    }, default=str)


@mcp.tool()
async def call_db_function(
    function_name: str,
    args: list[Any] | None = None,
) -> str:

    if not isinstance(function_name, str):
        raise ValueError("function_name must be string")

    if args is None:
        args = []

    if not isinstance(args, list):
        raise ValueError("args must be list")

    _validate_identifier(function_name, "function_name")

    placeholders = ", ".join(["?"] * len(args))
    sql = f"SELECT * FROM {function_name}({placeholders})"

    dsn = "postgresql://mcpserver:open-db@db:5432/school-db"

    try:
        rows = await execute_query(dsn, sql, args)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "row_count": len(rows),
        "rows": rows[:100]
    }, default=str)


if __name__ == "__main__":
    mcp.run(transport="stdio")