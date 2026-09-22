import json
import subprocess
from pathlib import Path
from tools.receipt_support import attach_signed_receipt

def _run_command(
    arguments: list[str],
    directory: Path | None = None,
) -> dict[str, object]:
    """Run a read-only Docker command."""
    try:
        result = subprocess.run(
            arguments,
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "error": "docker_not_found",
            "message": "Docker is not installed or is not available in PATH.",
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "docker_timeout",
            "message": "Docker command timed out.",
        }

    return {
        "ok": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _list_compose_files(path: str) -> list[Path]:
    directory = Path(path).expanduser().resolve()

    if not directory.is_dir():
        return []

    return sorted(
        file
        for file in directory.iterdir()
        if (
            file.is_file()
            and file.suffix.lower() in {".yaml", ".yml"}
            and "compose" in file.name.casefold()
        )
    )


def _validate_compose_file(path: str) -> Path | None:
    compose_file = Path(path).expanduser().resolve()

    if not compose_file.is_file():
        return None

    if compose_file.suffix.lower() not in {".yaml", ".yml"}:
        return None

    return compose_file


def _compose_file_error(
    tool: str,
    message: str,
) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": "compose_file_not_found",
        "message": message,
    }


def register_docker_tools(mcp, config, signing_provider) -> None:
    @mcp.tool()
    def docker_list_compose_files(path: str) -> dict[str, object]:
        """List Docker Compose files in a directory."""
        directory = Path(path).expanduser().resolve()

        if not directory.is_dir():
            return {
                "tool": "docker_list_compose_files",
                "ok": False,
                "status": "invalid_directory",
                "message": "The path must be an existing directory.",
            }

        files = _list_compose_files(path)
        file_data = [
            {
                "name": compose_file.name,
                "path": str(compose_file),
            }
            for compose_file in files
        ]

        if not files:
            return {
                "tool": "docker_list_compose_files",
                "ok": True,
                "status": "no_compose_files",
                "path": str(directory),
                "files": [],
                "message": "No Docker Compose files were found.",
            }

        message = (
            "One Docker Compose file was found."
            if len(files) == 1
            else "Multiple Docker Compose files were found. Select one explicitly."
        )

        return {
            "tool": "docker_list_compose_files",
            "ok": True,
            "status": "compose_files_found",
            "path": str(directory),
            "files": file_data,
            "message": message,
        }

    @mcp.tool()
    def docker_compose_config(compose_file: str) -> dict[str, object]:
        """Validate an explicitly selected Docker Compose file."""
        compose_path = _validate_compose_file(compose_file)

        if compose_path is None:
            return _compose_file_error(
                "docker_compose_config",
                "The selected Docker Compose file does not exist or is invalid.",
            )

        result = _run_command(
            [
                "docker",
                "compose",
                "-f",
                str(compose_path),
                "config",
                "--quiet",
            ],
            compose_path.parent,
        )

        if result["ok"]:
            return {
                "tool": "docker_compose_config",
                "ok": True,
                "status": "valid",
                "path": str(compose_path),
                "message": "Docker Compose configuration is valid.",
            }

        return {
            "tool": "docker_compose_config",
            "ok": False,
            "status": "invalid_compose",
            "path": str(compose_path),
            "message": "Docker Compose configuration is invalid.",
            "return_code": result.get("return_code"),
            "details": (
                result.get("stderr")
                or result.get("stdout")
                or result.get("message")
                or ""
            ),
        }

    @mcp.tool()
    def docker_compose_images(
        compose_file: str,
        include_receipt: bool = False,
        actor: str = "local-user",
    ) -> dict[str, object]:
        """List images declared in a Docker Compose file."""
        compose_path = _validate_compose_file(compose_file)


        if compose_path is None:
            return _compose_file_error(
                "docker_compose_images",
                "The selected Docker Compose file does not exist or is invalid."
            )

        result = _run_command(
            [
                "docker",
                "compose",
                "-f",
                str(compose_path),
                "config",
                "--images",
            ],
            compose_path.parent,
        )


        if not result["ok"]:
            return {
                "tool": "docker_compose_images",
                "ok": False,
                "status": "image_extraction_failed",
                "path": str(compose_path),
                "message": "Docker Compose images could not be extracted.",
                "return_code": result.get("return_code"),
                "details": (
                    result.get("stderr")
                    or result.get("stdout")
                    or result.get("message")
                    or ""
                ),
            }

        images = [
            line.strip()
            for line in str(result.get("stdout", "")).splitlines()
            if line.strip()
        ]


        response = {
            "tool": "docker_compose_images",
            "ok": True,
            "status": "images_found",
            "path": str(compose_path),
            "images": images,
            "count": len(images),
            "message": (
                f"{len(images)} Docker image(s) found in the Compose file."
            ),
        }

        return attach_signed_receipt(
            response,
            include_receipt=include_receipt,
            action="docker_compose_images",
            target=str(compose_path),
            actor=actor,
            environment=config.environment,
            input_data={
                "compose_file": str(compose_path),
            },
            signing_provider=signing_provider,
        )


    @mcp.tool()
    def docker_image_inspect(image: str) -> dict[str, object]:
        """Inspect a locally available Docker image."""
        result = _run_command(
            [
                "docker",
                "image",
                "inspect",
                image,
                "--format",
                "{{json .}}",
            ]
        )

        if not result["ok"]:
            return {
                "tool": "docker_image_inspect",
                "ok": False,
                "status": "image_not_found",
                "image": image,
                "message": "The Docker image was not found locally.",
                "details": result.get("stderr", ""),
            }

        try:
            image_data = json.loads(str(result["stdout"]))
        except json.JSONDecodeError:
            return {
                "tool": "docker_image_inspect",
                "ok": False,
                "status": "invalid_docker_output",
                "image": image,
                "message": "Docker returned an invalid inspection response.",
            }

        return {
            "tool": "docker_image_inspect",
            "ok": True,
            "status": "image_found",
            "image": image,
            "message": "Docker image inspected successfully.",
            "image_id": image_data.get("Id"),
            "repo_tags": image_data.get("RepoTags", []),
            "repo_digests": image_data.get("RepoDigests", []),
            "architecture": image_data.get("Architecture"),
            "os": image_data.get("Os"),
        }

    @mcp.tool()
    def docker_compose_ps(compose_file: str) -> dict[str, object]:
        """Show the status of services from an explicit Compose file."""
        compose_path = _validate_compose_file(compose_file)

        if compose_path is None:
            return _compose_file_error(
                "docker_compose_ps",
                "The selected Docker Compose file does not exist or is invalid.",
            )

        result = _run_command(
            [
                "docker",
                "compose",
                "-f",
                str(compose_path),
                "ps",
                "--all",
                "--format",
                "json",
            ],
            compose_path.parent,
        )

        if not result["ok"]:
            return {
                "tool": "docker_compose_ps",
                "ok": False,
                "status": "status_unavailable",
                "path": str(compose_path),
                "message": "Docker Compose service status could not be retrieved.",
                "details": result.get("stderr", ""),
            }

        return {
            "tool": "docker_compose_ps",
            "ok": True,
            "status": "status_available",
            "path": str(compose_path),
            "message": "Docker Compose service status retrieved successfully.",
            "services": result.get("stdout", ""),
        }
