# AI Empire

A multi-agent content pipeline built with [CrewAI](https://github.com/crewAIInc/crewAI) that researches trending AI news and turns it into ready-to-publish short-form video scripts (TikTok / YouTube Shorts), powered by Google Gemini.

> **Status:** in progress — proof of concept works; analytics feedback loop not yet built.

## What it does

Two entry points, two pipeline sizes:

- **`main.py`** — a lean 2-agent crew:
  - **Trend Researcher** searches the web (DuckDuckGo) for the most viral AI news from the last 24 hours
  - **YouTube Scriptwriter** turns that news into a 60-second script (Hook → Body → Call to Action)
  - Output is written to `final_script.txt`

- **`app.py`** — a Streamlit UI fronting a 10-agent "content factory" crew (Trend Hunter, Scriptwriter, Title Master, Visual Director, Video Editor, Thumbnail Designer, SEO Expert, Social Media Manager, Voiceover Coach, General Manager) that produces a full content package — script, titles, image prompts, edit notes, thumbnail brief, SEO description/hashtags, captions, and voiceover direction — for any topic you give it.

## Stack

- [CrewAI](https://github.com/crewAIInc/crewAI) for agent orchestration
- Google Gemini via `langchain-google-genai` (`gemini-2.5-flash` for workers, `gemini-3.1-pro-preview` as manager)
- DuckDuckGo search tool for live web research
- [Streamlit](https://streamlit.io/) for the multi-agent UI (`app.py`)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install crewai langchain-google-genai langchain-community streamlit
```

Set your Gemini API key as an environment variable (don't hardcode it):

```bash
export GOOGLE_API_KEY="your-key-here"
```

Run the lean pipeline:

```bash
python main.py
```

Or launch the full content-factory UI:

```bash
streamlit run app.py
```

## Roadmap

- [ ] Move the API key out of source and into environment variables / `.env`
- [ ] Hook up YouTube Analytics so the pipeline learns from real performance (views, retention, CTR) and feeds that back into the scriptwriting agent — this is the feature that turns the proof of concept into a real product

See `progress.md` for the full status notes.
