import json
import os
import time

from config import BASE_DIR
from patch_notes import generate_patch_notes
from tools import fetch_release_metadata


def load_style_guide() -> str | None:
    """
    Same behavior as app.load_style_guide, but duplicated here
    so eval_runner does not depend on app.py.
    """
    path = os.path.join(BASE_DIR, "seed", "style_guide.md")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def run_eval() -> None:
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    total = len(tests)
    passed = 0

    # We can reuse the same metadata / style guide for all tests
    metadata = fetch_release_metadata()
    style_guide = load_style_guide()

    for idx, test in enumerate(tests, 1):
        print(f"Running test {idx}/{total}: {test['name']}")

        bullets = test["input_bullets"]
        expected = [p.lower() for p in test.get("expected_patterns", [])]

        start = time.time()
        text, token_stats = generate_patch_notes(
            bullets=bullets,
            metadata=metadata,
            short_description=None,
            style_guide=style_guide,
        )
        latency = time.time() - start

        out_lower = text.lower()
        ok = all(p in out_lower for p in expected)

        if ok:
            passed += 1
            print(f"  PASS ({latency:.2f}s)")
        else:
            print(f"  FAIL ({latency:.2f}s)")
            print("    Output was:")
            print(text)
            print("    Expected patterns:", expected)

        print()

    rate = (passed / total) * 100
    print(f"RESULT: {passed}/{total} tests passed ({rate:.1f}%).")


if __name__ == "__main__":
    run_eval()