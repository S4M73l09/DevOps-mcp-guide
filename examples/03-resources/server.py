from mcp.server import MCPServer

mcp = MCPServer("Resource DevOps MCP")

@mcp.resource(
    "devops://service-catalog",
    name="service_catalog",
    title="DevOps Service Catalog",
    description="Catalog of services monitored by the platform",
    mime_type="application/json",
)
def service_catalog() -> dict[str, list[dict[str, str]]]:
    """Return a static catalog of DevOps Services."""
    return {
        "services": [
            {"name": "api", "environment": "production", "status": "healthy"},
            {"name": "worker", "environment": "production", "status": "degraded"},
        ]
    }

@mcp.resource(
    "devops://services/{service_name}/status",
    name="service_status",
    title="Service Status",
    description="Return the status of a specific service",
    mime_type="application/json",
)
def service_status(service_name: str) -> dict[str, str]:
    """Return the status of a service identified by its URI."""
    statuses = {
        "api": "healthy",
        "worker": "degraded",
    }

    return {
        "service": service_name,
        "status": statuses.get(service_name, "unknown"),
    }

if __name__ == "__main__":
    mcp.run()