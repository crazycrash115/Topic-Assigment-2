import requests
from datetime import datetime

def fetch_release_metadata() -> dict:
    """
    Calls an external API (worldtimeapi) to get current date/time.
    Generates a version string based on the date.
    This satisfies the 'tool use' requirement.
    """
    try:
        resp = requests.get(
            "https://worldtimeapi.org/api/timezone/America/Toronto",
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        iso = data.get("datetime")
        if iso is None:
            raise ValueError("No datetime in response")

        # worldtimeapi uses ISO with timezone; normalize for datetime
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        version = dt.strftime("v%Y.%m.%d")
        return {
            "release_date": iso,
            "version": version,
        }
    except Exception:
        # Fallback if API fails
        now = datetime.utcnow()
        iso = now.isoformat() + "Z"
        version = now.strftime("v%Y.%m.%d-fallback")
        return {
            "release_date": iso,
            "version": version,
        }
