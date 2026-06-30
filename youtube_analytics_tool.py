import os
import json
import datetime

from crewai.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.readonly',
]

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CACHE_PATH = os.path.join(DATA_DIR, 'analytics_cache.json')
CACHE_TTL_HOURS = 24


def _cache_is_fresh() -> bool:
    """Return True if the cache exists and is younger than CACHE_TTL_HOURS."""
    if not os.path.exists(CACHE_PATH):
        return False
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        fetched_at = datetime.datetime.fromisoformat(cache['fetched_at'])
        age = datetime.datetime.now(datetime.timezone.utc) - fetched_at
        return age.total_seconds() < CACHE_TTL_HOURS * 3600
    except (json.JSONDecodeError, KeyError, ValueError):
        return False


def _read_cache() -> str:
    """Read the cached analytics and format them for the Strategist."""
    with open(CACHE_PATH, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    lines = [f"YouTube Analytics (cached, fetched {cache['fetched_at']}):\n"]
    for v in cache.get('videos', []):
        lines.append(
            f"- \"{v['title']}\" | Views: {v['views']} | "
            f"CTR: {v.get('ctr_percent', 'N/A')}% | "
            f"Avg Duration: {v.get('avg_view_duration_sec', 'N/A')}s | "
            f"Retention: {v.get('avg_view_percentage', 'N/A')}%"
        )
    return '\n'.join(lines)


def _authenticate():
    """Handle OAuth 2.0 flow. Returns (youtube_service, analytics_service) or None."""
    project_root = os.path.dirname(__file__)
    client_secret = os.path.join(project_root, 'client_secret.json')
    token_path = os.path.join(project_root, 'token.json')

    if not os.path.exists(client_secret):
        return None

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    youtube = build('youtube', 'v3', credentials=creds)
    analytics = build('youtubeAnalytics', 'v2', credentials=creds)
    return youtube, analytics


def _fetch_and_cache() -> str:
    """Fetch fresh data from YouTube APIs, cache it, and return formatted string."""
    auth = _authenticate()
    if auth is None:
        return None

    youtube, analytics = auth

    # Get channel ID
    channels = youtube.channels().list(mine=True, part='id,snippet').execute()
    if not channels.get('items'):
        return "No YouTube channel found for this account."
    channel_id = channels['items'][0]['id']

    # Calculate date range (last 28 days)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=28)

    # Fetch analytics
    report = analytics.reports().query(
        ids=f'channel=={channel_id}',
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        metrics='views,estimatedMinutesWatched,averageViewDuration,likes,comments',
        dimensions='video',
        maxResults=10,
        sort='-views',
    ).execute()

    rows = report.get('rows', [])
    if not rows:
        return "No analytics data found for the last 28 days."

    # Get video titles and publish dates
    video_ids = [row[0] for row in rows]
    videos_resp = youtube.videos().list(
        id=','.join(video_ids),
        part='snippet,statistics',
    ).execute()

    video_meta = {}
    for item in videos_resp.get('items', []):
        vid = item['id']
        video_meta[vid] = {
            'title': item['snippet']['title'],
            'published_at': item['snippet']['publishedAt'],
        }

    # Build cache object
    cache = {
        'fetched_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'channel_id': channel_id,
        'period': 'last_28_days',
        'videos': [],
    }

    for row in rows:
        vid_id = row[0]
        meta = video_meta.get(vid_id, {})
        cache['videos'].append({
            'video_id': vid_id,
            'title': meta.get('title', 'Unknown'),
            'published_at': meta.get('published_at', ''),
            'views': row[1],
            'estimated_minutes_watched': row[2],
            'avg_view_duration_sec': row[3],
            'likes': row[4],
            'comments': row[5],
        })

    # Write cache
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

    return _read_cache()


@tool("youtube_analytics")
def youtube_analytics_tool() -> str:
    """
    Fetches YouTube Analytics data for the channel.
    Returns a report of the top-performing videos from the last 28 days
    including views, CTR, and average view duration.
    Uses a 24-hour local cache to avoid unnecessary API calls.
    Falls back gracefully if no credentials are configured.
    """
    # 1. Try the cache first
    if _cache_is_fresh():
        return _read_cache()

    # 2. Try fetching fresh data
    result = _fetch_and_cache()
    if result is not None:
        return result

    # 3. Graceful fallback: no client_secret.json present
    return (
        "NOTICE: No YouTube API credentials found (client_secret.json is missing). "
        "Unable to fetch real analytics data.\n\n"
        "Since this is the first run or the credentials haven't been set up yet, "
        "produce a generic Viral Strategy Brief based on YouTube Shorts best practices:\n"
        "- Use question-style or controversy hooks in the first 2 seconds.\n"
        "- Keep scripts under 60 seconds for maximum retention.\n"
        "- Topics about 'AI tools replacing jobs' and 'new releases' tend to perform well.\n"
        "- Avoid generic roundup-style content (e.g. '5 AI news this week').\n"
        "- Push for a strong CTA at the end (subscribe, comment, follow)."
    )
