import csv
import os

from crewai.tools import tool

from analytics.pattern_extractor import find_correlated_patterns
from analytics.youtube_analytics import fetch_recent_videos

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), 'analytics', 'sample_videos.csv')


def _load_sample_videos():
    """Load the bundled sample dataset for testing without API keys."""
    videos = []
    with open(SAMPLE_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            videos.append((row['title'], int(row['view_count']), row['publish_date']))
    return videos


def _load_real_videos():
    """Try fetching real videos via YouTube Data API (API key, no OAuth)."""
    api_key = os.environ.get('YOUTUBE_API_KEY')
    channel_id = os.environ.get('YOUTUBE_CHANNEL_ID')

    if not api_key or not channel_id:
        return None

    try:
        fetched = fetch_recent_videos(channel_id, api_key=api_key, max_results=20)
        if fetched:
            return [(v['title'], v['view_count'], v['publish_date']) for v in fetched]
    except Exception:
        pass

    return None


@tool("pattern_analysis")
def pattern_analysis_tool() -> str:
    """
    Analyzes title patterns across recent videos to find statistical
    correlations with view count (e.g. titles with numbers perform better,
    question-style titles get more views, best posting day).
    Uses real channel data if YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID are set,
    otherwise falls back to bundled sample data.
    """
    videos = _load_real_videos()
    source = "real channel data"

    if videos is None:
        videos = _load_sample_videos()
        source = "bundled sample dataset (set YOUTUBE_API_KEY + YOUTUBE_CHANNEL_ID for real data)"

    patterns = find_correlated_patterns(videos, top_n=5)

    if not patterns:
        return f"No significant patterns found in {source}."

    lines = [f"Pattern Analysis ({source}):\n"]
    for p in patterns:
        pval = f" (p={p['p_value']:.3f})" if p.get('p_value') is not None else ""
        lines.append(f"- {p['description']}{pval}")

    lines.append(
        "\nUse these patterns to guide title style, hook format, and posting schedule."
    )
    return '\n'.join(lines)
