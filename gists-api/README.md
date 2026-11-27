# GitHub Gists API

A small HTTP service that returns the public gists of a GitHub user.
`GET /<username>` calls the GitHub REST API and returns a JSON list of gists.

All commands below are run from this folder (`gists-api/`).

## Requirements

- Python 3.9+ (to run locally) and/or Docker

No global installs are needed: the local setup uses a virtual environment.

## Run locally

```bash
cd gists-api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --port 8080
```

Try it:

```bash
curl http://localhost:8080/octocat
```

## Run the tests

```bash
cd gists-api
pytest              # offline: the GitHub API is mocked
pytest -m live      # optional: also calls the real GitHub API
```

## Build and run with Docker

```bash
cd gists-api
docker build -t gists-api .
docker run --rm -p 8080:8080 gists-api
curl http://localhost:8080/octocat
```

## API

| Endpoint | Description |
|---|---|
| `GET /<username>` | Public gists of the GitHub user |
| `GET /_health` | Health check |

Example response:

```json
[
  {
    "id": "abc123",
    "description": "Hello world",
    "url": "https://gist.github.com/octocat/abc123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z",
    "files": ["hello.py"]
  }
]
```

Error responses:

| Status | Meaning |
|---|---|
| 400 | Invalid GitHub username |
| 404 | GitHub user not found |
| 429 | GitHub rate limit exceeded |
| 502 | GitHub unreachable or returned an unexpected response |

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | unset | Optional token to raise the GitHub rate limit |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Timeout for calls to GitHub |

Example: `docker run --rm -p 8080:8080 -e GITHUB_TOKEN=xxx gists-api`

## Project structure

```
gists-api/
├── app/
│   ├── config.py          # settings from environment variables
│   ├── github_client.py   # GitHub API calls and error handling
│   └── main.py            # FastAPI app and routes
├── tests/
│   └── test_gists.py      # automated tests (GitHub API mocked)
├── Dockerfile
├── pytest.ini
├── requirements.txt       # runtime dependencies
└── requirements-dev.txt   # runtime + test dependencies
```

## Design notes

- `app/github_client.py` isolates the GitHub call and turns failures into domain exceptions; `app/main.py` maps them to HTTP status codes.
- The health endpoint is `/_health` because GitHub usernames cannot contain underscores, so it cannot clash with a real user.
- Only the first 100 gists are returned (GitHub's maximum page size); pagination is not implemented.
- The container runs as a non-root user and has a healthcheck.