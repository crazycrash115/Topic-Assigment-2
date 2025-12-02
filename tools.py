import requests
from datetime import datetime

def fetch_release_metadata() -> dict:
    """
    Fetches current datetime from worldtimeapi.

    Version and release_type are inferred later from the actual changes,
    not from this function.
    """
    try:
        resp = requests.get(
            "https://worldtimeapi.org/api/timezone/America/Toronto",
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        iso = data.get("datetime")
        if not iso:
            raise ValueError("No datetime in response")
    except Exception:
        # Fallback to local UTC time if the API fails
        iso = datetime.utcnow().isoformat() + "Z"

    return {
        "release_date": iso,
    }
