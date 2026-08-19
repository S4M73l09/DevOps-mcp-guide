import pytest
from mcp import Client

from server import mcp

@pytest.mark.anyio
async def test_static_resource() -> None:
    async with Client(mcp) as client:
        result = await client.read_resource("devops://service-catalog")

        assert result.contents
        assert result.contents[0].text is not None
        assert "api" in result.contents[0].text

@pytest.mark.anyio
async def test_dynamic_resource() -> None:
    async with Client(mcp) as client:
        result = await client.read_resource(
            "devops://services/worker/status"
        )

        assert result.contents
        assert result.contents[0].text is not None
        assert "degraded" in result.contents[0].text