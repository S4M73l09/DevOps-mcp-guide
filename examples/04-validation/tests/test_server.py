import pytest
from mcp import Client

from server import mcp


@pytest.mark.anyio
async def test_valid_deployment_request() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "validate_deployment",
            {
                "service": "api",
                "environment": "staging",
                "replicas": 2,
            },
        )


        assert result.is_error is False
        assert result.structured_content == {
            "valid": True,
            "service": "api",
            "environment": "staging",
            "replicas": 2,
        }



@pytest.mark.anyio
async def test_invalid_environment() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "validate_deployment",
            {
                "service": "api",
                "environment": "production-old",
                "replicas": 2,
            },
        )


        assert result.is_error is True



@pytest.mark.anyio
async def test_service_name_too_short() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "validate_deployment",
            {
                "service": "a",
                "environment": "development",
                "replicas": 1,
            },
        )


        assert result.is_error is True