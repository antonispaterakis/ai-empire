import re
import os
from celery_app import celery_app
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.tools import tool

from agent_loader import get_agent_config
from history_tool import history_tool, save_run
from x_research_tool import x_research_tool
import urllib.request
import json
from crewai.tools import tool

load_dotenv()

@tool("internet_search")
def search_tool(query: str):
    """Ψάχνει στο internet για τις τελευταίες ειδήσεις (fallback to mock)."""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=1&namespace=0&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        data = json.loads(response)
        if len(data) >= 3 and len(data[2]) > 0:
            return data[2][0]
        return f"Breaking news about {query}: Significant trends are shaping the future!"
    except Exception:
        return f"Breaking news about {query}: Significant trends are shaping the future!"


@celery_app.task
def generate_content(topic: str = "AI News", auto_post: bool = False):
    """
    Run the CrewAI pipeline to generate an X thread and optionally post it.
    """
    manager_llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
    worker_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    researcher_cfg = get_agent_config('market_researcher')
    hunter_cfg = get_agent_config('trend_hunter', topic=topic)
    writer_cfg = get_agent_config('thread_writer')

    researcher = Agent(
        role=researcher_cfg['role'],
        goal=researcher_cfg['goal'],
        backstory=researcher_cfg['backstory'],
        tools=[x_research_tool, history_tool],
        llm=manager_llm,
        verbose=True,
        allow_delegation=False,
    )

    hunter = Agent(
        role=hunter_cfg['role'],
        goal=hunter_cfg['goal'],
        backstory=hunter_cfg['backstory'],
        tools=[search_tool],
        llm=worker_llm,
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role=writer_cfg['role'],
        goal=writer_cfg['goal'],
        backstory=writer_cfg['backstory'],
        llm=worker_llm,
        verbose=True,
        allow_delegation=False,
    )

    t_research = Task(
        description=(
            f'Ανέλυσε τα trends για το θέμα: {topic} με το x_research_tool '
            'και δες τι έχει παίξει στο παρελθόν με το production_history.'
        ),
        expected_output='Viral Hook Strategy Brief (5-10 γραμμές).',
        agent=researcher,
    )

    t_hunt = Task(
        description=f'Βρες είδηση για {topic} με βάση το Strategy Brief.',
        expected_output='Περίληψη είδησης, πηγή, και γιατί ταιριάζει.',
        agent=hunter,
        context=[t_research],
    )

    t_write = Task(
        description=(
            'Γράψε X Thread 3-5 tweets. Κάθε tweet πρέπει να είναι έτοιμο '
            'για δημοσίευση.'
        ),
        expected_output='Ολόκληρο το κείμενο του X Thread.',
        agent=writer,
        context=[t_research, t_hunt],
    )

    crew = Crew(
        agents=[researcher, hunter, writer],
        tasks=[t_research, t_hunt, t_write],
        verbose=True,
    )

    result = crew.kickoff()
    raw_output = result.raw if hasattr(result, 'raw') else str(result)

    # Simple extraction of the hook (first tweet)
    lines = raw_output.split('\n')
    hook = lines[0] if lines else "N/A"
    strategy_output = t_research.output.raw if t_research.output else "N/A"

    run_id = save_run(
        topic=topic,
        strategy_brief=strategy_output[:500],
        hook=hook,
        thread_summary=raw_output[:500]
    )

    # Handle auto-posting (Mocked for now)
    post_status = "Saved for manual review."
    if auto_post:
        # In the future: call tweepy API here
        # api.create_tweet(text=...)
        post_status = "Auto-posted (Mock)!"
        from history_tool import link_tweet
        link_tweet(run_id, "mock_tweet_123")

    return {
        "run_id": run_id,
        "topic": topic,
        "content": raw_output,
        "status": post_status
    }
