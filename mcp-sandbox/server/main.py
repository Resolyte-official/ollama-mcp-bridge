import sys
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

from server.tools import (
    read_file,
    write_file,
    list_dir,
    run_shell,
    run_python,
)

# Configure logger
logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "{message}"
    ),
)

app = FastAPI()

@app.get("/health")
async def health():
    return JSONResponse(
        {
            "status": "healthy",
            "service": "mcp-sandbox",
        }
    )

mcp = FastMCP("mcp-sandbox", host="0.0.0.0", port=8080)

# Register tools
mcp.tool()(read_file)
mcp.tool()(write_file)
mcp.tool()(list_dir)
mcp.tool()(run_shell)
mcp.tool()(run_python)

app.mount("/", mcp.sse_app())

def main():
    logger.info("Starting MCP server")

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    sys.exit(main())