from typing import List, Dict, Optional, Tuple
from llm_client import LLMClient

def generate_patch_notes(
    bullets: List[str],
    metadata: Dict[str, str],
    short_description: Optional[str] = None,
    style_guide: Optional[str] = None,
) -> Tuple[str, dict]:
    """
    Main core function that converts bullets into patch notes.
    This is used both by app.py and eval_runner.py.
    """
    client = LLMClient()
    text, token_stats = client.generate_patch_notes(
        bullets=bullets,
        metadata=metadata,
        short_description=short_description,
        style_guide=style_guide,
    )
    return text, token_stats
