from subprocess import CompletedProcess
from unittest.mock import patch


import pytest
from mcp import Client


from server import mcp


@pytest.mark.anyio
async def test_list_containers() -> None:
    completed = CompletedProcess(
        args=["docker", "ps", "--all"],
        returncode=0,
        stdout="CONTAINER ID IMAGE STATUS NAMES\n",
        stderr="",
    )


    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "docker_list_containers",
                {},
            )


    assert result.structured_content["ok"] is True
    assert result.structured_content["return_code"] == 0


@pytest.mark.anyio
async def test_list_images() -> None:
    completed = CompletedProcess(
        args=["docker", "image", "ls"],
        returncode=0,
        stdout="REPOSITORY  TAG  IMAGE ID  SIZE\n",
        stderr="",
    )


    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "docker_list_images",
                {},
            )


    assert result.structured_content["ok"] is True


@pytest.mark.anyio
async def test_inspect_containers() -> None:
    completed = CompletedProcess(
        args=["docker", "inspect", "api-container"],
        returncode=0,
        stdout='[{"Name": "/api-container"}]',
        stderr="",
    )

    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "docker_inspect_container",
                {"container": "api-container"},
            )

    
    assert result.structured_content["ok"] is True


@pytest.mark.anyio
async def test_empty_container_name() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "docker_inspect_container",
            {"container": ""},
        )


    assert result.structured_content == {
        "ok": False,
        "error": "container_required",
        "message": "A container name or ID is required.",
    }
