# AI Empire - Development Progress

## Status: v2 COMPLETE

## Architecture

Three-layer system: **Data** (YouTube Analytics + production history) → **Intelligence** (Performance Strategist) → **Production** (10 specialized agents).

## Changelog

### v2 - Analytics Feedback Loop (June 2026)

**New files:**
- `youtube_analytics_tool.py` - YouTube API integration with OAuth 2.0 and 24-hour local cache. Falls back to generic best practices if no `client_secret.json` is present.
- `history_tool.py` - Saves every generated content package (topic, hook, strategy, script) to `data/production_history.json`. Supports linking runs to published YouTube video IDs to close the feedback loop.
- `agents.yaml` - All 11 agent definitions (role, goal, backstory) in a single YAML file. Replaces hardcoded agent configs.
- `agent_loader.py` - Parses `agents.yaml` and supports `{topic}` placeholder formatting.
- `data/production_history.json` - Ships empty, grows with each pipeline run.

**Modified files:**
- `main.py` - Refactored to 3-agent pipeline (Strategist → Trend Hunter → Scriptwriter). Loads configs from YAML. Saves output to production history.
- `app.py` - Refactored to 11-agent pipeline. Added sidebar UI for linking published videos to past runs.
- `requirements.txt` - Added `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `pyyaml`.
- `.gitignore` - Added `client_secret.json`, `token.json`, `data/analytics_cache.json`.
- `README.md` - Complete rewrite with architecture diagram and updated documentation.

### v1 - Proof of Concept

- Two-agent CrewAI pipeline: Trend Researcher + YouTube Scriptwriter.
- 10-agent Streamlit UI (content factory) in `app.py`.
- Stack: CrewAI, LangChain, DuckDuckGo search.
- [x] ~~API key hardcoded in source~~ - moved to `.env` via `python-dotenv`.

## What's Next

- Auto-detect published videos (remove need for manual linking).
- Streamlit dashboard page showing performance trends over time.
- A/B testing: generate multiple hook variants and track which style performs best.

## Design Decisions

- **YAML over Markdown for agent configs**: Markdown parsing breaks when agent prompts contain `#` characters. YAML is strict and safe.
- **24-hour analytics cache**: YouTube Analytics data updates roughly every 24-48 hours. Hitting the API on every pipeline run wastes quota and adds latency for identical data.
- **Local-only OAuth**: The `InstalledAppFlow` opens a browser window. This will not work on headless servers or cloud deployments. Acceptable for the current scope (personal content tool).
- **Graceful fallback**: If `client_secret.json` is missing, the Strategist produces a generic brief based on best practices instead of crashing. This means anyone can clone the repo and run it immediately.
