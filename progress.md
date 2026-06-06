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
- The API key is hardcoded in `main.py` — move to `.env` before any further development.

## Notes

Originally conceived as a faceless YouTube automation system. Current version is a clean 2-agent proof of concept. YouTube Analytics feedback loop is the key feature that makes it a real product.
