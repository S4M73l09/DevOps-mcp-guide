from typing import Literal

from pydantic import Field
from mcp.server import MCPServer

mcp = MCPServer("Validation DevOps MCP")

@mcp.tool()
def validate_deployment(
    service: str = Field(min_length=2, max_length=50),
    environment: Literal["Development", "staging", "production"] = "development",
    replicas: int = Field(ge=1, le=10),
) -> dict[str, object]:
    """Validate a deployment request without changing external state."""
    return {
        "valid": True,
        "service": service,
        "environment": environment,
        "replicas": replicas,
    }


if __name__ == "__main__":
    mcp.run()