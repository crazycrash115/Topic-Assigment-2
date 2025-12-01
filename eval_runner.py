import json
import os
from typing import List, Dict

from patch_notes import generate_patch_notes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_PATH = os.path.join(BASE_DIR, "tests.json")

def load_tests() -> List[Dict]:
    with open(TESTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_eval():
    tests = load_tests()
    total = len(tests)
    passed = 0

    # Use fixed metadata for eval to avoid hitting external API
    metadata = {
        "release_date": "2025-01-01T00:00:00Z",
        "version": "vTEST",
    }

    for test in tests:
        name = test.get("name", "unnamed")
        bullets = test.get("input_bullets", [])
        expected_patterns = test.get("expected_patterns", [])

        print(f"Running test: {name}")
        output, _ = generate_patch_notes(
            bullets=bullets,
            metadata=metadata,
            short_description=None,
            style_guide=None,
        )

        lower_output = output.lower()
        ok = all(pattern.lower() in lower_output for pattern in expected_patterns)

        if ok:
            passed += 1
            print("  -> PASS\n")
        else:
            print("  -> FAIL")
            print("     Output:")
            print(output)
            print("     Expected patterns:", expected_patterns)
            print()

    if total > 0:
        rate = (passed / total) * 100
    else:
        rate = 0.0
    print(f"Summary: {passed}/{total} tests passed ({rate:.1f}%).")

if __name__ == "__main__":
    run_eval()
