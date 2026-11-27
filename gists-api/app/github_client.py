import logging
from typing import Any

import requests

from app import config

logger = logging.getLogger(__name__)


class GitHubUserNotFound(Exception):
    """The requested GitHub user does not exist."""


class GitHubRateLimited(Exception):
    """GitHub API rate limit has been exceeded."""


class GitHubUnavailable(Exception):
    """GitHub could not be reached or returned an unexpected response."""


def _headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gists-api",
    }
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
    return headers


def fetch_public_gists(username: str) -> list:
    """Return the public gists of a GitHub user, formatted for our API."""
    url = f"{config.GITHUB_API_URL}/users/{username}/gists"
    try:
        resp = requests.get(
            url,
            headers=_headers(),
            params={"per_page": 100},
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        logger.error("Timeout calling GitHub for user %s", username)
        raise GitHubUnavailable("GitHub API timed out") from exc
    except requests.RequestException as exc:
        logger.error("Error calling GitHub: %s", exc)
        raise GitHubUnavailable("Could not reach GitHub API") from exc

    if resp.status_code == 404:
        raise GitHubUserNotFound(username)
    if resp.status_code in (403, 429) and resp.headers.get("X-RateLimit-Remaining") == "0":
        raise GitHubRateLimited("GitHub rate limit exceeded")
    if resp.status_code != 200:
        logger.error("Unexpected GitHub status %s", resp.status_code)
        raise GitHubUnavailable(f"GitHub returned status {resp.status_code}")

    return [_format_gist(g) for g in resp.json()]


def _format_gist(gist: dict) -> dict:
    return {
        "id": gist.get("id"),
        "description": gist.get("description"),
        "url": gist.get("html_url"),
        "created_at": gist.get("created_at"),
        "updated_at": gist.get("updated_at"),
        "files": list((gist.get("files") or {}).keys()),
    }