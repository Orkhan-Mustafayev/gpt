# Tweet Delete Tracker Bot

A Python 3.11 bot that watches selected X (Twitter) accounts and announces when they delete tweets. The bot fetches timelines, stores snapshots locally, detects deletions, and posts a short announcement from your authenticated bot account.

## Prerequisites
- Python 3.11
- An X API key/secret and access token/secret with permissions to read timelines and post tweets
- Depending on your tier, frequent timeline polling may require elevated or paid access

## Setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Export environment variables (consider using a `.env` file with `python-dotenv`):
   ```bash
   export X_API_KEY="your_api_key"
   export X_API_SECRET="your_api_secret"
   export X_ACCESS_TOKEN="your_access_token"
   export X_ACCESS_SECRET="your_access_secret"
   export X_BEARER_TOKEN="your_bearer_token"  # optional for v2 endpoints
   export TRACKED_HANDLES="some_user,another_user"
   export POLL_INTERVAL_SECONDS="120"
   ```

## Running the bot
Run from the project root:
```bash
python main.py
```

The bot will start polling the configured handles and announce deletions from your authenticated account. Stored state is written to `data/state.json`.

## Notes
- Timeline polling relies on X API capabilities; ensure your access tier supports the required endpoints or swap in a third-party provider inside `core/twitter_client.py`.
- The default poll interval is 120 seconds. Increase the interval to stay within rate limits.
