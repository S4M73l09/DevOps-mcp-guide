from integrations.gitlab_client import GitLabClient


def _gitlab_error(
    tool: str,
    result: dict[str, object],
) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": result.get("error", "gitlab_request_failed"),
        "message": result.get(
            "message",
            "GitLab request failed.",
        ),
        "status_code": result.get("status_code"),
    }


def register_gitlab_tools(mcp, config) -> None:
    client = GitLabClient()


    @mcp.tool()
    def gitlab_list_pipelines(
        project_id: str,
        ref: str | None = None,
        status: str | None = None,
        per_page: int = 20,
    ) -> dict[str, object]:
        """List GitLab pipelines for a project."""
        result = client.list_pipelines(
            project_id,
            ref,
            status,
            per_page,
        )


        if not result["ok"]:
            return _gitlab_error(
                "gitlab_list_pipelines",
                result,
            )


        pipelines = result["data"]


        return {
            "tool": "gitlab_list_pipelines",
            "ok": True,
            "status": "pipelines_found",
            "project_id": project_id,
            "count": len(pipelines),
            "pipelines": pipelines,
        }


    @mcp.tool()
    def gitlab_get_pipeline(
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        """Get details for a GitLab pipeline."""
        result = client.get_pipeline(
            project_id,
            pipeline_id,
        )


        if not result["ok"]:
            return _gitlab_error(
                "gitlab_get_pipeline",
                result,
            )

        
        return {
            "tool": "gitlab_get_pipeline",
            "ok": True,
            "status": "pipeline_found",
            "project_id": project_id,
            "pipeline": result["data"]
        }

    
    @mcp.tool()
    def gitlab_list_pipeline_jobs(
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        """List jobs belonging to a GitLab pipeline."""
        result = client.list_pipeline_jobs(
            project_id,
            pipeline_id,
        )


        if not result["ok"]:
            return _gitlab_error(
                "gitlab_list_pipeline_jobs",
                result,
            )


        jobs = result["data"]


        return {
            "tool": "gitlab_list_pipeline_jobs",
            "ok": True,
            "status": "jobs_found",
            "project_id": project_id,
            "pipeline_id": pipeline_id,
            "count": len(jobs),
            "jobs": jobs,
        }