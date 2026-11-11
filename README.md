# NLPApp

A small Tkinter desktop application for sentiment analysis, named entity
recognition, and emotion detection using OpenRouter.

## Setup

1. Install Python 3.10 or newer.
2. From the `PythonProject` directory, install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Configure your OpenRouter API key as the `OPENROUTER_API_KEY` environment
   variable. Do not commit the key or place it directly in source code.

   PowerShell:

   ```powershell
   $env:OPENROUTER_API_KEY = "your_key"
   python app.py
   ```

   macOS/Linux:

   ```bash
   export OPENROUTER_API_KEY="your_key"
   python app.py
   ```

4. Run the application:

   ```bash
   python app.py
   ```

## Local account data

Account data is stored under `~/.nlpapp/db.json` by default (or in the directory
specified by `NLPAPP_DATA_DIR`). Passwords are stored as salted PBKDF2-HMAC-SHA256
hashes, not plaintext. The previous `PythonProject/db.json` format is migrated
to the new location on first launch if it exists.

The repository's `PythonProject/db.json` is intentionally an empty template.
Do not commit real user records. Since the old sample credentials were publicly
committed, do not reuse them; rotate any real password that may have appeared
in repository history.

## Notes

- The API request has a 30-second timeout and displays readable errors for
  authentication, billing (HTTP 402), rate limiting (HTTP 429), network, and
  provider failures.
- NLP requests run in a background thread so the Tkinter window stays
  responsive.
- The application can be imported without opening a GUI; launch behavior is
  protected by the `__main__` guard.
