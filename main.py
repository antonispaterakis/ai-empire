

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# 2. ΤΑ ΜΟΝΑ ΕΝΕΡΓΑ ΜΟΝΤΕΛΑ (Τέρμα τα 404)
gm_llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
worker_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 3. Το Tool
search_tool_raw = DuckDuckGoSearchRun()

@tool("internet_search")
def search_tool(query: str):
    """Ψάχνει στο internet για τις τελευταίες ειδήσεις σχετικά με την AI."""
    return search_tool_raw.run(query)

# 4. Agents
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

# 5. Tasks
task_find = Task(
    description='Ψάξε στο internet και βρες μια αληθινή είδηση AI από τις τελευταίες 24 ώρες.',
    expected_output='Μια περίληψη της είδησης και το link της πηγής.',
    agent=hunter
)

task_write = Task(
    description='Γράψε ένα σενάριο 60 δευτερολέπτων βασισμένο στην είδηση. Πρέπει να έχει Hook, Body και Call to Action.',
    expected_output='Το πλήρες σενάριο σε μορφή κειμένου.',
    agent=writer,
    output_file='final_script.txt'
)

# 6. Kickoff
crew = Crew(
    agents=[hunter, writer],
    tasks=[task_find, task_write],
    verbose=True
)

print("--- Η Αυτοκρατορία ξεκινάει... ---")
crew.kickoff()