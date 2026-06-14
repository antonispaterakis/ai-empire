"""
YouTube Data API v3 client — fetches recent public video stats for a channel.

This only needs a YouTube Data API v3 key (YOUTUBE_API_KEY env var, no OAuth
required) and reads PUBLIC data via the read-only `search.list` / `videos.list`
endpoints: title, view count, like count, comment count, publish date, duration.

NOTE: This does NOT give you retention, audience-CTR, or impressions — that
data lives behind the YouTube ANALYTICS API, which requires OAuth and is only
accessible to the channel owner. That's the natural next step once this
scaffold proves the feedback loop works end-to-end (see README).
"""

import os

from googleapiclient.discovery import build


def fetch_recent_videos(channel_id, api_key=None, max_results=20):
    """Return a list of dicts with title, view_count, like_count, publish_date,
    duration for the most recent videos uploaded to `channel_id`."""
    api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set")

    youtube = build("youtube", "v3", developerKey=api_key)

    search_response = (
        youtube.search()
        .list(
            channelId=channel_id,
            part="id",
            order="date",
            type="video",
            maxResults=max_results,
        )
        .execute()
    )

    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
    if not video_ids:
        return []

    videos_response = (
        youtube.videos()
        .list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
        .execute()
    )

    videos = []
    for item in videos_response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        videos.append(
            {
                "title": snippet.get("title", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "publish_date": snippet.get("publishedAt", ""),
                "duration": item.get("contentDetails", {}).get("duration", ""),
            }
        )
    return videos
