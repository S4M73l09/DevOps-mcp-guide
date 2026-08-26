from pathlib import Path
import subprocess


from mcp.server import MCPServer


mcp = MCPServer("terraform DevOps MCP")


def validate_terraform_path(path: str) -> Path:
    """Validate that the requested path is a local Terraform directory."""
    terraform_path = Path(path).resolve()

    if not terraform_path.is_dir():
        raise ValueError("The terraform path must be an existing directory.")

    if not any(terraform_path.glob("*.tf")):
        raise ValueError("The directory does not contain Terraform files.")

    return terraform_path


def run_terraform_check(command: list[str], path: Path) -> dict[str, object]:
    """Run an allowlisted Terraform read-only check."""
    completed = subprocess.run(
        command,
        cwd=path,
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
def terraform_format_check(path: str) -> dict[str, object]:
    """Check Terraform formatting without modifying files."""
    terraform_path = validate_terraform_path(path)


    return run_terraform_check(
        ["terraform", "fmt", "-check", "-diff", "-recursive"],
        terraform_path,
    )


@mcp.tool()
def terraform_validate(path: str) ->  dict[str, object]:
    """Validate Terraform configuration without applying changes."""
    terraform_path = validate_terraform_path(path)

    return run_terraform_check(
        ["terraform", "validate"],
        terraform_path,
    )



if __name__ == "__main__":
    mcp.run()