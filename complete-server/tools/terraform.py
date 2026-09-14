from pathlib import Path
import subprocess


def _run_terraform(
    arguments: list[str],
    directory: Path,
) -> dict[str, object]:
    """Run a Terraform command in the selected directory."""
    try:
        result = subprocess.run(
            ["terraform", *arguments],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "error": "terraform_not_found",
            "message": "Terraform is not installed or is not available in PATH.",
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "terraform_timeout",
            "message": "Terraform command timed out.",
        }

    return {
        "ok": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _validate_directory(path: str) -> Path | None:
    directory = Path(path).expanduser().resolve()

    if not directory.is_dir():
        return None

    return directory


def _invalid_directory_response(
    tool: str,
) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": "invalid_directory",
        "message": "The Terraform path must be an existing directory.",
    }


def _init_terraform(directory: Path) -> dict[str, object]:
    return _run_terraform(
        [
            "init",
            "-backend=false",
            "-input=false",
            "-no-color",
        ],
        directory,
    )


def register_terraform_tools(mcp, config) -> None:
    @mcp.tool()
    def terraform_format_check(path: str) -> dict[str, object]:
        """Check Terraform formatting without modifying files."""
        directory = _validate_directory(path)

        if directory is None:
            return _invalid_directory_response("terraform_format_check")

        result = _run_terraform(
            ["fmt", "-check", "-no-color"],
            directory,
        )
        return_code = result.get("return_code")

        if result["ok"]:
            return {
                "tool": "terraform_format_check",
                "ok": True,
                "status": "formatted",
                "path": str(directory),
                "message": "All Terraform files are correctly formatted.",
                "return_code": return_code,
            }

        if return_code == 3:
            files = [
                line.strip()
                for line in str(result.get("stdout", "")).splitlines()
                if line.strip()
            ]

            return {
                "tool": "terraform_format_check",
                "ok": False,
                "status": "format_required",
                "path": str(directory),
                "message": "Some Terraform files require formatting.",
                "files": files,
                "return_code": return_code,
            }

        return {
            "tool": "terraform_format_check",
            "ok": False,
            "status": "execution_error",
            "path": str(directory),
            "message": "Terraform could not complete the formatting check.",
            "return_code": return_code,
            "details": result.get("stderr") or result.get("stdout") or "",
        }

    @mcp.tool()
    def terraform_validate(path: str) -> dict[str, object]:
        """Initialize and validate Terraform without using a backend."""
        directory = _validate_directory(path)

        if directory is None:
            return _invalid_directory_response("terraform_validate")

        init_result = _init_terraform(directory)

        if not init_result["ok"]:
            return {
                "tool": "terraform_validate",
                "ok": False,
                "status": "init_failed",
                "path": str(directory),
                "message": "Terraform initialization failed.",
                "return_code": init_result.get("return_code"),
                "details": (
                    init_result.get("stderr")
                    or init_result.get("stdout")
                    or init_result.get("message")
                    or ""
                ),
            }

        validate_result = _run_terraform(
            ["validate", "-no-color"],
            directory,
        )

        if validate_result["ok"]:
            return {
                "tool": "terraform_validate",
                "ok": True,
                "status": "valid",
                "path": str(directory),
                "message": "Terraform configuration is valid.",
                "return_code": validate_result.get("return_code"),
            }

        return {
            "tool": "terraform_validate",
            "ok": False,
            "status": "validation_failed",
            "path": str(directory),
            "message": "Terraform configuration is invalid.",
            "return_code": validate_result.get("return_code"),
            "details": (
                validate_result.get("stderr")
                or validate_result.get("stdout")
                or ""
            ),
        }

    @mcp.tool()
    def terraform_plan(
        path: str,
        var_file: str | None = None,
    ) -> dict[str, object]:
        """Create a Terraform plan without applying changes."""
        directory = _validate_directory(path)

        if directory is None:
            return _invalid_directory_response("terraform_plan")

        plan_arguments = [
            "plan",
            "-detailed-exitcode",
            "-input=false",
            "-refresh=false",
            "-no-color",
        ]

        if var_file:
            variable_file = Path(var_file).expanduser()

            if not variable_file.is_absolute():
                variable_file = directory / variable_file

            variable_file = variable_file.resolve()

            if not variable_file.is_file():
                return {
                    "tool": "terraform_plan",
                    "ok": False,
                    "status": "invalid_var_file",
                    "path": str(directory),
                    "message": "The variable file does not exist.",
                }

            plan_arguments.append(f"-var-file={variable_file}")

        init_result = _init_terraform(directory)

        if not init_result["ok"]:
            return {
                "tool": "terraform_plan",
                "ok": False,
                "status": "init_failed",
                "path": str(directory),
                "message": "Terraform initialization failed.",
                "return_code": init_result.get("return_code"),
                "details": (
                    init_result.get("stderr")
                    or init_result.get("stdout")
                    or init_result.get("message")
                    or ""
                ),
            }

        plan_result = _run_terraform(
            plan_arguments,
            directory,
        )
        return_code = plan_result.get("return_code")

        if return_code == 0:
            return {
                "tool": "terraform_plan",
                "ok": True,
                "status": "no_changes",
                "path": str(directory),
                "message": "Terraform plan completed with no changes.",
                "return_code": return_code,
            }

        if return_code == 2:
            return {
                "tool": "terraform_plan",
                "ok": True,
                "status": "changes_planned",
                "path": str(directory),
                "message": "Terraform plan contains proposed changes.",
                "return_code": return_code,
                "plan_output": plan_result.get("stdout", ""),
            }

        return {
            "tool": "terraform_plan",
            "ok": False,
            "status": "plan_error",
            "path": str(directory),
            "message": "Terraform could not create a plan.",
            "return_code": return_code,
            "details": (
                plan_result.get("stderr")
                or plan_result.get("stdout")
                or plan_result.get("message")
                or ""
            ),
        }
