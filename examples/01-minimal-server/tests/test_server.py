import pytest
from mcp import Client

from server import mcp

@pytest.mark.anyio
async def test_server_can_connect() -> None:
    async with Client(mcp) as client:
        assert client.server_capabilities is not None