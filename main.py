import re
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

from agent_loader import get_agent_config
from youtube_analytics_tool import youtube_analytics_tool
from history_tool import history_tool, save_run

load_dotenv()

# --- Models ---
manager_llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
worker_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- Search Tool ---
search_tool_raw = DuckDuckGoSearchRun()

@tool("internet_search")
def search_tool(query: str):
    """Ψάχνει στο internet για τις τελευταίες ειδήσεις."""
    return search_tool_raw.run(query)

# --- Agents (loaded from agents.yaml) ---
strategist_cfg = get_agent_config('performance_strategist')
hunter_cfg = get_agent_config('trend_hunter', topic="AI News")
writer_cfg = get_agent_config('scriptwriter')

strategist = Agent(
    role=strategist_cfg['role'],
    goal=strategist_cfg['goal'],
    backstory=strategist_cfg['backstory'],
    tools=[youtube_analytics_tool, history_tool],
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

# --- Tasks ---
task_strategy = Task(
    description=(
        'Χρησιμοποίησε το youtube_analytics tool για να δεις τα τελευταία στατιστικά. '
        'Μετά χρησιμοποίησε το production_history tool για να δεις τι σενάρια και hooks '
        'έχει γράψει η ομάδα στο παρελθόν. '
        'Βγάλε ένα Viral Strategy Brief: τι θέμα να ψάξουμε, τι στυλ hook να γράψουμε, '
        'και τι να αποφύγουμε.'
    ),
    expected_output=(
        'Ένα σύντομο Viral Strategy Brief (5-10 γραμμές) που δίνει ξεκάθαρες '
        'οδηγίες στον Trend Hunter και τον Scriptwriter.'
    ),
    agent=strategist,
)

task_find = Task(
    description=(
        'Διάβασε τη στρατηγική του Strategist. '
        'Ψάξε στο internet και βρες μια αληθινή είδηση AI από τις τελευταίες 24 ώρες '
        'που να ταιριάζει με τη στρατηγική.'
    ),
    expected_output='Μια περίληψη της είδησης, το link της πηγής, και γιατί ταιριάζει στη στρατηγική.',
    agent=hunter,
    context=[task_strategy],
)

task_write = Task(
    description=(
        'Διάβασε τη στρατηγική και την είδηση. '
        'Γράψε ένα σενάριο 60 δευτερολέπτων. '
        'Δομή: [HOOK] - [BODY] - [CALL TO ACTION]. '
        'Το Hook πρέπει να ακολουθεί ακριβώς το στυλ που λέει η στρατηγική.'
    ),
    expected_output='Το πλήρες σενάριο σε μορφή κειμένου.',
    agent=writer,
    context=[task_strategy, task_find],
    output_file='final_script.txt',
)

# --- Crew ---
crew = Crew(
    agents=[strategist, hunter, writer],
    tasks=[task_strategy, task_find, task_write],
    verbose=True,
)

print("--- Η Αυτοκρατορία ξεκινάει (with Analytics Feedback Loop)... ---")
result = crew.kickoff()

# --- Save to Production History ---
raw_output = result.raw if hasattr(result, 'raw') else str(result)

# Try to extract the hook from the script
hook_match = re.search(r'\[HOOK\]\s*\n?(.*?)(?:\n\n|\[BODY\])', raw_output, re.DOTALL)
hook = hook_match.group(1).strip() if hook_match else raw_output[:100]

# Extract the strategy brief from the strategist's output
strategy_output = task_strategy.output.raw if task_strategy.output else "N/A"

run_id = save_run(
    topic="AI News",
    strategy_brief=strategy_output[:500],
    hook=hook,
    script_summary=raw_output[:300],
    titles=[],
)

print(f"\n--- Script saved. Run ID: {run_id} ---")
print("--- After publishing, link the video with: ---")
print(f"---   python3 -c \"from history_tool import link_video; link_video('{run_id}', 'YOUR_VIDEO_ID')\" ---")