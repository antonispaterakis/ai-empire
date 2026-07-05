import json
import os
import logging
import tweepy
from crewai.tools import tool

@tool("x_research_tool")
def x_research_tool(query: str) -> str:
    """Ψάχνει το X (Twitter) για viral tweets και βγάζει report στρατηγικής.
    Χρησιμοποιήστε αυτό το εργαλείο για να αναλύσετε τον ανταγωνισμό."""
    
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    
    mock_report = {
        "trending_topics": [f"{query} insights", "AI Automation", "Microservices"],
        "viral_hooks": [
            f"Why 99% of {query} projects fail (and how to be the 1%):",
            f"I spent 100 hours researching {query}. Here's what I found:",
            "Stop doing X. Do Y instead. A thread 🧵"
        ],
        "engagement_advice": "Κράτα τις προτάσεις μικρές. Χρησιμοποίησε λίγα emojis. Ξεκίνα με μια έντονη δήλωση."
    }

    if not bearer_token:
        logging.warning("X_BEARER_TOKEN not found in environment. Falling back to mock x_research_tool.")
        return json.dumps(mock_report, indent=2, ensure_ascii=False)
        
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Search for recent tweets, filter out retweets
        search_query = f"{query} -is:retweet lang:en"
        response = client.search_recent_tweets(
            query=search_query,
            tweet_fields=["public_metrics", "text"],
            max_results=50
        )
        
        if not response.data:
            logging.warning(f"No tweets found for query '{query}'. Falling back to mock data.")
            return json.dumps(mock_report, indent=2, ensure_ascii=False)
            
        tweets = response.data
        
        # Sort tweets by engagement (likes + retweets + replies)
        def engagement_score(t):
            metrics = t.public_metrics
            return metrics["like_count"] + metrics["retweet_count"] + metrics["reply_count"]
            
        tweets.sort(key=engagement_score, reverse=True)
        top_tweets = tweets[:10]
        
        viral_hooks = []
        for t in top_tweets:
            # Extract first line or sentence as a hook
            first_line = t.text.split('\n')[0].strip()
            if len(first_line) > 5:
                viral_hooks.append(first_line)
                
        # Fill in with mock data if we didn't find enough hooks
        if not viral_hooks:
            viral_hooks = mock_report["viral_hooks"]
            
        report = {
            "trending_topics": [f"{query} trends"] + [f.split()[0] for f in viral_hooks[:2]],
            "viral_hooks": viral_hooks[:5],
            "engagement_advice": "Focus on strong hooks that have generated high engagement in these examples."
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logging.warning(f"Failed to fetch from X API: {e}. Falling back to mock x_research_tool.")
        return json.dumps(mock_report, indent=2, ensure_ascii=False)
