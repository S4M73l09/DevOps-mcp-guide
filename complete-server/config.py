import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfig:
    name: str
    transport: str
    environment: str
    signing_mode: str
    signing_key_path: str


def load_config() -> ServerConfig:
    return ServerConfig(
        name=os.getenv(
            "MCP_SERVER_NAME",
            "DevOps Complete MCP Server",
        ),
        transport=os.getenv(
            "MCP_TRANSPORT",
            "stdio",
        ),
        environment=os.getenv(
            "MCP_ENVIRONMENT",
            "development",
        ),
        signing_mode=os.getenv(
            "MCP_SIGNING_MODE",
            "ephemeral",
        ),
        signing_key_path=os.getenv(
            "MCP_SIGNING_KEY_PATH",
            "keys/dev-signing-key.pem",
        ),
    )