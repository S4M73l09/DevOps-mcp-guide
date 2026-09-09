from typing import Literal


from mcp.server import MCPServer


from receipt import create_receipt, verify_receipt
from signing import get_signing_provider


mcp = MCPServer("Signed Receipts DevOps MCP")


signing_provider = get_signing_provider()

@mcp.tool()
def simulate_sensitive_action(
    action: Literal["restart_service", "deploy_service"],
    target: str,
    actor: str,
    environment: Literal["development", "staging", "production"],
    authorized: bool,
    human_confirmed: bool,
) -> dict[str, object]:
    """Simulate a sensitive action and generate a signed receipt."""
    if not target.strip():
        return {
            "ok": False,
            "error": "target_required",
            "message": "A target is required.",
        }

    if not actor.strip():
        return {
            "ok": False,
            "error": "actor_required",
            "message": "An actor is required.",
        }

    if not authorized:
        return {
            "ok": False,
            "error": "not_authorized",
            "message": "The actor is not authorized for this action.",
        }

    if not human_confirmed:
        return {
            "ok": False,
            "error": "confirmation_required",
            "message": "Human confirmation is required.",
        }

    input_data = {
        "action": action,
        "target": target,
        "actor": actor,
        "environment": environment,
    }


    output_data = {
        "status": "simulated",
        "message": "No external resource was modified.",
    }


    receipt = create_receipt(
        action=action,
        target=target,
        actor=actor,
        environment=environment,
        input_data=input_data,
        output_data=output_data,
        private_key=signing_provider.private_key,
        key_id=signing_provider.key_id,
    )


    return {
        "ok": True,
        "simulated": True,
        "output": output_data,
        "receipt": receipt,
    }


@mcp.tool()
def verify_signed_receipt(receipt: dict[str, object]) -> dict[str, object]:
    """Verify the signature of a signed receipt."""
    is_valid = verify_receipt(receipt, signing_provider.public_key)


    return {
        "valid": is_valid,
        "message": (
            "The receipt signature is valid."
            if is_valid
            else "The receipt signature is invalid."
        ),
    }


if __name__ == "__main__":
    mcp.run()
