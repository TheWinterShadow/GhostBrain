"""MCP bridge for connecting Pipecat LLM tools to remote MCP servers.

Connects to ObsidianPalace (or any MCP server) over Streamable HTTP,
discovers available tools, and registers them with the Pipecat LLM so the
voice pipeline can call them during a conversation.

Authentication uses GCP OIDC identity tokens for service-to-service auth
when running on Cloud Run. Falls back to no-auth for local development.
"""

import logging
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.services.llm_service import FunctionCallParams, LLMService

logger = logging.getLogger(__name__)


def _fetch_gcp_identity_token(audience: str) -> str | None:
    """Fetch a GCP OIDC identity token from the metadata server.

    Only works on GCP (Cloud Run, GCE, etc). Returns None in local dev
    or if the metadata server is unreachable.

    Args:
        audience: The target audience (typically the server URL).

    Returns:
        A Google-signed JWT identity token, or None.
    """
    try:
        import google.auth.transport.requests
        from google.oauth2 import id_token

        request = google.auth.transport.requests.Request()
        token = id_token.fetch_id_token(request, audience)
        logger.info("Fetched GCP identity token for audience: %s", audience)
        return token
    except Exception as exc:
        logger.debug("Could not fetch GCP identity token (expected in local dev): %s", exc)
        return None


def _mcp_tool_to_function_schema(tool: Any) -> FunctionSchema:
    """Convert an MCP Tool definition to a Pipecat FunctionSchema.

    Args:
        tool: An MCP Tool object with name, description, and inputSchema.

    Returns:
        A Pipecat FunctionSchema for LLM tool registration.
    """
    input_schema = tool.inputSchema or {}
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    description = tool.description or f"MCP tool: {tool.name}"

    return FunctionSchema(
        name=tool.name,
        description=description,
        properties=properties,
        required=required,
    )


def _make_tool_handler(session: ClientSession, tool_name: str):
    """Create a Pipecat function handler that calls an MCP tool.

    Args:
        session: Active MCP ClientSession.
        tool_name: Name of the MCP tool to call.

    Returns:
        An async handler compatible with Pipecat's register_function.
    """

    async def handler(params: FunctionCallParams) -> None:
        logger.info("MCP tool call: %s(%s)", tool_name, params.arguments)
        try:
            result = await session.call_tool(tool_name, dict(params.arguments))

            # MCP results have a `content` list of content blocks.
            # Concatenate text content for the LLM.
            text_parts = []
            for block in result.content:
                if hasattr(block, "text"):
                    text_parts.append(block.text)
                else:
                    text_parts.append(str(block))

            response = "\n".join(text_parts) if text_parts else "Tool returned no content."

            if result.isError:
                logger.warning("MCP tool %s returned error: %s", tool_name, response)

            await params.result_callback(response)
        except Exception as exc:
            logger.exception("MCP tool %s failed: %s", tool_name, exc)
            await params.result_callback(f"Error calling {tool_name}: {exc}")

    return handler


class MCPBridge:
    """Manages a persistent MCP client session for the duration of a call.

    Usage::

        bridge = MCPBridge(server_url="https://lifeos.thewintershadow.com/mcp")
        tools = await bridge.connect()       # Returns list of FunctionSchema
        bridge.register_handlers(llm)        # Registers handlers with LLM
        # ... pipeline runs ...
        await bridge.disconnect()            # Clean teardown
    """

    def __init__(self, server_url: str) -> None:
        self._server_url = server_url
        self._session: ClientSession | None = None
        self._tools: list[FunctionSchema] = []
        self._mcp_tool_names: list[str] = []

        # Context manager state for the streamable HTTP client.
        self._client_cm: Any = None
        self._session_cm: Any = None

    async def connect(self) -> list[FunctionSchema]:
        """Connect to the MCP server and discover available tools.

        Returns:
            List of FunctionSchema objects for Pipecat tool registration.
        """
        # Build auth headers
        headers = {}
        audience = self._server_url.rstrip("/").rsplit("/mcp", 1)[0]
        token = _fetch_gcp_identity_token(audience)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            logger.warning(
                "No GCP identity token available — connecting to MCP server without auth"
            )

        # Open the streamable HTTP transport
        self._client_cm = streamablehttp_client(
            url=self._server_url,
            headers=headers,
        )
        read_stream, write_stream, _ = await self._client_cm.__aenter__()

        # Open the MCP session
        self._session_cm = ClientSession(read_stream, write_stream)
        self._session = await self._session_cm.__aenter__()
        await self._session.initialize()

        # Discover tools
        tools_result = await self._session.list_tools()
        self._tools = []
        self._mcp_tool_names = []

        for tool in tools_result.tools:
            schema = _mcp_tool_to_function_schema(tool)
            self._tools.append(schema)
            self._mcp_tool_names.append(tool.name)
            logger.info("Discovered MCP tool: %s", tool.name)

        logger.info(
            "MCP bridge connected to %s — %d tools available",
            self._server_url,
            len(self._tools),
        )
        return self._tools

    def register_handlers(self, llm: LLMService) -> None:
        """Register MCP tool handlers with the Pipecat LLM.

        Must be called after connect().

        Args:
            llm: The Pipecat LLM service to register handlers with.
        """
        if self._session is None:
            raise RuntimeError("MCPBridge.connect() must be called before register_handlers()")

        for tool_name in self._mcp_tool_names:
            handler = _make_tool_handler(self._session, tool_name)
            llm.register_function(tool_name, handler)
            logger.info("Registered MCP tool handler: %s", tool_name)

    async def disconnect(self) -> None:
        """Cleanly shut down the MCP session and HTTP transport."""
        if self._session_cm is not None:
            try:
                await self._session_cm.__aexit__(None, None, None)
            except Exception as exc:
                logger.debug("MCP session close: %s", exc)
            self._session_cm = None
            self._session = None

        if self._client_cm is not None:
            try:
                await self._client_cm.__aexit__(None, None, None)
            except Exception as exc:
                logger.debug("MCP transport close: %s", exc)
            self._client_cm = None

        logger.info("MCP bridge disconnected")
