from types import SimpleNamespace
from unittest.mock import patch
from integrations.gitlab_client import GitLabClient

import pytest
from mcp import Client
from mcp.server import MCPServer


from tools.gitlab_ci import register_gitlab_tools


class FakeGitLabClient:
    """Fake client used to avoid real GitLab API calls."""


    def list_pipelines(
        self,
        project_id: str,
        ref: str | None = None,
        status: str | None = None,
        per_page: int = 20,
    ) -> dict[str, object]:
        return {
            "ok": True,
            "data": [
                {
                    "id": 101,
                    "status": "success",
                    "ref": ref or "main",
                    "project_id": project_id,
                }
            ],
        }

    
    def get_pipeline(
        self,
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        return {
            "ok": True,
            "data": {
                "id": pipeline_id,
                "status": "success",
                "project_id": project_id,
            },
        }


    def list_pipeline_jobs(
        self,
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        return {
            "ok": True,
            "data": [
                {
                    "id": 501,
                    "name": "test",
                    "status": "success",
                    "pipeline_id": pipeline_id,
                }
            ],
        }


@pytest.fixture
def gitlab_server():
    mcp = MCPServer("GitLab CI Test Server")
    config = SimpleNamespace()


    with patch(
        "tools.gitlab_ci.GitLabClient",
        return_value=FakeGitLabClient(),
    ):
        register_gitlab_tools(mcp, config)
        yield mcp


@pytest.mark.anyio
async def test_list_gitlab_pipelines(gitlab_server) -> None:
    async with Client(gitlab_server) as client:
        result = await client.call_tool(
            "gitlab_list_pipelines",
            {
                "project_id": "my-group/my-project",
                "ref": "main",
                "status": "success",
            },
        )

    content = result.structured_content


    assert content["ok"] is True
    assert content["status"] == "pipelines_found"
    assert content["count"] == 1
    assert content["pipelines"][0]["status"] == "success"



@pytest.mark.anyio
async def test_list_gitlab_pipeline_jobs(gitlab_server) -> None:
    async with Client(gitlab_server) as client:
        result = await client.call_tool(
            "gitlab_list_pipeline_jobs",
            {
                "project_id": "my-group/my-project",
                "pipeline_id": 101,
            },
        )


    content = result.structured_content


    assert content["ok"] is True
    assert content["status"] == "jobs_found"
    assert content["count"] == 1
    assert content["jobs"][0]["name"] == "test"


# Esta parte se encarga de una prueba de credenciales.

def test_gitlab_client_requires_token(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_TOKEN", raising= False)


    client = GitLabClient()


    result = client.list_pipelines(
        "my-group/my-project",
    )


    assert result["ok"] is False
    assert result["error"] == "gitlab_token_missing"