from mcp.server import MCPServer

mcp = MCPServer("First Tool DevOps MCP")


@mcp.tool()
def echo_message(message: str) -> dict[str, str]:
    """Return the received message as structured output."""
    return {
        "message": message,
    }


if __name__ == "__main__":
    mcp.run()
