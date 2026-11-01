# Custom Log Validator

A small Streamlit app that checks whether a list of test methods appears in a blob of log
output. Paste the logs on the left, the test method names on the right, hit **Validate**,
and each method is reported as **FOUND** (green) or **NOT FOUND** (red).

## Features

- Two inputs: a large logs text area and a test-methods list.
- `Validate` button in the top-right corner.
- Colour-coded results with hit counts and the log line numbers where each method matched.
- Test names can be separated by newlines, commas or semicolons; duplicates are ignored.
- Optional **case sensitive** and **match whole method name only** modes.
- "Show only missing" toggle and a CSV report download.

## Requirements

- Python 3.9 or newer
- The packages in `requirements.txt` (just `streamlit`)

## Run it

### macOS / Linux

```bash
./run.sh
```

The script creates a `.venv`, installs dependencies and starts the app. If the file is not
executable yet:

```bash
chmod +x run.sh && ./run.sh
```

### Windows

```bat
run.bat
```

### Manual (any OS)

```bash
python3 -m venv .venv            # Windows: py -3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>. Use `streamlit run app.py --server.port 8600` to
pick a different port.

## Usage

1. Paste the log content into **Logs content**.
2. List the test methods in **Test methods**, e.g.

   ```
   testLoginSuccess
   testLogoutRedirect
   testCheckoutFlow
   ```

3. Click **Validate**.
4. Read the results below the inputs: a summary row (total / found / not found) followed by
   one coloured row per method. Download the CSV report if you need to share it.

Matching is a substring search per log line by default, so `testLoginSuccess` also matches
`com.example.suite.testLoginSuccess PASSED`. Enable **match whole method name only** to
require an exact method-name boundary (this makes `testCheckoutFlow` stop matching
`testCheckoutFlowExtra`).

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit UI: inputs, Validate button, result rendering. |
| `validator.py` | Matching logic (`parse_test_names`, `validate`, `summarize`) — no UI code. |
| `requirements.txt` | Python dependencies. |
| `run.sh` / `run.bat` | One-command launchers for macOS/Linux and Windows. |

New checks usually mean adding a rule and a field in `validator.py`; the UI picks up the
extra information with a one-line change in `app.py`.
