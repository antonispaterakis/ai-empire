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
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Gemini API key (both `main.py` and `app.py` load it via `python-dotenv`):

```bash
cp .env.example .env
# then edit .env and set GOOGLE_API_KEY=your-key-here
```

Run the lean pipeline:

```bash
python main.py
```

Or launch the full content-factory UI:

```bash
streamlit run app.py
```

## Example Output

> The pipeline hasn't been run yet in this environment (no `GOOGLE_API_KEY` configured), so this is an **illustrative example** showing the expected `final_script.txt` structure from `main.py` — Hook → Body → Call to Action:

```
🎬 AI News Script (60 seconds)

[HOOK]
Google just dropped a Gemini update that's quietly changing how AI agents work — and almost nobody noticed.

[BODY]
The new model adds native multi-agent orchestration support, meaning teams of AI agents can now hand off tasks to each other without custom glue code. Early developers are already reporting builds that used to take a week now coming together in an afternoon. This isn't just a speed bump — it's a shift in how AI products get built.

[CALL TO ACTION]
Want to see this in action? Follow for the next video where we build a real multi-agent crew live. 🚀
```

## Analytics Feedback Loop (experimental)

> Lives on the `feature/analytics-feedback` branch. A first-pass scaffold of
> the feedback loop described in the roadmap below — not yet merged to `main`.

`main_with_feedback.py` is a third entry point that runs the same 2-agent crew
as `main.py`, but first analyzes the channel's recent videos and feeds the
findings into the **YouTube Scriptwriter** task:

1. **`analytics/youtube_analytics.py`** — calls the **YouTube Data API v3**
   (`search.list` / `videos.list`, read-only, just an API key — no OAuth) to
   pull a channel's recent videos: title, view count, like count, publish
   date, duration.
2. **`analytics/pattern_extractor.py`** — takes `(title, view_count,
   publish_date)` tuples, computes simple per-title features (word count,
   presence of a number, presence of a question mark, day of week posted),
   and compares the top half vs bottom half of videos by views to find which
   features correlate with higher view counts (using `scipy` for a p-value if
   installed, otherwise a plain proportion/mean comparison).
3. **`main_with_feedback.py`** — runs the above and injects the top
   correlated patterns into the scriptwriter's task description, e.g.
   *"Top-performing titles use numbers more often (62% vs 0%) — consider this
   pattern when writing the title/hook."*

```bash
python main_with_feedback.py
```

### What's implemented

- Fetching real public stats for any channel via the Data API (no OAuth).
- Feature extraction + top-half/bottom-half correlation analysis.
- A bundled sample dataset (`analytics/sample_videos.csv`) so the script runs
  **out of the box with no extra API keys** — without `YOUTUBE_API_KEY` /
  `YOUTUBE_CHANNEL_ID` it falls back to the sample data and still
  demonstrates the full loop end-to-end.

### What you need to provide for it to run on a real channel

Set these in `.env` (see `.env.example`):

- `GOOGLE_API_KEY` — Gemini key (same as `main.py`).
- `YOUTUBE_API_KEY` — a YouTube Data API v3 key (enable the API in Google
  Cloud Console and create an API key — read-only, no OAuth needed).
- `YOUTUBE_CHANNEL_ID` — the `UC...` channel ID to analyze.

### What's still missing for the full vision

- **Real retention/CTR/impressions** — the Data API only exposes public
  vanity metrics (views, likes). True audience retention and click-through
  rate live behind the **YouTube Analytics API**, which requires OAuth and is
  restricted to the channel owner. That's the natural next step.
- **A true closed-loop feedback cycle** — right now this runs once, before
  writing a script. The full vision re-runs analytics *after* a video is
  published, to validate whether the suggested patterns actually moved the
  needle, and refines the prompt over time based on real outcomes.
- Only the lean pipeline (`main_with_feedback.py`) uses this so far; `app.py`'s
  10-agent factory doesn't yet.

## Roadmap

- [x] ~~Move the API key out of source and into environment variables / `.env`~~ — done, see `.env.example`
- [ ] Hook up YouTube Analytics so the pipeline learns from real performance (views, retention, CTR) and feeds that back into the scriptwriting agent — this is the feature that turns the proof of concept into a real product (**scaffolded** on `feature/analytics-feedback`, see "Analytics Feedback Loop" above)

See `progress.md` for the full status notes.
