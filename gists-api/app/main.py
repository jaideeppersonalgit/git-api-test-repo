import logging
import re

from fastapi import FastAPI, HTTPException

from app import github_client as gh

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="GitHub Gists API", version="1.0.0")

# GitHub usernames: alphanumeric or hyphens, must start alphanumeric, max 39 chars
USERNAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")


@app.get("/_health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/{username}")
def get_gists(username: str) -> list:
    if not USERNAME_RE.fullmatch(username):
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    try:
        return gh.fetch_public_gists(username)
    except gh.GitHubUserNotFound:
        raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
    except gh.GitHubRateLimited:
        raise HTTPException(status_code=429, detail="GitHub rate limit exceeded, try again later")
    except gh.GitHubUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc))