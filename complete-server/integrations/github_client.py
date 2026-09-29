import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GitHubClient:
    """Small read-only client for the GitHub Actions API."""


    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.api_url = os.getenv(
            "GITHUB_API_URL",
            "https://api.github.com",
        ).rstrip("/")
        self.api_version = os.getenv(
            "GITHUB_API_VERSION",
            "2026-03-10",
        )

    def _request(
        self,
        path: str,
        query: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if not self.token:
            return {
                "ok": False,
                "error": "github_token_missing",
                "message": "GITHUB_TOKEN is not configured.",
            }

        url = f"{self.api_url}{path}"


        if query:
            url = f"{url}?{urlencode(query)}"

        
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": self.api_version,
            },
            method="GET",
        )


        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))


        except HTTPError as error:
            return {
                "ok": False,
                "error": "github_api_error",
                "status_code": error.code,
                "message": (
                    "GitHub rejected the request. "
                    "Check the repository and token permissions."
                ),
            }

        except URLError:
            return {
                "ok": False,
                "error": "github_unreachable",
                "message": "GitHub API could not be reached.",
            }


        except TimeoutError:
            return {
                "ok": False,
                "error": "github_timeout",
                "message": "GitHub API request timed out.",
            }

        return {
            "ok": True,
            "data": payload,
        }

    def list_workflows(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, object]:
        return self._request(
            f"/repos/{owner}/{repo}/actions/workflows",
        )

    def list_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: str | None = None,
        branch: str | None = None,
        status: str | None = None,
        per_page: int = 20,
    ) -> dict[str, object]:
        endpoint = (
            f"/repos/{owner}/{repo}/actions/workflows/"
            f"{workflow_id}/runs"
            if workflow_id
            else f"/repos/{owner}/{repo}/actions/runs"
        )

        query: dict[str, object] = {
            "per_page": min(max(per_page, 1), 100),
        }


        if branch:
            query["branch"] = branch

        
        if status:
            query["status"] = status

        
        return self._request(endpoint, query)


    def get_run(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> dict[str, object]:
        return self._request(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}",
        )


    def list_jobs(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> dict[str, object]:
        return self._request(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
        )
