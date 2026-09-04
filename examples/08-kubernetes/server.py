import subprocess

from mcp.server import MCPServer


mcp = MCPServer("Kubernetes DevOps MCP")


def run_kubectl_command(command: list[str]) -> dict[str, object]:
    """Run an allowlisted read-only kubectl command."""
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


def validate_namespace(namespace: str) -> str:
    """Validate a namespace value before using it as a command argument."""
    namespace = namespace.strip()

    if not namespace:
        raise ValueError("The namespace cannot be empty.")

    if namespace.startswith("-"):
        raise ValueError("Invalid namespace value.")

    return namespace


@mcp.tool()
def kubernetes_current_context() -> dict[str, object]:
    """Return the active Kubernetes context without changing it."""
    return run_kubectl_command(
        [
            "kubectl",
            "config",
            "current-context",
        ]
    )


@mcp.tool()
def kubernetes_list_pods(namespace: str = "") -> dict[str, object]:
    """List Kubernetes pods in one namespace or across all namespaces."""
    if namespace != "":
        validated_namespace = validate_namespace(namespace)

        command = [
            "kubectl",
            "get",
            "pods",
            "--namespace",
            validated_namespace,
            "--output",
            "wide",
        ]
    else:
        command = [
            "kubectl",
            "get",
            "pods",
            "--all-namespaces",
            "--output",
            "wide",
        ]

    return run_kubectl_command(command)


@mcp.tool()
def kubernetes_list_events(namespace: str = "") -> dict[str, object]:
    """List Kubernetes events in one namespace or across all namespaces."""
    if namespace != "":
        validated_namespace = validate_namespace(namespace)

        command = [
            "kubectl",
            "get",
            "events",
            "--namespace",
            validated_namespace,
            "--sort-by=.lastTimestamp",
        ]
    else:
        command = [
            "kubectl",
            "get",
            "events",
            "--all-namespaces",
            "--sort-by=.lastTimestamp",
        ]

    return run_kubectl_command(command)


@mcp.tool()
def kubernetes_list_namespaces() -> dict[str, object]:
    """List namespaces visible to the active Kubernetes identity."""
    return run_kubectl_command(
        [
            "kubectl",
            "get",
            "namespace",
        ]
    )


if __name__ == "__main__":
    mcp.run()
