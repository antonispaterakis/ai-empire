# AI Empire — Progress

## Status: IN PROGRESS

## What's Built

Two-agent CrewAI pipeline:
- **Trend Researcher** — searches the internet (DuckDuckGo) for the latest AI news in the past 24 hours
- **YouTube Scriptwriter** — takes the news and writes a 60-second TikTok/Shorts script (Hook → Body → Call to Action)

Stack: CrewAI, Gemini (worker: `gemini-2.5-flash`, manager: `gemini-3.1-pro-preview`), DuckDuckGo search.

Output: `final_script.txt`

## What's Needed to Finish

- Integrate YouTube Analytics — the pipeline should learn from real performance data (views, retention, CTR) and feed that back into the scriptwriting agent to improve future scripts.
  - **Scaffolded — see `feature/analytics-feedback` branch** (not merged to `main`). What's done there:
    - `analytics/youtube_analytics.py` — fetches recent video titles + public stats (views, likes, publish date, duration) via the YouTube Data API v3 (API key only, no OAuth).
    - `analytics/pattern_extractor.py` — extracts title features (word count, numbers, question marks, posting day) and finds which correlate with higher views (top-half vs bottom-half comparison).
    - `main_with_feedback.py` — new entry point that runs the above and feeds the top patterns into the YouTube Scriptwriter task. Falls back to a bundled sample dataset (`analytics/sample_videos.csv`) if no `YOUTUBE_API_KEY`/`YOUTUBE_CHANNEL_ID` is configured, so it runs out of the box.
  - **Still remaining:**
    - Real retention/CTR/impressions data — requires the YouTube Analytics API (OAuth, channel-owner only).
    - A true closed-loop cycle that re-runs analytics after a video is published and refines future scripts based on real outcomes (not just a one-shot pre-write analysis).
    - Wire the same feedback into `app.py`'s 10-agent factory.
    - Validate the pattern-extraction findings against a larger/real channel dataset (the bundled sample is illustrative, not statistically robust).
- [x] ~~The API key is hardcoded in `main.py` — move to `.env` before any further development.~~ Done: both `main.py` and `app.py` now load `GOOGLE_API_KEY` from `.env` via `python-dotenv`.

## Notes

Originally conceived as a faceless YouTube automation system. Current version is a clean 2-agent proof of concept. YouTube Analytics feedback loop is the key feature that makes it a real product.
