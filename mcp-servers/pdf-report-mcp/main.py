import base64
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
import uvicorn
from playwright.async_api import async_playwright

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

app = FastAPI()


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "pdf-report"})


PORT = int(os.getenv("MCP_PORT", "8091"))
HOST = os.getenv("MCP_HOST", "0.0.0.0")

mcp = FastMCP("pdf-report", host=HOST, port=PORT)


@mcp.tool()
async def generate_pdf_report(
    report_text_markdown: str,
    graph_data: list[str],
    graph_type: str,
    title: str | None = None,
    x_axis_label: str | None = None,
    y_axis_label: str | None = None,
    colors: list[str] | None = None,
) -> tuple[TextContent, ImageContent]:
    """Generate a PDF report containing text and a chart."""

    labels: list[str] = []
    values: list[float] = []

    for data_string in graph_data:
        try:
            row = json.loads(data_string)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse graph data: {exc}") from exc

        if not isinstance(row, dict):
            raise ValueError("Each graph_data item must be a JSON object.")

        label = ""
        value = 0.0
        for key, value_item in row.items():
            if not label and isinstance(value_item, str):
                label = value_item
            elif value == 0 and isinstance(value_item, (int, float)):
                value = float(value_item)

        if label:
            labels.append(label)
            values.append(value)

    html = build_report_html(
        labels=labels,
        values=values,
        report_text_markdown=report_text_markdown,
        graph_type=graph_type,
        title=title or "Generated Graph",
        x_axis_label=x_axis_label or "X Axis",
        y_axis_label=y_axis_label or "Y Axis",
        colors=colors or ["rgba(75, 192, 192, 0.2)"],
    )

    pdf_bytes = await render_pdf_from_html(html)
    return (
        TextContent(type="text", text="PDF report generated successfully."),
        ImageContent(
            type="image",
            data=base64.b64encode(pdf_bytes).decode("ascii"),
            mimeType="application/pdf",
        ),
    )


def build_report_html(
    labels: list[str],
    values: list[float],
    report_text_markdown: str,
    graph_type: str,
    title: str,
    x_axis_label: str,
    y_axis_label: str,
    colors: list[str],
) -> str:
    chart_id = f"chart_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    js_labels = json.dumps(labels)
    js_values = json.dumps(values)
    js_colors = json.dumps(colors)
    js_report = json.dumps(report_text_markdown)

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{title}</title>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    <script src=\"https://cdn.jsdelivr.net/npm/marked/marked.min.js\"></script>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
      .container {{ width: 85%; max-width: 1000px; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: auto; }}
      .chart-wrapper {{ margin-bottom: 30px; }}
      canvas {{ width: 100% !important; height: auto !important; }}
      .report {{ line-height: 1.6; color: #444; }}
      .report h1, .report h2, .report h3 {{ margin-top: 20px; }}
      .report code {{ background: #f1f1f1; padding: 2px 5px; border-radius: 4px; }}
      .report pre {{ background: #f6f6f6; padding: 12px; border-radius: 6px; overflow-x: auto; }}
    </style>
  </head>
  <body>
    <div class=\"container\">
      <h3>{title}</h3>
      <div class=\"chart-wrapper\"><canvas id=\"{chart_id}\"></canvas></div>
      <div id=\"report\" class=\"report\"></div>
    </div>
    <script>
      (function() {{
        const mdText = {js_report};
        document.getElementById('report').innerHTML = marked.parse(mdText);
        const ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx, {{
          type: '{graph_type}',
          data: {{
            labels: {js_labels},
            datasets: [{{
              label: '{title}',
              data: {js_values},
              backgroundColor: {js_colors},
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            }}]
          }},
          options: {{
            responsive: true,
            scales: {{
              y: {{ beginAtZero: true, title: {{ display: true, text: '{y_axis_label}' }} }},
              x: {{ title: {{ display: true, text: '{x_axis_label}' }} }}
            }}
          }}
        }});
      }})();
    </script>
  </body>
</html>
"""


async def render_pdf_from_html(html: str) -> bytes:
    async with async_playwright() as playwright:
        browser_path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or shutil.which("chromium") or shutil.which("chromium-browser")
        launch_kwargs: dict[str, Any] = {"headless": True}
        if browser_path:
            launch_kwargs["executable_path"] = browser_path

        browser = await playwright.chromium.launch(**launch_kwargs)
        page = await browser.new_page(viewport={"width": 1024, "height": 768})
        await page.set_content(html, wait_until="networkidle")
        return await page.pdf(print_background=True, format="Letter")


app.mount("/", mcp.sse_app())


def main() -> int:
    logger.info("Starting MCP server on {host}:{port}", host=HOST, port=PORT)
    uvicorn.run(app, host=HOST, port=PORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
