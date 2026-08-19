import pytest
from mcp import Client

from server import mcp


@pytest.mark.anyio
async def test_server_can_connect() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "echo_message",
            {"message": "Hello MCP"},
        )

        assert result.structured_content == {
            "message": "Hello MCP",
        }
