import os

GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
# Optional: raises the GitHub rate limit from 60/hour to 5000/hour
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")