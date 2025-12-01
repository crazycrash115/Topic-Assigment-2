# LLM Patch Note Writer

Small CLI app that turns raw bullet point change lists into clean, professional patch notes using a **local Gemma model via Ollama**.

It also uses an external API to fetch the current date and generate a version string, implements simple safety checks, logs telemetry, and comes with an offline evaluation script.

## Stack

- Model: `gemma2:9b` via [Ollama](https://ollama.com/)
- App: Python CLI
- Tool use: `https://worldtimeapi.org` for current time and version tag
- Data: plain text bullets from the user

## Features

- Core user flow:
  - Paste bullet points of changes into the CLI.
  - Optional short description for the release.
  - App calls the local LLM to generate formatted patch notes.
- Enhancement:
  - Tool use: calls `https://worldtimeapi.org` to get current time and derive a version like `v2025.11.27`.
- Safety and robustness:
  - System prompt with explicit do / dont rules (inside `llm_client.py`).
  - Input length guard (`MAX_INPUT_CHARS`, default 4000).
  - Basic prompt injection detection (blocks phrases like "ignore previous instructions").
  - Clear error messages and early exits on failure.
- Telemetry:
  - Logs JSON lines per request to `logs/requests.log` including timestamp, pathway (`tool`), and latency.
  - Token counts are `null` because local models do not expose them.
- Offline eval:
  - `tests.json` with 15 test cases.
  - `eval_runner.py` runs the tests and prints pass rate.
- Repro:
  - `README.md`, `requirements.txt`, `.env.example`, and seed style guide.
  - One-command run for app and eval.

## Prerequisites

1. Install [Ollama](https://ollama.com/).
2. Pull the Gemma model:

   ```bash
   ollama pull gemma2:9b
