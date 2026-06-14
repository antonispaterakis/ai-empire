import csv
import os

from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

from analytics.pattern_extractor import find_correlated_patterns
from analytics.youtube_analytics import fetch_recent_videos

load_dotenv()

SAMPLE_VIDEOS_PATH = os.path.join(os.path.dirname(__file__), "analytics", "sample_videos.csv")


def load_sample_videos():
    """Bundled fixture so this script runs out of the box without API keys."""
    videos = []
    with open(SAMPLE_VIDEOS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            videos.append((row["title"], int(row["view_count"]), row["publish_date"]))
    return videos


def get_recent_videos():
    """Use the real YouTube channel if configured, otherwise fall back to the
    bundled sample dataset."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")

    if api_key and channel_id:
        print(f"--- Fetching recent videos for channel {channel_id} via YouTube Data API ---")
        fetched = fetch_recent_videos(channel_id, api_key=api_key, max_results=20)
        if fetched:
            return [(v["title"], v["view_count"], v["publish_date"]) for v in fetched]
        print("--- No videos returned by the API, falling back to bundled sample dataset ---")
    else:
        print("--- YOUTUBE_API_KEY / YOUTUBE_CHANNEL_ID not set, using bundled sample dataset ---")

    return load_sample_videos()


# 1. LLM + search tool (same setup as main.py)
worker_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool_raw = DuckDuckGoSearchRun()


@tool("internet_search")
def search_tool(query: str):
    """Ψάχνει στο internet για τις τελευταίες ειδήσεις σχετικά με την AI."""
    return search_tool_raw.run(query)


# 2. Analytics feedback: find which title patterns correlate with more views
#    on this channel's recent videos (real channel, or bundled sample data).
recent_videos = get_recent_videos()
patterns = find_correlated_patterns(recent_videos)

print("--- Patterns εντοπίστηκαν στα πρόσφατα βίντεο ---")
for p in patterns:
    print(f"  - {p['description']}")

if patterns:
    pattern_lines = "\n".join(f"- {p['description']}" for p in patterns)
    analytics_context = (
        "\n\nΣΗΜΕΙΩΣΗ ΑΠΟ ANALYTICS: Τα πιο επιτυχημένα πρόσφατα βίντεο αυτού του "
        "καναλιού έχουν τα παρακάτω χαρακτηριστικά:\n"
        f"{pattern_lines}\n"
        "Λάβε υπόψη αυτά τα patterns όταν γράφεις τον τίτλο και το hook του σεναρίου."
    )
else:
    analytics_context = ""


# 3. Agents (same roles as main.py)
hunter = Agent(
    role='Trend Researcher',
    goal='Να βρει το πιο viral AI news των τελευταίων 24 ωρών.',
    backstory='Digital scout που χρησιμοποιεί το internet για να βρίσκει breaking news.',
    tools=[search_tool],
    llm=worker_llm,
    verbose=True,
    allow_delegation=False
)

writer = Agent(
    role='YouTube Scriptwriter',
    goal='Να γράφει σενάρια για TikTok/Shorts με δυνατό Hook.',
    backstory='Expert στο storytelling που μετατρέπει ειδήσεις σε viral σενάρια.',
    llm=worker_llm,
    verbose=True,
    allow_delegation=False
)

# 4. Tasks — the writer's task description is extended with the analytics
#    findings from step 2.
task_find = Task(
    description='Ψάξε στο internet και βρες μια αληθινή είδηση AI από τις τελευταίες 24 ώρες.',
    expected_output='Μια περίληψη της είδησης και το link της πηγής.',
    agent=hunter
)

task_write = Task(
    description=(
        'Γράψε ένα σενάριο 60 δευτερολέπτων βασισμένο στην είδηση. '
        'Πρέπει να έχει Hook, Body και Call to Action.'
        + analytics_context
    ),
    expected_output='Το πλήρες σενάριο σε μορφή κειμένου.',
    agent=writer,
    output_file='final_script.txt'
)

# 5. Kickoff
crew = Crew(
    agents=[hunter, writer],
    tasks=[task_find, task_write],
    verbose=True
)

if __name__ == "__main__":
    print("--- Η Αυτοκρατορία ξεκινάει (με Analytics Feedback Loop)... ---")
    crew.kickoff()
