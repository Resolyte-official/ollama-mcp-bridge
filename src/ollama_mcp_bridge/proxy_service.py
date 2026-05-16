"""Service for handling proxy requests to Ollama"""

import json
from typing import Dict, Any, AsyncGenerator, Union
import httpx
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from .utils import check_ollama_health_async, iter_ndjson_chunks, get_ollama_proxy_timeout_config
from .mcp_manager import MCPManager


class ProxyService:
    """Service handling all proxy-related operations to Ollama with or without MCP tools"""

    def __init__(self, mcp_manager: MCPManager, db_pool=None):
        """Initialize the proxy service with an MCP manager and optional db pool."""
        self.mcp_manager = mcp_manager
        self.db_pool = db_pool
        is_set, timeout_seconds = get_ollama_proxy_timeout_config()
        # Preserve existing behavior when unset (no timeout for /api/chat). If set, honor it.
        self.http_client = httpx.AsyncClient(timeout=timeout_seconds) if is_set else httpx.AsyncClient(timeout=None)

    async def _get_procedural_memory(self, user_query: str) -> Dict[str, Any]:
        """Fetch similar procedural memory for a user query."""
        if not self.db_pool:
            return {}

        try:
            # 1. Get embedding for user query
            embed_payload = {
                "model": "embeddinggemma",
                "input": user_query,
                "dimensions": 768,
                "options": {"temperature": 0.0, "seed": 1024},
            }
            embed_resp = await self.http_client.post(f"{self.mcp_manager.ollama_url}/api/embed", json=embed_payload)
            embed_resp.raise_for_status()
            embed_data = embed_resp.json()
            embedding = embed_data.get("embeddings", [[]])[0]

            if not embedding:
                return {}

            # Pad or truncate if necessary
            dimensions = 768
            if len(embedding) < dimensions:
                embedding += [0.0] * (dimensions - len(embedding))
            elif len(embedding) > dimensions:
                embedding = embedding[:dimensions]

            # 2. Query database for similar memories
            embedding_str = f"[{','.join(map(str, embedding))}]"

            async with self.db_pool.acquire() as conn:
                # Top K = 1, threshold = 0.50 based on fetch_embeddings.py
                row = await conn.fetchrow(
                    """
                    SELECT instruction, tool_sequence, constraints, query_examples, 1 - (embedding <=> $1::vector) AS similarity
                    FROM procedural_memory
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> $1::vector
                    LIMIT 1
                """,
                    embedding_str,
                )

                if row and row["similarity"] >= 0.50:
                    return {
                        "instruction": row["instruction"],
                        "tool_sequence": row["tool_sequence"],
                        "constraints": row["constraints"],
                        "query_examples": row["query_examples"],
                    }

        except Exception as e:
            logger.error(f"Error fetching procedural memory: {e}")

        return {}

    async def _maybe_prepend_system_prompt(self, messages: list) -> tuple[list, Dict[str, Any]]:
        """If a system prompt is configured on the MCP manager, ensure it is the first message.
        Also appends any procedural memory instructions based on the user's latest query as a new system message.

        Does not duplicate if the first message already has role 'system'.
        Returns a tuple of (messages, procedural_memory).
        """
        system_prompt = getattr(self.mcp_manager, "system_prompt", None)
        procedural_memory = {}
        
        # If messages is empty or first message isn't a system role, prepend base system prompt
        if system_prompt:
            if not messages or messages[0].get("role") != "system":
                messages = [{"role": "system", "content": system_prompt}] + messages

        # Look for the last user message to fetch procedural memory
        last_user_message = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if last_user_message:
            user_query = last_user_message.get("content", "")
            if user_query:
                procedural_memory = await self._get_procedural_memory(user_query)
                if procedural_memory:
                    content_parts = []
                    content_parts.append("Important Note: Only use the following instructions if the intent of the user query matches the following query examples.")
                    if procedural_memory.get("query_examples"):
                        qe = procedural_memory['query_examples']
                        qe_str = json.dumps(qe) if isinstance(qe, (list, dict)) else qe
                        content_parts.append(f"Query Examples: {qe_str}")
                    if procedural_memory.get("instruction"):
                        content_parts.append(f"Instruction: {procedural_memory['instruction']}")
                    if procedural_memory.get("tool_sequence"):
                        ts = procedural_memory['tool_sequence']
                        ts_str = json.dumps(ts) if isinstance(ts, (list, dict)) else ts
                        content_parts.append(f"Expected Tool Sequence: {ts_str}")
                    if procedural_memory.get("constraints"):
                        c = procedural_memory['constraints']
                        c_str = json.dumps(c) if isinstance(c, (list, dict)) else c
                        content_parts.append(f"Constraints: {c_str}")
                    
                    if len(content_parts) > 1:
                        messages.append({"role": "system", "content": "\n".join(content_parts)})

        return messages, procedural_memory

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Ollama server and MCP setup"""
        ollama_healthy = await check_ollama_health_async(self.mcp_manager.ollama_url)
        return {
            "status": "healthy" if ollama_healthy else "degraded",
            "ollama_status": "running" if ollama_healthy else "not accessible",
            "tools": len(self.mcp_manager.all_tools),
        }

    async def proxy_chat_with_tools(
        self, payload: Dict[str, Any], stream: bool = False
    ) -> Union[Dict[str, Any], StreamingResponse]:
        """Handle chat requests with potential tool integration

        Args:
            payload: The request payload
            stream: Whether to use streaming response

        Returns:
            Either a dictionary response or a StreamingResponse
        """
        if not await check_ollama_health_async(self.mcp_manager.ollama_url):
            raise httpx.RequestError("Ollama server not accessible", request=None)

        try:
            if stream:
                return StreamingResponse(
                    self._proxy_with_tools_streaming(endpoint="/api/chat", payload=payload),
                    media_type="application/json",
                )
            else:
                return await self._proxy_with_tools_non_streaming(endpoint="/api/chat", payload=payload)
        except httpx.HTTPStatusError as e:
            logger.error(f"Chat proxy failed: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Chat connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Chat proxy failed: {e}")
            raise

    async def _make_final_llm_call(self, endpoint: str, payload: Dict[str, Any], messages: list) -> Dict[str, Any]:
        """Make a final LLM call without tools to get final answer after tool execution"""
        final_payload = dict(payload)
        final_payload["stream"] = False  # Explicitly disable streaming to get single JSON response
        final_payload["messages"] = messages
        final_payload["tools"] = None  # Don't allow more tool calls
        resp = await self.http_client.post(f"{self.mcp_manager.ollama_url}{endpoint}", json=final_payload)
        resp.raise_for_status()
        result = resp.json()
        
        import re
        content = result.get("message", {}).get("content", "")
        if content:
            file_refs = re.findall(r"\[FILE_REF:([a-zA-Z0-9-]+)\]", content)
            for file_id in file_refs:
                if hasattr(self.mcp_manager, "file_store") and file_id in self.mcp_manager.file_store:
                    file_info = self.mcp_manager.file_store[file_id]
                    mime_type = file_info["mime_type"]
                    data = file_info["data"]
                    result["message"]["content"] += f"\n\n![Generated Plot](data:{mime_type};base64,{data})"
                    
        return result

    async def _stream_final_llm_call(
        self, stream_ollama, payload: Dict[str, Any], messages: list
    ) -> AsyncGenerator[bytes, None]:
        """Stream a final LLM call without tools to get final answer after tool execution"""
        final_payload = dict(payload)
        final_payload["messages"] = messages
        final_payload["tools"] = None  # Don't allow more tool calls

        response_text = ""
        done_chunk = None

        ndjson_iter = iter_ndjson_chunks(stream_ollama(final_payload))
        async for json_obj in ndjson_iter:
            msg_content = json_obj.get("message", {}).get("content", "")
            if msg_content:
                response_text += msg_content

            if json_obj.get("done"):
                done_chunk = json_obj
                break
            else:
                if msg_content and "[FILE_REF:" in msg_content:
                    pass
                elif msg_content and "]" in msg_content and response_text.count("[FILE_REF:") > response_text.count("]"):
                    pass
                else:
                    yield (json.dumps(json_obj) + "\n").encode()

        if done_chunk:
            yield (json.dumps(done_chunk) + "\n").encode()

    async def _proxy_with_tools_non_streaming(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle non-streaming chat requests with tools"""
        payload = dict(payload)
        payload["stream"] = False  # Explicitly disable streaming to get single JSON response
        payload["tools"] = self.mcp_manager.all_tools if self.mcp_manager.all_tools else None
        messages = payload.get("messages") or []
        messages, procedural_memory = await self._maybe_prepend_system_prompt(messages)

        # Get max tool rounds from app state (None means unlimited)
        max_rounds = getattr(self.mcp_manager, "max_tool_rounds", None)
        current_round = 0

        # Loop to handle potentially multiple rounds of tool calls
        while True:
            # Call Ollama
            current_payload = dict(payload)
            current_payload["messages"] = messages
            resp = await self.http_client.post(f"{self.mcp_manager.ollama_url}{endpoint}", json=current_payload)
            resp.raise_for_status()
            result = resp.json()

            # Add procedural memory to the final result
            if procedural_memory:
                result["_procedural_memory"] = procedural_memory

            # Check for tool calls
            tool_calls = self._extract_tool_calls(result)
            if not tool_calls:
                # No more tool calls, check for files to append
                import re
                
                # We need to collect file refs from ALL tool messages in this request,
                # as well as the final assistant content, to ensure we don't miss any if the LLM drops them.
                all_contents = [str(m.get("content", "")) for m in messages if m.get("role") == "tool"]
                content = result.get("message", {}).get("content", "")
                all_contents.append(content)
                
                all_text = " ".join(all_contents)
                file_refs = list(dict.fromkeys(re.findall(r"\[FILE_REF:([a-zA-Z0-9-]+)\]", all_text)))
                
                for file_id in file_refs:
                    if hasattr(self.mcp_manager, "file_store") and file_id in self.mcp_manager.file_store:
                        file_info = self.mcp_manager.file_store[file_id]
                        mime_type = file_info["mime_type"]
                        data = file_info["data"]
                        if "message" not in result:
                            result["message"] = {"role": "assistant", "content": ""}
                        result["message"]["content"] += f"\n\n![Generated Plot](data:{mime_type};base64,{data})"
                
                # Clean up any leftover raw FILE_REF strings from the text
                if result.get("message", {}).get("content"):
                    result["message"]["content"] = re.sub(r"\[FILE_REF:[a-zA-Z0-9-]+\]", "", result["message"]["content"])
                    
                return result

            # Add assistant's response with tool calls
            response_content = result.get("message", {}).get("content", "")
            messages.append({"role": "assistant", "content": response_content, "tool_calls": tool_calls})

            # Execute tool calls and add results to messages
            messages = await self._handle_tool_calls(messages, tool_calls)

            # Check if we've reached the maximum number of rounds
            current_round += 1
            if max_rounds is not None and current_round >= max_rounds:
                logger.warning(
                    f"Reached maximum tool execution rounds ({max_rounds}), making final LLM call with tool results"
                )
                final_result = await self._make_final_llm_call(endpoint, payload, messages)
                if procedural_memory:
                    final_result["_procedural_memory"] = procedural_memory
                return final_result

            # Continue loop to get next response

    async def _proxy_with_tools_streaming(self, endpoint: str, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Handle streaming chat requests with tools"""

        payload = dict(payload)
        payload["tools"] = self.mcp_manager.all_tools if self.mcp_manager.all_tools else None
        messages = list(payload.get("messages") or [])
        messages, procedural_memory = await self._maybe_prepend_system_prompt(messages)

        async def stream_ollama(payload_to_send):
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST", f"{self.mcp_manager.ollama_url}{endpoint}", json=payload_to_send
                ) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        # Get max tool rounds from app state (None means unlimited)
        max_rounds = getattr(self.mcp_manager, "max_tool_rounds", None)
        current_round = 0
        first_chunk_sent = False

        # Loop to handle potentially multiple rounds of tool calls
        while True:
            current_payload = dict(payload)
            current_payload["messages"] = messages

            tool_calls = []
            response_text = ""
            done_chunk = None

            ndjson_iter = iter_ndjson_chunks(stream_ollama(current_payload))
            async for json_obj in ndjson_iter:
                msg_content = json_obj.get("message", {}).get("content", "")
                if msg_content:
                    response_text += msg_content

                if not first_chunk_sent and procedural_memory:
                    json_obj["_procedural_memory"] = procedural_memory
                    first_chunk_sent = True

                extracted_calls = self._extract_tool_calls(json_obj)
                if extracted_calls:
                    tool_calls = extracted_calls

                if json_obj.get("done"):
                    done_chunk = json_obj
                    break
                else:
                    if msg_content and "[FILE_REF:" in msg_content:
                        pass # Skip chunks with file ref parts
                    elif msg_content and "]" in msg_content and response_text.count("[FILE_REF:") > response_text.count("]"):
                        pass # Skip chunks that are completing the file ref
                    else:
                        yield (json.dumps(json_obj) + "\n").encode()

            if done_chunk:
                # Do NOT stream the done chunk here, we must only yield it when NO tool calls are found
                pass

            if not tool_calls:
                if done_chunk:
                    yield (json.dumps(done_chunk) + "\n").encode()
                # No tool calls required, streaming complete
                break

            # Tool calls detected; execute them
            messages.append({"role": "assistant", "content": response_text, "tool_calls": tool_calls})
            messages = await self._handle_tool_calls(messages, tool_calls)

            # --- Instantly stream any files generated by the tools to the frontend ---
            import re
            tool_contents = [str(m.get("content", "")) for m in messages[-len(tool_calls):]]
            for i, content in enumerate(tool_contents):
                file_refs = re.findall(r"\[FILE_REF:([a-zA-Z0-9-]+)\]", content)
                for file_id in file_refs:
                    if hasattr(self.mcp_manager, "file_store") and file_id in self.mcp_manager.file_store:
                        file_info = self.mcp_manager.file_store[file_id]
                        mime_type = file_info["mime_type"]
                        data = file_info["data"]
                        
                        img_chunk = {
                            "model": current_payload.get("model", "unknown"),
                            "message": {
                                "role": "assistant",
                                "content": f"\n\n![Generated Plot](data:{mime_type};base64,{data})\n\n"
                            },
                            "done": False
                        }
                        logger.info(f"YIELDING IMAGE CHUNK FOR {file_id}, size: {len(data)}")
                        yield (json.dumps(img_chunk) + "\n").encode()
                
                # Strip FILE_REFs from the message so the LLM doesn't hallucinate paths
                if file_refs:
                    strict_msg = "[Image successfully generated and displayed directly to the user. Do NOT output any markdown image tags or file paths in your response. Just briefly summarize what the plot represents.]"
                    messages[-len(tool_calls) + i]["content"] = re.sub(r"\[FILE_REF:([a-zA-Z0-9-]+)\]", strict_msg, messages[-len(tool_calls) + i]["content"])
            # -------------------------------------------------------------------------

            # Check if we've reached the maximum number of rounds
            current_round += 1
            if max_rounds is not None and current_round >= max_rounds:
                logger.warning(
                    f"Reached maximum tool execution rounds ({max_rounds}), making final LLM call with tool results"
                )
                # Stream the final LLM response with tool results (no more tools allowed)
                async for chunk in self._stream_final_llm_call(stream_ollama, payload, messages):
                    # We might need to inject it here if we never yielded a chunk, but usually we did
                    # in the first round. We'll just yield it.
                    yield chunk
                break

    def _extract_tool_calls(self, result: Dict[str, Any]) -> list:
        """Extract tool calls from response"""
        tool_calls = result.get("message", {}).get("tool_calls", [])
        if tool_calls:
            logger.debug(f"Extracted tool_calls from response: {tool_calls}")
        return tool_calls

    async def _handle_tool_calls(self, messages: list, tool_calls: list) -> list:
        """Process tool calls and get results"""
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            tool_result = await self.mcp_manager.call_tool(tool_name, arguments)
            logger.debug(f"Tool {tool_name} called with args {arguments}, result: {tool_result}")
            messages.append({"role": "tool", "tool_name": tool_name, "content": tool_result})
        return messages

    async def proxy_generic_request(self, path: str, request: Request) -> Response:
        """Proxy any request to Ollama

        Args:
            path: The path to proxy to
            request: The FastAPI request object

        Returns:
            FastAPI Response object
        """
        # Get ollama URL from MCP manager
        ollama_url = self.mcp_manager.ollama_url

        try:
            # Create URL to forward to
            url = f"{ollama_url}/{path}"

            # Copy headers but exclude host
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

            # Get request body if present
            body = await request.body()

            # Create HTTP client
            is_set, timeout_seconds = get_ollama_proxy_timeout_config()
            client_kwargs = {"timeout": timeout_seconds} if is_set else {}
            async with httpx.AsyncClient(**client_kwargs) as client:
                # Forward the request with the same method
                response = await client.request(
                    request.method, url, headers=headers, params=request.query_params, content=body if body else None
                )

                # Return the response as-is
                return Response(
                    content=response.content, status_code=response.status_code, headers=dict(response.headers)
                )
        except httpx.HTTPStatusError as e:
            logger.error(f"Proxy failed for {path}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e
        except httpx.RequestError as e:
            logger.error(f"Proxy connection error for {path}: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Could not connect to target server: {str(e)}") from e
        except Exception as e:
            logger.error(f"Proxy failed for {path}: {e}")
            raise HTTPException(status_code=500, detail=f"Proxy failed: {str(e)}") from e

    async def cleanup(self):
        """Close HTTP client resources"""
        await self.http_client.aclose()
