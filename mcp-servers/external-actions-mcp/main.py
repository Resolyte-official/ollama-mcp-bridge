import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

import time
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger
from mcp.server.fastmcp import FastMCP
import uvicorn
import base64
import aiofiles
from mcp.types import ImageContent, TextContent

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
            "service": "external-actions",
        }
    )

PORT = int(os.getenv("MCP_PORT", "8090"))
HOST = os.getenv("MCP_HOST", "0.0.0.0")

mcp = FastMCP("external-actions", host=HOST, port=PORT)


@mcp.tool()
async def demo_action(num: int, **kwargs) -> any:
    if not isinstance(num, int) or num <= 0:
        raise ValueError("The 'num' parameter must be a positive integer.")

    # Normalize nested JSON kwargs commonly produced by the LLM (e.g. {"kwargs": "{\"parent_email\": \"x@x.com\"}"})
    if "kwargs" in kwargs:
        nested = kwargs.get("kwargs")
        try:
            if isinstance(nested, str):
                parsed = json.loads(nested)
            elif isinstance(nested, dict):
                parsed = nested
            else:
                parsed = None

            if isinstance(parsed, dict):
                # merge parsed into kwargs without overwriting explicit top-level keys
                for k, v in parsed.items():
                    if k not in kwargs:
                        kwargs[k] = v
                # remove the nested wrapper to avoid confusion later
                kwargs.pop("kwargs", None)
        except Exception:
            logger.warning("demo_action: failed to parse nested JSON 'kwargs', continuing with original kwargs")

    match num:
        case 1: # generate time-table as pdf for all sections of grade 10th
            # time.sleep(2)
            pdf_path = "static/grade10_timetable.pdf"
            try:
                async with aiofiles.open(pdf_path, mode='rb') as f:
                    pdf_bytes = await f.read()
                    
                return (
                    TextContent(type="text", text="PDF report generated successfully."),
                    ImageContent(
                        type="image",
                        data=base64.b64encode(pdf_bytes).decode("ascii"),
                        mimeType="application/pdf",
                    ),
                )
            except FileNotFoundError:
                return TextContent(type="text", text=f"Error: The file at {pdf_path} was not found.")
            except Exception as e:
                return TextContent(type="text", text=f"An error occurred: {str(e)}")

        case 2: # generate exam reports for all students and email them to their parents
            # time.sleep(3)
            pdf_bytes = None
            pdf_path = "static/exam_report.pdf"
            try:
                async with aiofiles.open(pdf_path, mode='rb') as f:
                    pdf_bytes = await f.read()

                to = kwargs.get("parent_email", "example@mail.com")
                resp = await send_email(
                    to=to,
                    subject="Exam Report",
                    body="Please find attached the exam report for your ward.",
                    attachments=[
                        {
                            "filename": "exam-report.pdf",
                            "content": base64.b64encode(pdf_bytes).decode("ascii"),
                            "contentType": "application/pdf",
                        }
                    ],
                )

                if isinstance(resp, dict) and resp.get("status_code"):
                    body = resp.get("body")
                    if isinstance(body, dict) and body.get("success") is True:
                        return TextContent(
                            type="text",
                            text=("mailed reports to all parents successfully."),
                        )
                    else:
                        print(f"Email sending failed: {body}")
                        return TextContent(type="text", text=f"email failed")
                else:
                    print(f"Unexpected response from send_email: {resp}")
                    return TextContent(type="text", text=f"email failed")

            except FileNotFoundError:
                return TextContent(type="text", text=f"Error: The file at {pdf_path} was not found.")
            except Exception as e:
                return TextContent(type="text", text=f"An error occurred: {str(e)}")

        case 3: # generate geo heatmap for student distribution
            map_path = "static/student_distribution_map.html"
            try:
                async with aiofiles.open(map_path, mode='rb') as f:
                    html_bytes = await f.read()
                return (
                    TextContent(type="text", text="Geo heatmap generated successfully"),
                    ImageContent(
                        type="image",
                        data=base64.b64encode(html_bytes).decode(),
                        mimeType="text/html",
                    )
                )
            except FileNotFoundError:
                return TextContent(type="text", text=f"Error: The file at {map_path} was not found.")
            except Exception as e:
                return TextContent(type="text", text=f"An error occurred: {str(e)}")

        case 4: # generate class wise attendance report pdf
            # time.sleep(2)
            pdf_path = "static/attendance_report.pdf"
            try:
                async with aiofiles.open(pdf_path, mode='rb') as f:
                    pdf_bytes = await f.read()
                    
                return (
                    TextContent(type="text", text="PDF report generated successfully."),
                    ImageContent(
                        type="image",
                        data=base64.b64encode(pdf_bytes).decode("ascii"),
                        mimeType="application/pdf",
                    ),
                )
            except FileNotFoundError:
                return TextContent(type="text", text=f"Error: The file at {pdf_path} was not found.")
            except Exception as e:
                return TextContent(type="text", text=f"An error occurred: {str(e)}")
                
        case _:
            # The wildcard '_' acts as the 'default' case
            return {"message": "no action exists for this number."}

@mcp.tool()
async def send_email(
    to: str | dict[str, str] | list[str | dict[str, str]],
    *,
    subject: str | None = None,
    body: str | None = None,
    template: str | None = None,
    from_email: str | dict[str, str] | None = None,
    subscribed: bool | None = None,
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    reply: str | None = None,
    attachments: list[dict[str, Any]] | None = None,
) -> dict:
    """
    Send a transactional email using the Plunk API.

    Required:
        - to
        - Either:
            * template
          OR
            * subject + body

    Conditionally required:
        - from_email if not using a template with a configured sender.
    """

    api_key = os.getenv("PLUNK_API_KEY")
    if not api_key:
        raise RuntimeError("PLUNK_API_KEY is required.")

    url = os.getenv(
        "PLUNK_API_BASE_URL",
        "https://next-api.useplunk.com/v1/send",
    )

    # Validate recipient(s)
    if not to:
        raise ValueError("'to' is required.")

    def _validate_recipient(recipient: Any) -> None:
        if isinstance(recipient, str):
            if not recipient.strip():
                raise ValueError("Recipient email cannot be empty.")
            return

        if isinstance(recipient, dict):
            email = recipient.get("email")
            if not isinstance(email, str) or not email.strip():
                raise ValueError(
                    "Recipient object must contain a non-empty 'email' field."
                )
            return

        raise ValueError(
            "Recipients must be strings or objects containing an 'email' field."
        )

    if isinstance(to, list):
        if not to:
            raise ValueError("'to' cannot be an empty list.")
        for recipient in to:
            _validate_recipient(recipient)
    else:
        _validate_recipient(to)

    # Validate content requirements
    if not template and (not subject or not body):
        raise ValueError(
            "Either 'template' or both 'subject' and 'body' must be provided."
        )

    # Subject validation
    if subject:
        if "\n" in subject or "\r" in subject:
            raise ValueError(
                "The 'subject' field cannot contain newline characters."
            )

        if len(subject) > 998:
            raise ValueError(
                "Subject length must not exceed 998 characters."
            )

    # Reply-to validation
    if reply and not isinstance(reply, str):
        raise ValueError("'reply' must be a string email address.")

    # Header validation
    if headers:
        for key, value in headers.items():
            if "\r" in key or "\n" in key:
                raise ValueError(
                    f"Header name '{key}' contains invalid characters."
                )

            if "\r" in value or "\n" in value:
                raise ValueError(
                    f"Header value for '{key}' contains invalid characters."
                )

            if len(value) > 998:
                raise ValueError(
                    f"Header value for '{key}' exceeds 998 characters."
                )

    # Build payload
    payload: dict[str, Any] = {
        "to": to,
    }

    if template is not None:
        payload["template"] = template

    if subject is not None:
        payload["subject"] = subject

    if body is not None:
        payload["body"] = body

    payload["from"] = "ai@abcdery.com"

    if subscribed is not None:
        payload["subscribed"] = subscribed

    if data is not None:
        payload["data"] = data

    if headers is not None:
        payload["headers"] = headers

    if reply is not None:
        payload["reply"] = reply

    if attachments is not None:
        payload["attachments"] = attachments

    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    def _do_request_sync(req: urllib.request.Request) -> tuple[int, str]:
        try:
            with urllib.request.urlopen(req) as response:
                status = response.getcode()
                body = response.read().decode("utf-8")
                return status, body

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Plunk API request failed ({exc.code}): {error_body or exc.reason}"
            ) from exc

        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to connect to Plunk API: {exc.reason}") from exc

    status_code, response_body = await asyncio.to_thread(_do_request_sync, request)

    try:
        parsed = json.loads(response_body) if response_body else None
    except Exception:
        parsed = response_body

    logger.info("Plunk send_email response: status={status}", status=status_code)

    # Treat non-2xx as errors
    if not (200 <= status_code < 300):
        raise RuntimeError(f"Plunk API returned status {status_code}: {response_body}")

    return {"status_code": status_code, "body": parsed}


app.mount("/", mcp.sse_app())


def main():
    logger.info("Starting MCP server on {host}:{port}", host=HOST, port=PORT)
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )


if __name__ == "__main__":
    sys.exit(main())
