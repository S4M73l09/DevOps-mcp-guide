def register_diagnostic_tools(mcp, config):
    @mcp.tool()
    def server_health() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": config.environment
        }