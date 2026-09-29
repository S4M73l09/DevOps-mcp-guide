import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class GitLabClient:
    """Read-only client for the GitLab CI/CD API."""


    def __init__(self) -> None:
        self.token = os.getenv("GITLAB_TOKEN")
        self.api_url = os.getenv(
            "GITLAB_API_URL",
            "https://gitlab.com/api/v4",
        ).rstrip("/")


    def _project_path(self, project_id: str) -> str:
        return quote(str(project_id), safe="")


    def _request(
        self,
        path: str,
        query: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if not self.token:
            return {
                "ok": False,
                "error": "gitlab_token_missing",
                "message": "GITLAB_TOKEN is not configured.",
            }

        url = f"{self.api_url}{path}"


        if query:
            url = f"{url}?{urlencode(query)}"

        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "PRIVATE-TOKEN": self.token,
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            return {
                "ok": False,
                "error": "gitlab_api_error",
                "status_code": error.code,
                "message": "GitLab rejected the request.",
            }

        except URLError:
            return {
                "ok": False,
                "error": "gitlab_unreachable",
                "message": "GitLab API could not be reached.",
            }

        except TimeoutError:
            return {
                "ok": False,
                "error": "gitlab_timeout",
                "message": "GitLab API request timed out.",
            }

        return {
            "ok": True,
            "data": payload,
        }


    def list_pipelines(
        self,
        project_id: str,
        ref: str | None = None,
        status: str | None = None,
        per_page: int = 20,
    ) -> dict[str, object]:
        query: dict[str, object] = {
            "per_page": min(max(per_page, 1), 100),
        }


        if ref:
            query["ref"] = ref

        if status:
            query["status"] = status


        project = self._project_path(project_id)


        return self._request(
            f"/projects/{project}/pipelines",
            query,
        )


    def get_pipeline(
        self,
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        project = self._project_path(project_id)


        return self._request(
            f"/projects/{project}/pipelines/{pipeline_id}",
        )


    def list_pipeline_jobs(
        self,
        project_id: str,
        pipeline_id: int,
    ) -> dict[str, object]:
        project = self._project_path(project_id)


        return self._request(
            f"/projects/{project}/pipelines/{pipeline_id}/jobs",
        )