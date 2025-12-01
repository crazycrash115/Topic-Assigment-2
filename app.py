import os
from typing import List, Optional

from config import BASE_DIR
from saftey import is_prompt_injection, check_length, flatten_bullets
from tools import fetch_release_metadata
from telemetry import log_request
from patch_notes import generate_patch_notes

def load_style_guide() -> Optional[str]:
    path = os.path.join(BASE_DIR, "seed", "style_guide.md")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def read_bullets_from_stdin() -> List[str]:
    print("Paste your bullet point changes. One change per line.")
    print("When you are done, enter a blank line and press Enter.\n")

    bullets = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            # Blank line ends input
            break
        bullets.append(line)
    return bullets

def main():
    bullets = read_bullets_from_stdin()
    if not bullets:
        print("No bullets provided. Exiting.")
        return

    flat = flatten_bullets(bullets)

    # Length guard
    if not check_length(flat):
        print("Error: Input is too long. Please split your changes into multiple runs.")
        return

    # Prompt injection guard
    if is_prompt_injection(flat):
        print(
            "Refusing to process: detected potential prompt injection "
            "(e.g., attempts to ignore safety rules)."
        )
        return

    short_description = input("\nOptional: short description of this release (or leave blank): ").strip()
    if not short_description:
        short_description = None

    # Tool use: call external API for release metadata
    metadata = fetch_release_metadata()

    # Load optional style guide
    style_guide = load_style_guide()

    try:
        notes, token_stats = generate_patch_notes(
            bullets=bullets,
            metadata=metadata,
            short_description=short_description,
            style_guide=style_guide,
        )
    except Exception as e:
        print("An error occurred while generating patch notes:")
        print(e)
        return

    # Telemetry logging
    log_request(pathway="tool", token_stats=token_stats)

    print("\n=== Generated Patch Notes ===\n")
    print(notes)
    print("\n=============================\n")

if __name__ == "__main__":
    main()
