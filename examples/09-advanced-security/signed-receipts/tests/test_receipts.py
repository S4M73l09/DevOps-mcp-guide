from copy import deepcopy


import pytest
from mcp import Client


from server import mcp


@pytest.mark.anyio
async def test_authorized_action_creates_receipt() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "simulate_sensitive_action",
            {
                "action": "restart_service",
                "target": "api",
                "actor": "user-123",
                "environment": "staging",
                "authorized": True,
                "human_confirmed": True,
            },
        )


    assert result.structured_content["ok"] is True
    assert result.structured_content["simulated"] is True
    assert "receipt" in result.structured_content



@pytest.mark.anyio
async def test_unauthorized_action_is_rejected() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "simulate_sensitive_action",
            {
                "action": "deploy_service",
                "target": "api",
                "actor": "user-123",
                "environment": "production",
                "authorized": False,
                "human_confirmed": True,
            },
        )


    assert result.structured_content == {
        "ok": False,
        "error": "not_authorized",
        "message": "The actor is not authorized for this action.",
    }


@pytest.mark.anyio
async def test_missing_confirmation_is_rejected() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "simulate_sensitive_action",
            {
                "action": "restart_service",
                "target": "api",
                "actor": "user-123",
                "environment": "staging",
                "authorized": True,
                "human_confirmed": False,
            },
        )


    assert result.structured_content["error"] == "confirmation_required"



@pytest.mark.anyio
async def test_tampered_receipt_is_rejected() -> None:
    async with Client(mcp) as client:
        creation_result = await client.call_tool(
            "simulate_sensitive_action",
            {
                "action": "restart_service",
                "target": "api",
                "actor": "user-123",
                "environment": "staging",
                "authorized": True,
                "human_confirmed": True,
            },
        )


        receipt = creation_result.structured_content["receipt"]
        tampered_receipt = deepcopy(receipt)
        tampered_receipt["target"] = "database"


        verification_result = await client.call_tool(
            "verify_signed_receipt",
            {"receipt": tampered_receipt},
        )


    verification = verification_result.structured_content

    assert verification["valid"] is False
    assert verification["message"] == "The receipt signature is invalid."
