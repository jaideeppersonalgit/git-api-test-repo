import pytest
import requests
import responses
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
GITHUB_URL = "https://api.github.com/users/octocat/gists"

SAMPLE_GISTS = [
    {
        "id": "abc123",
        "description": "Hello world",
        "html_url": "https://gist.github.com/octocat/abc123",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "files": {"hello.py": {"filename": "hello.py"}},
    }
]


@responses.activate
def test_returns_list_of_gists_for_octocat():
    responses.add(responses.GET, GITHUB_URL, json=SAMPLE_GISTS, status=200)

    resp = client.get("/octocat")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["id"] == "abc123"
    assert body[0]["files"] == ["hello.py"]


@responses.activate
def test_user_with_no_gists_returns_empty_list():
    responses.add(responses.GET, GITHUB_URL, json=[], status=200)

    resp = client.get("/octocat")

    assert resp.status_code == 200
    assert resp.json() == []


@responses.activate
def test_unknown_user_returns_404():
    responses.add(responses.GET, GITHUB_URL, json={"message": "Not Found"}, status=404)

    resp = client.get("/octocat")

    assert resp.status_code == 404


@responses.activate
def test_github_timeout_returns_502():
    responses.add(responses.GET, GITHUB_URL, body=requests.Timeout())

    resp = client.get("/octocat")

    assert resp.status_code == 502


@responses.activate
def test_rate_limit_returns_429():
    responses.add(
        responses.GET,
        GITHUB_URL,
        json={"message": "rate limit exceeded"},
        status=403,
        headers={"X-RateLimit-Remaining": "0"},
    )

    resp = client.get("/octocat")

    assert resp.status_code == 429


def test_invalid_username_returns_400():
    assert client.get("/bad..name").status_code == 400


def test_health():
    resp = client.get("/_health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.live
def test_live_octocat():
    """Calls the real GitHub API. Run with: pytest -m live"""
    resp = client.get("/octocat")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)