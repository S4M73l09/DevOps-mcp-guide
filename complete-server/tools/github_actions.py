from integrations.github_client import GitHubClient


def _github_error(
    tool: str,
    result: dict[str, object],
) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": result.get("error", "github_request_failed"),
        "message": result.get(
            "message",
            "GitHub request failed.",
        ),
        "status_code": result.get("status_code"),
    }

def register_github_actions_tools(mcp, config) -> None:
    client = GitHubClient()


    @mcp.tool()
    def github_list_workflows(
        owner: str,
        repo: str,
    ) -> dict[str, object]:
        """List GitHub Actions workflows in a repository."""
        result = client.list_workflows(owner, repo)


        if not result["ok"]:
            return _github_error(
                "github_list_workflows",
                result,
            )

        data = result["data"]


        return {
            "tool": "github_list_workflows",
            "ok": True,
            "status": "workflows_found",
            "owner": owner,
            "repo": repo,
            "count": data.get("total_count", 0),
            "workflows": data.get("workflows", []),
        }


    @mcp.tool()
    def github_list_workflow_runs(
        owner: str,
        repo: str,
        workflow_id: str | None = None,
        branch: str | None = None,
        status: str | None = None,
        per_page: int = 20,
    ) -> dict[str, object]:
        """List GitHub Actions workflow runs."""
        result = client.list_runs(
            owner,
            repo,
            workflow_id,
            branch,
            status,
            per_page,
        )


        if not result["ok"]:
            return _github_error(
                "github_list_workflow_runs",
                result,
            )


        data = result["data"]


        return {
            "tool": "github_list_workflow_runs",
            "ok": True,
            "status": "runs_found",
            "owner": owner,
            "repo": repo,
            "count": data.get("total_count", 0),
            "runs": data.get("workflow_runs", []),
        }

    
    @mcp.tool()
    def github_get_workflow_run(
        owner: str,
        repo: str,
        run_id: int,
    ) -> dict[str, object]:
        """Get details for a GitHub Actions workflow run."""
        result = client.get_run(owner, repo, run_id)


        if not result["ok"]:
            return _github_error(
                "github_get_workflow_run",
                result,
            )


        return {
            "tool": "github_get_workflow_run",
            "ok": True,
            "status": "run_found",
            "owner": owner,
            "repo": repo,
            "run": result["data"],
        }


    @mcp.tool()
    def github_list_run_jobs(
        owner: str,
        repo: str,
        run_id: int,
    ) -> dict[str, object]:
        """List jobs belonging to a GitHub Actions run."""
        result = client.list_jobs(owner, repo, run_id)


        if not result["ok"]:
            return _github_error(
                "github_list_run_jobs",
                result,
            )


        data = result["data"]


        return {
            "tool": "github_list_run_jobs",
            "ok": True,
            "status": "jobs_found",
            "owner": owner,
            "repo": repo,
            "run_id": run_id,
            "count": data.get("total_count", 0),
            "jobs": data.get("jobs", []),
        }
