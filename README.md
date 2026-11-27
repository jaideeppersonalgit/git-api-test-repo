# Gists API take-home

The solution is in the [`gists-api/`](gists-api/) folder.
See [`gists-api/README.md`](gists-api/README.md) for how to run the app, run the tests and build the Docker image.

Quick start:

    cd gists-api
    docker build -t gists-api .
    docker run --rm -p 8080:8080 gists-api
    curl http://localhost:8080/octocat