import json
import os
from datetime import datetime
from typing import Optional, Dict

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "requests.log")

def log_request(pathway: str, token_stats: Optional[Dict] = None) -> None:
    """
    Log one JSON line per LLM request.
    pathway: 'tool', 'none', or 'rag' (here we use 'tool').
    token_stats: dict with prompt_tokens, completion_tokens, total_tokens, latency_s.
    For local Gemma via Ollama, token counts are None, latency is filled.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pathway": pathway,
        "tokens": token_stats,
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Do not crash the app because of logging issues
        pass
