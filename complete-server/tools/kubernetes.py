import json
import os
import subprocess
from pathlib import Path
from tools.receipt_support import attach_signed_receipt


def _configured_context() -> str | None:
    return os.getenv("KUBERNETES_CONTEXT") or None


def _run_kubectl(
    arguments: list[str],
    context: str | None = None,
    timeout: int = 30,
) -> dict[str, object]:
    """Run a read-only kubectl command."""
    selected_context = context or _configured_context()
    command = ["kubectl"]


    if selected_context:
        command.extend(["--context", selected_context])


    command.extend(arguments)


    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "error": "kubectl_not_found",
            "message": "kubectl is not installed or is unavailable in PATH.",
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "kubectl_timeout",
            "message": "The kubectl command timed out.",
        }

    return {
        "ok": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "context": selected_context or "current-context",
    }


def _command_error(
    tool: str,
    result: dict[str, object],
) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": result.get("error", "kubectl_command_failed"),
        "message": result.get(
            "message",
            "The kubectl command failed.",
        ),
        "details": result.get("stderr") or result.get("stdout") or "",
        "context": result.get("context"),
        "return_code": result.get("return_code"),
    }


def _parse_resource_list(
    tool: str,
    result: dict[str, object],
    namespace: str | None = None,
) -> dict[str, object]:
    if not result["ok"]:
        return _command_error(tool, result)

    try:
        payload = json.loads(str(result["stdout"]))
    except json.JSONDecodeError:
        return {
            "tool": tool,
            "ok": False,
            "status": "invalid_json",
            "message": "kubectl returned an invalid JSON response.",
            "context": result.get("context"),
        }

    resources = []

    for item in payload.get("items", []):
        metadata = item.get("metadata", {})
        status = item.get("status", {})

        resource = {
            "name": metadata.get("name"),
            "namespace": metadata.get("namespace"),
            "labels": metadata.get("labels", {}),
            "status": status,
        }

        resources.append(resource)

    return {
        "tool": tool,
        "ok": True,
        "status": "resources_found",
        "context": result.get("context"),
        "namespace": namespace or "all",
        "count": len(resources),
        "resources": resources,
    }


def register_kubernetes_tools(mcp, config, signing_provider) -> None:
    @mcp.tool()
    def kubernetes_current_context(
        context: str | None = None,
    ) -> dict[str, object]:
        """Show the active Kubernetes context."""
        result = _run_kubectl(
            ["config", "current-context"],
            context=context,
        )

        if not result["ok"]:
            return _command_error(
                "kubernetes_current_context",
                result,
            )

        active_context = str(result["stdout"]).strip()


        return {
            "tool": "kubernetes_current_context",
            "ok": True,
            "status": "context_detected",
            "context": active_context,
            "message": f"Active Kubernetes context: {active_context}",
        }

    @mcp.tool()
    def kubernetes_list_namespaces(
        context: str | None = None,
    ) -> dict[str, object]:
        """List namespaces available in the selected Kubernetes context."""
        result = _run_kubectl(
            ["get", "namespaces", "-o", "json"],
            context=context,
        )

        return _parse_resource_list(
            "kubernetes_list_namespaces",
            result,
        )

    @mcp.tool()
    def kubernetes_list_pods(
        namespace: str,
        context: str | None = None,
    ) -> dict[str, object]:
        """List pods in a specific namespace."""
        result = _run_kubectl(
            [
                "--namespace",
                namespace,
                "get",
                "pods",
                "-o",
                "json",
            ],
            context=context,
        )

        return _parse_resource_list(
            "kubernetes_list_pods",
            result,
            namespace,
        )


    @mcp.tool()
    def kubernetes_list_deployments(
        namespace: str,
        context: str | None = None,
    ) -> dict[str, object]:
        """List deployments in a specific namespace."""
        result = _run_kubectl(
            [
                "--namespace",
                namespace,
                "get",
                "deployments",
                "-o",
                "json",
            ],
            context=context,
        )

        return _parse_resource_list(
            "kubernetes_list_deployments",
            result,
            namespace,
        )


    @mcp.tool()
    def kubernetes_list_services(
        namespace: str,
        context: str | None = None,
    ) -> dict[str, object]:
        """List services in a specific namespace."""
        result = _run_kubectl(
            [
                "--namespace",
                namespace,
                "get",
                "services",
                "-o",
                "json",
            ],
            context=context,
        )


        return _parse_resource_list(
            "kubernetes_list_services",
            result,
            namespace,
        )

    @mcp.tool()
    def kubernetes_list_events(
        namespace: str,
        context: str | None = None,
    ) -> dict[str, object]:
        """List recent events in a specific namespace."""
        result = _run_kubectl(
            [
                "--namespace",
                namespace,
                "get",
                "events",
                "--sort-by=.lastTimestamp",
                "-o",
                "json",
            ],
            context=context,
        )

        return _parse_resource_list(
            "kubernetes_list_events",
            result,
            namespace,
        )


    @mcp.tool()
    def kubernetes_validate_manifest(
        path: str,
        context: str | None = None,
        include_receipt: bool = False,
        actor: str = "local-user",
    ) -> dict[str, object]:
        """Validate a Kubernetes manifest or Kustomize overlay without applying it."""
        manifest_path = Path(path).expanduser().resolve()


        if not manifest_path.exists():
            return {
                "tool": "kubernetes_validate_manifest",
                "ok": False,
                "status": "path_not_found",
                "message": "The manifest path does not exist.",
                "path": str(manifest_path),
            }

        if manifest_path.is_dir():
            arguments = [
                "apply",
                "--dry-run=client",
                "-k",
                str(manifest_path),
                "-o",
                "yaml",
            ]
        else:
            arguments = [
                "apply",
                "--dry-run=client",
                "-f",
                str(manifest_path),
                "-o",
                "yaml",
            ]

        result = _run_kubectl(
            arguments,
            context=context,
            timeout=60,
        )

        if not result["ok"]:
            return {
                "tool": "kubernetes_validate_manifest",
                "ok": False,
                "status": "validation_failed",
                "path": str(manifest_path),
                "context": result.get("context"),
                "message": "The kubernetes manifest is not valid.",
                "details": result.get("stderr")
                or result.get("stdout")
                or "",
            }

        response = {
            "tool": "kubernetes_validate_manifest",
            "ok": True,
            "status": "manifest_valid",
            "path": str(manifest_path),
            "context": result.get("context"),
            "message": (
                "The Kubernetes manifest is valid. "
                "No resources were applied."
            ),
        }

        return attach_signed_receipt(
            response,
            include_receipt=include_receipt,
            action="kubernetes_validate_manifest",
            target=str(manifest_path),
            actor=actor,
            environment=config.environment,
            input_data={
                "path": str(manifest_path),
                "context": context,
            },
            signing_provider=signing_provider,
        )
