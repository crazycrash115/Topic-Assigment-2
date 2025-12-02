import subprocess
import time
import random
from typing import Dict, List, Tuple, Optional

SYSTEM_PROMPT = """
You are a release notes assistant for a software team.

Your job:
- Turn raw bullet point change lists into clear, concise, professional patch notes.
- Use the provided version, release date, and inferred release type.
- If release_type is MAJOR, treat it like a big update (new systems, big features, big reworks).
- If release_type is MINOR, treat it like a smaller update (bug fixes, tweaks, small improvements).

STRICT FORMAT RULES:
First the releaes date (you should have it), only include yyyy/mm/dd :
- You must organize all changes into up to three sections ONLY:
  1) Gameplay changes
  2) Balances
  3) Bug fixes
- Do not invent or use any other section titles.
- Every change you mention must be placed under exactly one of these sections.
- If a section has no relevant changes do not add the section.

Guidelines for what goes where:
- Gameplay changes: new mechanics, new content, new maps or modes or levels, new areas,
 new bosses or enemies, new systems, big reworks that change how the game is played.
- Balances: number tweaks, damage changes, cooldowns, health or armor, economy values, 
difficulty tuning, spawn rates, anything that is mostly about values or tuning.
- Bug fixes: crashes, glitches, broken interactions, visual issues, 
anything explicitly fixed or resolved.

You must:
- Stay factual to the provided bullets.
- Keep tone clean and professional.
- Use short readable bullet points under each section.

You must NOT:
- Invent features or details that are not in the bullets.
- Add any sections other than: Gameplay changes, Balances, Bug fixes.
- Leave changes ungrouped.
"""

_MAJOR_KEYWORDS = [
    "new map",
    "new mode",
    "new level",
    "new area",
    "new boss",
    "new enemy",
    "new system",
    "new mechanic",
    "new character",
    "new hero",
    "new weapon",
    "new gun",
    "overhaul",
    "rework",
    "revamp",
    "redesign",
    "expansion",
    "season",
    "battle pass",
    "leaderboard",
    "progression system",
]

def _infer_release_type(bullets: List[str]) -> str:
    """
    Infer whether this feels like a major or minor update based on the bullets.

    Heuristic:
    - If any bullet includes obvious "big feature" keywords -> major.
    - If there is BIG changes like adding a new mechanic or like new charector/weapon its probably major
    - If its small (1-4) its probably minor but check each point and see if theres big changes to the game
    - Otherwise -> minor.
    """
    joined = " ".join(bullets).lower()

    # Keyword based "this is a big update" detection
    for kw in _MAJOR_KEYWORDS:
        if kw in joined:
            return "major"

    # If there are lots of changes, treat it as a major update
    if len(bullets) >= 6:
        return "major"

    # Default: minor update
    return "minor"

def _semantic_version(release_type: str) -> str:
    """
    Creates a fake version number:

      - MAJOR update -> X.0
      - MINOR update -> X.Y (Y != 0)

    X and Y are random integers.
    """
    major = random.randint(1, 5)

    if release_type == "major":
        return f"{major}.0"
    else:
        minor = random.randint(1, 9)  # avoid .0 for minor
        return f"{major}.{minor}"

class LLMClient:
    def __init__(self, model: str = "gemma2:9b"):
        self.model = model

    def _run_ollama(self, prompt: str) -> str:
        process = subprocess.Popen(
            ["ollama", "run", self.model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        stdout, stderr = process.communicate(prompt)

        if process.returncode != 0:
            err_text = (stderr or "").strip()
            raise RuntimeError(
                err_text or f"ollama run {self.model} failed with code {process.returncode}"
            )

        return stdout

    def generate_patch_notes(
        self,
        bullets: List[str],
        metadata: Dict[str, str],
        short_description: Optional[str] = None,
        style_guide: Optional[str] = None,
    ) -> Tuple[str, Dict]:

        release_type = _infer_release_type(bullets)  # "major" or "minor"
        version = _semantic_version(release_type)
        release_date = metadata.get("release_date", "")

        parts = [
            f"Version: {version}",
            f"Release Type: {release_type.upper()} update",
            f"Release Date: {release_date}",
        ]

        # User added
        if short_description:
            parts.append("Short Description:\n" + short_description)

        if style_guide:
            parts.append("Style Guide:\n" + style_guide)

        bullet_text = "\n".join("- " + b for b in bullets)
        parts.append("Raw Bullets:\n" + bullet_text)

        full_prompt = (
            SYSTEM_PROMPT.strip()
            + "\n\n### USER MESSAGE ###\n"
            + "\n\n".join(parts)
            + "\n\n### RESPONSE ###\n"
        )

        start = time.time()
        output = self._run_ollama(full_prompt)
        latency = time.time() - start

        token_stats = {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "latency_s": latency,
        }

        return output.strip(), token_stats
