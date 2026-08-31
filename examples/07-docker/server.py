import json
import subprocess


from mcp.server import MCPServer


mcp = MCPServer("Docker DevOps MCP")


def run_docker_command(command: list[str]) -> dict[str, object]:
    """Run an allowlisted read-only Docker command."""
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


    return {
        "ok": completed.returncode == 0,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


@mcp.tool()
def docker_list_containers() -> dict[str, object]:
    """List Docker containers without changing their state."""
    return run_docker_command(
        [
            "docker",
            "ps",
            "--all",
            "--format",
            "{{json .}}"
        ]
    )


@mcp.tool()
def docker_list_images() -> dict[str, object]:
    """List local Docker images without modifying them."""
    return run_docker_command(
        [
            "docker",
            "image",
            "ls",
            "--format",
            "{{json .}}"
        ]
    )


@mcp.tool()
def docker_inspect_container(container: str) -> dict[str, object]:
    """Inspect a Docker container without changing its state."""
    if not container.strip():
        return {
            "ok": False,
            "error": "container_required",
            "message": "A container name or ID is required.",
        }

    return run_docker_command(
        [
            "docker",
            "inspect",
            container,
        ]
    )


if __name__ == "__main__":
    mcp.run()