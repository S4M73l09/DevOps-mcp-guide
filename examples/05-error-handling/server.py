from mcp.server import MCPServer

mcp = MCPServer("Error Handling DevOps MCP")


@mcp.tool()
def get_service_status(service: str) -> dict[str, object]:
    """Return a service status or a controlled error."""
    if not service:
        return {
            "ok": False,
            "error": "service_required",
            "message": "A service name is required.",
        }

    if service == "missing-service":
        return {
            "ok": False,
            "error": "service_not_found",
            "message": "The requested service does not exist.",
        }

    if service == "backend-timeout":
        raise TimeoutError(
            "The status provider did not respond within the time limit."
        )

    return {
        "ok": True,
        "service": service,
        "status": "healthy",
    }


if __name__ == "__main__":
    mcp.run()