# AI Empire

> An AI-powered content factory that watches your YouTube Analytics, learns what goes viral, and generates optimized short-form video packages automatically.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/built%20with-CrewAI-orange)](https://github.com/crewAIInc/crewAI)


---

## The Idea

Most AI content tools generate scripts in a vacuum. They have no idea what actually performs well on *your* channel.

**AI Empire is different.** It plugs into your YouTube Analytics, studies what works (high CTR, strong retention, viral hooks) and what doesn't, and uses that data to guide an 11-agent production crew. Every video it creates is informed by real performance data. The more you use it, the smarter it gets.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                            │
│                                                             │
│  YouTube Analytics API ──► analytics_cache.json (24h TTL)   │
│  Past Generated Scripts ──► production_history.json         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTELLIGENCE LAYER                        │
│                                                             │
│  Performance Strategist reads both data sources and         │
│  outputs a "Viral Strategy Brief":                          │
│    • What topics are trending on YOUR channel               │
│    • What hook styles drive retention                       │
│    • What to avoid based on past underperformers            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION LAYER                         │
│                                                             │
│  10 specialized agents follow the brief:                    │
│  Trend Hunter → Scriptwriter → Title Master →               │
│  Visual Director → Video Editor → Thumbnail Designer →      │
│  SEO Expert → Social Media Manager → Voiceover Coach →      │
│  General Manager (assembles the final package)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PUBLISH ON  │
                    │   YOUTUBE    │──► Link video ID back
                    └──────────────┘    to close the loop
```

## Quick Start

```bash
git clone https://github.com/antonispaterakis/ai-empire.git
cd ai-empire
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your-key
```

**Run the lean 3-agent pipeline:**
```bash
python3 main.py
```

**Run the full 11-agent Streamlit UI:**
```bash
streamlit run app.py
```

## YouTube Analytics Setup (Optional)

The Strategist agent works out of the box with generic best practices, but it becomes powerful when connected to your real channel data.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **YouTube Data API v3** + **YouTube Analytics API**
3. Create an **OAuth 2.0 Client ID** (Desktop app) under Credentials
4. Download the JSON and save it as `client_secret.json` in the project root

On first run, a browser window opens for authentication. After that, `token.json` is saved locally and you won't need to log in again.

> **No credentials yet?** The system falls back gracefully to generic YouTube Shorts best practices. No crashes, no errors.

## Closing the Feedback Loop

After you publish a video that the pipeline generated:

**Streamlit sidebar:** Select the run and enter the YouTube video ID.

**CLI:**
```bash
python3 -c "from history_tool import link_video; link_video('RUN_ID', 'VIDEO_ID')"
```

Next time the pipeline runs, the Strategist cross-references the linked video's real performance with the hook and strategy it originally suggested, enabling it to learn what actually works.

## Agent Configuration

All 11 agents are defined in [`agents.yaml`](agents.yaml). You can tweak any agent's personality, goal, or instructions by editing this file. No Python changes needed.

## Project Structure

```
ai-empire/
├── agents.yaml               # 11 agent definitions (role, goal, backstory)
├── agent_loader.py            # YAML config parser
├── app.py                     # 11-agent Streamlit UI
├── main.py                    # 3-agent lean pipeline
├── youtube_analytics_tool.py  # YouTube API + 24h cache + fallback
├── history_tool.py            # Production history (save/link/read)
├── requirements.txt
├── .env.example
└── data/
    └── production_history.json  # Content memory (grows over time)
```

## Stack

| Component | Technology |
|-----------|-----------|
| Agent orchestration | [CrewAI](https://github.com/crewAIInc/crewAI) |
| LLM | Via `langchain-google-genai` (configurable in `main.py` / `app.py`) |
| Web research | DuckDuckGo Search |
| Analytics | YouTube Data API v3 + YouTube Analytics API |
| UI | [Streamlit](https://streamlit.io/) |

## Roadmap

- [x] Multi-agent content generation pipeline
- [x] Streamlit UI with 11-agent content factory
- [x] YouTube Analytics integration with Performance Strategist
- [x] Production history with feedback loop (video linking)
- [x] 24-hour analytics cache to prevent API quota drain
- [x] Agent configs externalized to YAML
- [ ] Auto-detect published videos (remove manual linking)
- [ ] Streamlit dashboard showing performance trends over time
- [ ] A/B test hook styles across multiple runs

See [`progress.md`](progress.md) for detailed development notes.

## License

This project is open source. Clone it, fill in your API keys, and make it your own.
