from types import SimpleNamespace
from unittest.mock import patch

import pytest
from mcp import Client
from mcp.server import MCPServer

from integrations.jenkins_client import JenkinsClient
from tools.jenkins_ci import register_jenkins_tools


class FakeJenkinsClient:
    """Fake client used to avoid real Jenkins API calls."""

    def server_info(self):
        return {
            "ok": True,
            "data": {
                "displayName": "Jenkins",
                "mode": "NORMAL",
                "numExecutors": 2,
            },
        }

    def list_jobs(self):
        return {
            "ok": True,
            "data": {
                "jobs": [
                    {
                        "name": "devops-pipeline",
                        "fullName": "devops-pipeline",
                        "color": "blue",
                    }
                ]
            },
        }

    def get_job(self, job: str):
        return {
            "ok": True,
            "data": {
                "name": job,
                "displayName": job,
                "buildable": True,
            },
        }

    def list_builds(self, job: str):
        return {
            "ok": True,
            "data": {
                "builds": [
                    {
                        "number": 15,
                        "result": "SUCCESS",
                        "job": job,
                    }
                ]
            },
        }

    def get_build(self, job: str, build_number: int):
        return {
            "ok": True,
            "data": {
                "number": build_number,
                "result": "SUCCESS",
                "job": job,
            },
        }

    def get_build_console(self, job: str, build_number: int):
        return {
            "ok": True,
            "data": f"Build {build_number} for {job} completed successfully.",
        }

    def get_queue(self):
        return {
            "ok": True,
            "data": {
                "items": [],
            },
        }

    def list_agents(self):
        return {
            "ok": True,
            "data": {
                "computer": [
                    {
                        "displayName": "built-in",
                        "offline": False,
                        "temporarilyOffline": False,
                        "numExecutors": 2,
                        "idle": True,
                    }
                ]
            },
        }


# Las pruebas internas usan el modo legacy para evitar la negociación automatica del protocolo durante la conexion
# en memoria.
# Se usaria este comando para volver al modo dinamico: async with Client(jenkins_server) as client:


@pytest.fixture
def jenkins_server():
    mcp = MCPServer("Jenkins CI Test Server")
    config = SimpleNamespace()

    with patch(
        "tools.jenkins_ci.JenkinsClient",
        return_value=FakeJenkinsClient(),
    ):
        register_jenkins_tools(mcp, config)
        yield mcp


@pytest.mark.anyio
async def test_jenkins_server_info(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_server_info",
            {},
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "server_info_found"
    assert content["server"]["mode"] == "NORMAL"


@pytest.mark.anyio
async def test_jenkins_list_jobs(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_list_jobs",
            {},
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "jobs_found"
    assert content["count"] == 1
    assert content["jobs"][0]["name"] == "devops-pipeline"


@pytest.mark.anyio
async def test_jenkins_list_builds(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_list_builds",
            {
                "job": "devops-pipeline",
            },
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "builds_found"
    assert content["builds"][0]["result"] == "SUCCESS"


@pytest.mark.anyio
async def test_jenkins_get_build(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_get_build",
            {
                "job": "devops-pipeline",
                "build_number": 15,
            },
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "build_found"
    assert content["build_number"] == 15
    assert content["build"]["result"] == "SUCCESS"


@pytest.mark.anyio
async def test_jenkins_console_output(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_get_build_console",
            {
                "job": "devops-pipeline",
                "build_number": 15,
            },
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "console_found"
    assert "completed successfully" in content["console"]


@pytest.mark.anyio
async def test_jenkins_queue(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_get_queue",
            {},
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "queue_found"
    assert content["queue"]["items"] == []


@pytest.mark.anyio
async def test_jenkins_agents(jenkins_server) -> None:
    async with Client(jenkins_server, mode="legacy") as client:
        result = await client.call_tool(
            "jenkins_list_agents",
            {},
        )

    content = result.structured_content

    assert content["ok"] is True
    assert content["status"] == "agents_found"
    assert content["count"] == 1
    assert content["agents"][0]["offline"] is False


def test_jenkins_requires_url(monkeypatch) -> None:
    monkeypatch.delenv("JENKINS_URL", raising=False)

    client = JenkinsClient()
    result = client.server_info()

    assert result["ok"] is False
    assert result["error"] == "jenkins_url_missing"
