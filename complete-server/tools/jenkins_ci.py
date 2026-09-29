from integrations.jenkins_client import JenkinsClient


def _error(tool: str, result: dict[str, object]) -> dict[str, object]:
    return {
        "tool": tool,
        "ok": False,
        "status": result.get("error", "jenkins_request_failed"),
        "message": result.get(
            "message",
            "Jenkins request failed.",
        ),
        "status_code": result.get("status_code"),
    }


def register_jenkins_tools(mcp, config) -> None:
    client = JenkinsClient()

    @mcp.tool()
    def jenkins_server_info() -> dict[str, object]:
        """Return basic information about the Jenkins controller."""
        result = client.server_info()

        if not result["ok"]:
            return _error("jenkins_server_info", result)

        return {
            "tool": "jenkins_server_info",
            "ok": True,
            "status": "server_info_found",
            "server": result["data"],
        }

    @mcp.tool()
    def jenkins_list_jobs() -> dict[str, object]:
        """List jobs available in Jenkins."""
        result = client.list_jobs()

        if not result["ok"]:
            return _error("jenkins_list_jobs", result)

        jobs = result["data"].get("jobs", [])

        return {
            "tool": "jenkins_list_jobs",
            "ok": True,
            "status": "jobs_found",
            "count": len(jobs),
            "jobs": jobs,
        }

    @mcp.tool()
    def jenkins_get_job(job: str) -> dict[str, object]:
        """Return details for a Jenkins job or folder job."""
        result = client.get_job(job)

        if not result["ok"]:
            return _error("jenkins_get_job", result)

        return {
            "tool": "jenkins_get_job",
            "ok": True,
            "status": "job_found",
            "job": result["data"],
        }

    @mcp.tool()
    def jenkins_list_builds(job: str) -> dict[str, object]:
        """List recent builds for a Jenkins job."""
        result = client.list_builds(job)

        if not result["ok"]:
            return _error("jenkins_list_builds", result)

        builds = result["data"].get("builds", [])

        return {
            "tool": "jenkins_list_builds",
            "ok": True,
            "status": "builds_found",
            "job": job,
            "count": len(builds),
            "builds": builds,
        }

    @mcp.tool()
    def jenkins_get_build(
        job: str,
        build_number: int,
    ) -> dict[str, object]:
        """Return details for a Jenkins build."""
        result = client.get_build(job, build_number)

        if not result["ok"]:
            return _error("jenkins_get_build", result)

        return {
            "tool": "jenkins_get_build",
            "ok": True,
            "status": "build_found",
            "job": job,
            "build_number": build_number,
            "build": result["data"],
        }

    @mcp.tool()
    def jenkins_get_build_console(
        job: str,
        build_number: int,
    ) -> dict[str, object]:
        """Return console output for a Jenkins build."""
        result = client.get_build_console(job, build_number)

        if not result["ok"]:
            return _error("jenkins_get_build_console", result)

        return {
            "tool": "jenkins_get_build_console",
            "ok": True,
            "status": "console_found",
            "job": job,
            "build_number": build_number,
            "console": result["data"],
        }

    @mcp.tool()
    def jenkins_get_queue() -> dict[str, object]:
        """Return items currently waiting in the Jenkins queue."""
        result = client.get_queue()

        if not result["ok"]:
            return _error("jenkins_get_queue", result)

        return {
            "tool": "jenkins_get_queue",
            "ok": True,
            "status": "queue_found",
            "queue": result["data"],
        }

    @mcp.tool()
    def jenkins_list_agents() -> dict[str, object]:
        """List Jenkins agents and their connection status."""
        result = client.list_agents()

        if not result["ok"]:
            return _error("jenkins_list_agents", result)

        agents = result["data"].get("computer", [])

        return {
            "tool": "jenkins_list_agents",
            "ok": True,
            "status": "agents_found",
            "count": len(agents),
            "agents": agents,
        }