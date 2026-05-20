"""MCP server for generating plots from CSV data."""

import base64
import io
import json
from pathlib import Path
from urllib.request import Request

import click
import pandas as pd
import structlog
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent, TextContent
from starlette.responses import JSONResponse, Response

from plotting_mcp.configure_logging import configure_logging
from plotting_mcp.constants import MCP_PORT
from plotting_mcp.plot import generate_geo_heatmap_html, plot_to_bytes
from plotting_mcp.utils import sizeof_fmt

logger = structlog.get_logger(__name__)

mcp = FastMCP(name="plotting-mcp", host="0.0.0.0", port=MCP_PORT)


@mcp.tool()
def generate_plot(
    csv_data: str, plot_type: str = "line", json_kwargs: str = "None"
) -> tuple[TextContent, ImageContent]:
    """
    Generate a plot from CSV data.

    Args:
        csv_data (str): CSV data as a string
        plot_type (str): Type of plot to generate (line, bar, pie, worldmap).
         If not specified, defaults to "line".
        json_kwargs (str, optional): JSON string with additional parameters for the plot.
            If not specified, the plot will be generated with default parameters.
            Additional plotting parameters in JSON format. For line/bar plots, Seaborn is used,
            so any parameters supported by Seaborn's plotting functions can be passed.
            For bar/line plots, you can specify:
                - `x` (str): Column name for x-axis
                - `y` (str): Column name for y-axis
                - `hue` (str): Column name for color encoding
            For worldmap plots, coordinate data is expected with latitude/longitude columns:
                - Latitude columns: lat, latitude, y
                - Longitude columns: lon, lng, long, longitude, x
                - `s` (int): marker size (default: 50)
                - `c` (str): marker color (default: 'red')
                - `alpha` (float): transparency (default: 0.7). Between 0 and 1.
                - `marker` (str): marker style (default: 'o')

    Returns:
        tuple[TextContent, ImageContent]: A tuple containing a success message and the
        generated plot as an image.
    """
    if json_kwargs != "None":
        try:
            kwargs = json.loads(json_kwargs)
        except Exception:
            logger.exception("Invalid JSON for kwargs")
            raise
    else:
        kwargs = {}

    try:
        df = pd.read_csv(io.StringIO(csv_data))

        plot_bytes = plot_to_bytes(df, plot_type, **kwargs)

        logger.info(
            "Plot generated successfully",
            plot_type=plot_type,
            kwargs=kwargs,
            size=sizeof_fmt(len(plot_bytes)),
        )
        return (
            TextContent(type="text", text="Plot generated successfully"),
            ImageContent(
                type="image",
                data=base64.b64encode(plot_bytes).decode(),
                mimeType="image/png",
            ),
        )
    except Exception:
        logger.exception("Error generating plot")
        raise


@mcp.tool()
def generate_geo_heatmap(
    csv_data: str, json_kwargs: str = "None"
) -> tuple[TextContent, ImageContent]:
    """
    Generate a geographical heatmap from CSV data using Folium.

    Args:
        csv_data (str): CSV data as a string
        json_kwargs (str, optional): JSON string with additional parameters for the heatmap.
            If not specified, the heatmap will be generated with default parameters.
            Parameters can include:
                - `weight_col` (str): Column name for weights
                - `zoom_start` (int): Initial zoom level (default: 11)
                - `tiles` (str): Map tiles (default: 'CartoDB dark_matter')
                - `title` (str): Title for the map
                - `radius` (int): Radius of each "point" of the heatmap (default: 15)
                - `blur` (int): Amount of blur (default: 20)
                - `min_opacity` (float): Minimum opacity (default: 0.3)
                - `max_zoom` (int): Zoom level where points reach maximum intensity (default: 15)
                - `gradient` (dict): Dictionary mapping floats to colors

    Returns:
        tuple[TextContent, ImageContent]: A tuple containing a success message and the
        generated HTML map encapsulated as a base64 encoded document.
    """
    if json_kwargs != "None":
        try:
            kwargs = json.loads(json_kwargs)
        except Exception:
            logger.exception("Invalid JSON for kwargs")
            raise
    else:
        kwargs = {}

    try:
        df = pd.read_csv(io.StringIO(csv_data))
        html_str = generate_geo_heatmap_html(df, **kwargs)

        logger.info(
            "Geo heatmap generated successfully",
            kwargs=kwargs,
            size=sizeof_fmt(len(html_str)),
        )
        return (
            TextContent(type="text", text="Geo heatmap generated successfully"),
            ImageContent(
                type="image",
                data=base64.b64encode(html_str.encode("utf-8")).decode(),
                mimeType="text/html",
            )
        )
    except Exception:
        logger.exception("Error generating geo heatmap")
        raise


# Health check endpoint
@mcp.custom_route("/", methods=["GET"])
def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


# Have to do it this way to conform the string expected by uvicorn.run
# Expected format: "<module>:<attribute>"
starlette_app = mcp.streamable_http_app()


@click.command()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set the logging level (default: INFO)",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development (default: False)",
)
@click.option(
    "--transport",
    default="http",
    type=click.Choice(["stdio", "http"]),
    help="Transport type for the MCP server (default: http)",
)
def main(log_level: str = "INFO", reload: bool = False, transport: str = "http") -> None:
    """Main entry point for the MCP server."""
    logging_dict = configure_logging(log_level=log_level)

    if transport == "stdio":
        mcp.run("stdio")
    elif transport == "http":
        uvicorn.run(
            "plotting_mcp.server:starlette_app",
            host=mcp.settings.host,
            port=mcp.settings.port,
            log_config=logging_dict,
            reload=reload,
            reload_dirs=[str(Path(__file__).parent.absolute())],
            timeout_graceful_shutdown=2,
        )
    else:
        raise ValueError(f"Unsupported transport type: {transport}")


if __name__ == "__main__":
    main()
