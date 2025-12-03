                   ┌────────────────────────┐
                   │        User CLI        │
                   │  (python app.py run)   │
                   └────────────┬───────────┘
                                │  bullet points
                                ▼
                   ┌────────────────────────┐
                   │     Safety Layer       │
                   │  - length check        │
                   │  - prompt-injection    │
                   └────────────┬───────────┘
                                │  sanitized input
                                ▼
                   ┌────────────────────────┐
                   │    Tool Integration    │
                   │ fetch_release_metadata │
                   │ (World Time API)       │
                   └────────────┬───────────┘
                                │  release_date
                                ▼
                   ┌────────────────────────┐
                   │     Prompt Builder     │
                   │ - system prompt rules  │
                   │ - style guide injected │
                   │ - metadata included    │
                   └────────────┬───────────┘
                                │ full prompt
                                ▼
                   ┌────────────────────────┐
                   │       LLM Engine       │
                   │ Ollama (gemma2:9b)     │
                   └────────────┬───────────┘
                                │ patch notes
                                ▼
                   ┌────────────────────────┐
                   │       Telemetry        │
                   │ - timestamp            │
                   │ - pathway="tool"       │
                   │ - latency + tokens     │
                   └────────────────────────┘
# Guardrails (Safety & Robustness)

## 1. System Prompt Safety Rules
Enforced in `llm_client.py`:

- Must **not** invent features not in the bullets.
- Must follow strict structure:
  - Gameplay changes
  - Balances
  - Bug fixes
- Must not create extra sections or filler.
- Must write concise, professional notes.
- Must use the provided style guide.

---

## 2. Input Length Guard
Defined in `saftey.py`:

- Rejects input over `MAX_INPUT_CHARS`.
- Shows a clean error message:

  "Error: Input is too long. Please split your changes..."

---

## 3. Prompt-Injection Guard
Also in `saftey.py`:

Detects common injection patterns such as:
- "ignore previous instructions"
- "disregard the system prompt"
- "you are now free"

If detected:
- Request is rejected.
- User receives a clear refusal message.

---

## 4. External API Failure Handling

Handled by `fetch_release_metadata()`:

- Tries the World Time API.
- If the request fails:
  - Falls back to local UTC time.
- Guarantees the app never crashes due to network errors.

---

# Tool Integration (Enhancement Choice)

This app uses **Tool Use** as the enhancement requirement.

**Tool:** World Time API  
**Endpoint:** `https://worldtimeapi.org/api/timezone/America/Toronto`

### Purpose
- Fetches the release date.
- Injected into the metadata section of the LLM prompt.
- Ensures patch notes always include real contextual data.

### Requirement Satisfied
"Call one external API and use its output inside the LLM generation pipeline."

---

# Offline Evaluation Method

The project includes the following:

## 1. `tests.json`
- Contains 15 test cases.
- Each test includes:
  - `input_bullets`
  - `expected_patterns`

## 2. `eval_runner.py`
Script performs automated evaluation:

- Iterates over each test case.
- Calls `generate_patch_notes(...)`.
- Checks whether expected patterns appear in the output.
- Tracks:
  - PASS/FAIL per test
  - Latency per test
- Prints a final pass rate, for example:


### Requirement Satisfied
"Offline eval: tests.json + script that prints a pass rate."

---

# Telemetry (Cost & Latency Awareness)

Logged via `telemetry.log_request()`:

- `timestamp`
- `pathway="tool"`
- `token_stats`, including:
  - `latency_s`
  - `prompt_tokens` (None for local models)
  - `completion_tokens` (None for local)
- Log entries saved in `logs/requests.log` as JSON lines.

---

# Known Limits

### 1. No guaranteed determinism
Local LLM (Gemma 2.9B via Ollama) may produce slightly different output per run.

### 2. Limited token accounting
Ollama does not expose token usage, so token fields remain `None`.

### 3. Single external API
Only one tool is used (time metadata). No multi-tool chaining.

### 4. No RAG or long-term memory
Patch notes are generated solely from:
- user bullet points
- style guide
- system prompt

No document retrieval or vector store.

### 5. Internet required for real metadata
If offline, the app falls back to UTC, but no real-time date is obtained.

### 6. No streaming output
LLM output is returned as a single completed string (non-streaming).

