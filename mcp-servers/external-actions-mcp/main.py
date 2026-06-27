import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger
from mcp.server.fastmcp import FastMCP
import uvicorn

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

    try:
        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body) if response_body else {}

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Plunk API request failed ({exc.code}): "
            f"{error_body or exc.reason}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Failed to connect to Plunk API: {exc.reason}"
        ) from exc


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
