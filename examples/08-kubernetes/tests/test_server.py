from subprocess import CompletedProcess
from unittest.mock import patch


import pytest
from mcp import Client


from server import mcp


@pytest.mark.anyio
async def test_current_context() -> None:
    completed = CompletedProcess(
        args=["kubectl", "config", "current-context"],
        returncode=0,
        stdout="minikube\n",
        stderr="",
    )

    
    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "kubernetes_current_context",
                {},
            )


    assert result.structured_content["ok"] is True
    assert result.structured_content["stdout"] == "minikube\n"



@pytest.mark.anyio
async def test_list_pods_in_namespace() -> None:
    completed = CompletedProcess(
        args=[
            "kubectl",
            "get",
            "pods",
            "--namespace",
            "default",
            "--output",
            "wide",
        ],
        returncode=0,
        stdout="NAME  READY  STATUS  RESTARTS  AGE\n",
        stderr="",
    )


    with patch("server.subprocess.run", return_value=completed) as run:
        async with Client(mcp) as client:
            result = await client.call_tool(
                "kubernetes_list_pods",
                {"namespace": "default"},
            )


    run.assert_called_once_with(
        completed.args,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.structured_content["ok"] is True


@pytest.mark.anyio
async def test_list_events() -> None:
    completed = CompletedProcess(
        args=[
            "kubectl",
            "get",
            "events",
            "--namespace",
            "default",
            "--sort-by=.lastTimestamp",
        ],
        returncode=0,
        stdout="LAST SEEN  TYPE  REASON\n",
        stderr="",
    )

    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "kubernetes_list_events",
                {"namespace": "default"},
            )

    assert result.structured_content["ok"] is True


@pytest.mark.anyio
async def test_list_namespaces() -> None:
    completed = CompletedProcess(
        args=["kubectl", "get", "namespaces"],
        returncode=0,
        stdout="NAME      STATUS   AGE\n",
        stderr="",
    )


    with patch("server.subprocess.run", return_value=completed):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "kubernetes_list_namespaces",
                {},
            )

    assert result.structured_content["ok"] is True


@pytest.mark.anyio
async def test_empty_namespace_is_rejected() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "kubernetes_list_pods",
            {"namespace": "  "},
        )

    assert result.is_error is True