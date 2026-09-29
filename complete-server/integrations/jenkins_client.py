import base64
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class JenkinsClient:
    """Read-only client for the Jenkins Remote Access API."""


    def __init__(self) -> None:
        self.base_url = os.getenv("JENKINS_URL", "").rstrip("/")
        self.user = os.getenv("JENKINS_USER")
        self.token = os.getenv("JENKINS_TOKEN")


    def _job_path(self, job: str) -> str:
        parts = [quote(part, safe="") for part in job.split("/") if part]
        return "".join(f"/job/{part}" for part in parts)


    def _request(self, path: str, query: dict[str, object] | None = None):
        if not self.base_url:
            return {
                "ok": False,
                "error": "jenkins_url_missing",
                "message": "JENKINS_URL is not configured.",
            }

        url = f"{self.base_url}{path}"


        if query:
            url = f"{url}?{urlencode(query)}"

        headers = {
            "Accept": "application/json",
        }

        if self.user and self.token:
            credentials = f"{self.user}:{self.token}".encode()
            encoded = base64.b64encode(credentials).decode()
            headers["Authorization"] = f"Basic {encoded}"


        request = Request(url, headers=headers, method="GET")


        try:
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "")
                body = response.read().decode("utf-8")


                if "json" in content_type:
                    return {
                        "ok": True,
                        "data": json.loads(body),
                    }

                return {
                    "oK": True,
                    "data": body,
                }

        except HTTPError as error:
            return {
                "ok": False,
                "error": "jenkins_api_error",
                "status_code": error.code,
                "message": "Jenkins rejected the request.",
            }

        except URLError:
            return {
                "ok": False,
                "error": "jenkins_unreachable",
                "message": "Jenkins could not be reached.",
            }

        except TimeoutError:
            return {
                "ok": False,
                "error": "jenkins_timeout",
                "message": "The Jenkins request timed out.",
            }

    def server_info(self):
        return self._request("/api/json")

    def list_jobs(self):
        return self._request(
            "/api/json",
            {
                "tree": "jobs[name,fullName,url,color]",
            },
        )

    def get_jobs(self, job: str):
        return self._request(f"{self._job_path(job)}/api/json")

    def list_builds(self, job: str):
        return self._request(
            f"{self._job_path(job)}/api/json",
            {
                "tree": "builds[number,result,timestamp,duration.url]",
            },
        )

    def get_build(self, job: str, build_number: int):
        return self._request(
            f"{self._job_path(job)}/{build_number}/api/json",
        )

    def get_build_console(self, job: str, build_number: int):
        return self._request(
            f"{self._job_path(job)}/{build_number}/consoleText",
        )

    def get_queue(self):
        return self._request("/queue/api/json")

    def list_agents(self):
        return self._request(
            "/computer/api/json",
            {
                "tree": (
                    "computer[displayName,offline,"
                    "temporarilyOffline,numExecutors,idle]"
                ),
            },
        )