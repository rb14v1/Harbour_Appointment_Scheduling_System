"""Health check for the Appointment Scheduling Management System.

Calls the running backend's /api/healthz/ endpoint, which also checks MongoDB.

Usage (backend running):
    python healthz.py

Exit code 0 means healthy. Exit code 1 means down or unhealthy.
Set HEALTHZ_URL to check a different address.
"""
import os
import sys
import urllib.error
import urllib.request

HEALTHZ_URL = os.environ.get("HEALTHZ_URL", "http://127.0.0.1:8000/api/healthz/")
TIMEOUT_SECONDS = 5


def check(url=HEALTHZ_URL):
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()
    except (urllib.error.URLError, OSError) as exc:
        return None, str(exc)


def main():
    status, body = check()
    if status == 200:
        print(f"OK: {body}")
        return 0
    if status is None:
        print(f"DOWN: cannot reach {HEALTHZ_URL} ({body})")
    else:
        print(f"UNHEALTHY: HTTP {status} {body}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
