import pytest
from mcp import Client

from server import mcp


@pytest.mark.anyio
async def test_valid_service_status() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_service_status",
            {"service": "api"},
        )

        assert result.is_error is False
        assert result.structured_content == {
            "ok": True,
            "service": "api",
            "status": "healthy",
        }


@pytest.mark.anyio
async def test_missing_service_returns_structured_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_service_status",
            {"service": "missing-service"},
        )

        assert result.is_error is False
        assert result.structured_content == {
            "ok": False,
            "error": "service_not_found",
            "message": "The requested service does not exist.",
        }


@pytest.mark.anyio
async def test_empty_service_returns_structured_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_service_status",
            {"service": ""},
        )

        assert result.is_error is False
        assert result.structured_content == {
            "ok": False,
            "error": "service_required",
            "message": "A service name is required.",
        }


@pytest.mark.anyio
async def test_timeout_is_marked_as_tool_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_service_status",
            {"service": "backend-timeout"},
        )

        assert result.is_error is True