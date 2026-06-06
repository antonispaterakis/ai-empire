import os
import streamlit as st
from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

st.set_page_config(page_title="10-Agent AI Empire", page_icon="👑", layout="wide")
st.title("👑 The 10-Agent Content Factory")
st.markdown("Βάλε το θέμα σου και άσε τους 10 υπαλλήλους σου να σου φτιάξουν όλο το βίντεο.")

api_key = "" 
os.environ["GOOGLE_API_KEY"] = api_key

llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool_raw = DuckDuckGoSearchRun()

@tool("internet_search")
def search_tool(query: str):
    """Ψάχνει στο internet για ειδήσεις."""
    return search_tool_raw.run(query)

# User Input
topic = st.text_input("Για ποιο θέμα θέλεις να ψάξουν; (π.χ. AI News, Crypto, Tesla, Gaming)", value="AI News")

if st.button("🚀 Ξεκίνα την Παραγωγή!", type="primary"):
    with st.spinner("Η στρατιά των 10 Agents δουλεύει... (Λόγω Free Tier της Google, θα πάρει ~3 λεπτά για να μην κρασάρει)"):
        
        # --- 10 AGENTS ---
        agent_1 = Agent(role='Trend Hunter', goal=f'Βρες την πιο hot είδηση για {topic} των τελευταίων 24 ωρών.', backstory='Digital scout.', tools=[search_tool], llm=llm_model, verbose=False, allow_delegation=False)
        agent_2 = Agent(role='Scriptwriter', goal='Γράψε σενάριο 60 δευτερολέπτων με Hook.', backstory='Viral storyteller.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_3 = Agent(role='Title Master', goal='Γράψε 5 Clickbait τίτλους.', backstory='Expert στο YouTube CTR.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_4 = Agent(role='Visual Director', goal='Δημιούργησε 3 Midjourney Prompts στα Αγγλικά για το βίντεο.', backstory='Master των AI images.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_5 = Agent(role='Video Editor', goal='Γράψε οδηγίες μοντάζ (Zoom, SFX, Transitions).', backstory='Senior TikTok Editor.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_6 = Agent(role='Thumbnail Designer', goal='Περίγραψε την εικόνα του Thumbnail.', backstory='YouTube Thumbnail expert.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_7 = Agent(role='SEO Expert', goal='Γράψε Description και 10 viral hashtags.', backstory='Αλγοριθμικός μάγος.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_8 = Agent(role='Social Media Manager', goal='Γράψε ένα TikTok/Insta caption.', backstory='Viral marketer.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_9 = Agent(role='Voiceover Coach', goal='Δώσε οδηγίες για το ύφος της φωνής (ElevenLabs).', backstory='Σκηνοθέτης ήχου.', llm=llm_model, verbose=False, allow_delegation=False)
        agent_10 = Agent(role='General Manager', goal='Συγκέντρωσε όλα τα δεδομένα σε ένα ωραίο έγγραφο.', backstory='O CEO του καναλιού.', llm=llm_model, verbose=False, allow_delegation=False)

        # --- 10 TASKS ---
        t1 = Task(description=f'Βρες είδηση για: {topic}.', expected_output='Περίληψη και link.', agent=agent_1)
        t2 = Task(
        description=(
        'Γράψε ένα δυναμικό σενάριο 60 δευτερολέπτων για το θέμα. '
        'ΠΡΟΣΟΧΗ: Πρέπει να το χωρίσεις αυστηρά σε 6 Σκηνές (Scenes). '
        'Κάθε σκηνή πρέπει να έχει 1-2 μικρές προτάσεις. '
        'Χρησιμοποίησε αυτό ακριβώς το format:\n'
        '[Scene 1]: (Δυνατό Hook εδώ)\n'
        '[Scene 2]: (Κείμενο)\n'
        '[Scene 3]: (Κείμενο)\n'
        '[Scene 4]: (Κείμενο)\n'
        '[Scene 5]: (Κείμενο)\n'
        '[Scene 6]: (Call to Action - Π.χ. Κάνε subscribe)'
        ),
        expected_output='Σενάριο 60 δευτερολέπτων χωρισμένο σε 6 αριθμημένες σκηνές.',
        agent=agent_2,
        context=[t1]
          # Θυμήσου να βάλεις το context για να ξέρει την είδηση!
        )       
        t3 = Task(description='Φτιάξε 5 τίτλους.', expected_output='5 τίτλοι.', agent=agent_3)
        t4 = Task(description='Φτιάξε αγγλικά prompts για εικόνες.', expected_output='3 Image Prompts.', agent=agent_4)
        t5 = Task(description='Γράψε οδηγίες μοντάζ.', expected_output='Οδηγίες Editor.', agent=agent_5)
        t6 = Task(description='Στήσε το Thumbnail.', expected_output='Οδηγίες Thumbnail.', agent=agent_6)
        t7 = Task(description='Γράψε SEO.', expected_output='Description & Tags.', agent=agent_7)
        t8 = Task(description='Γράψε Social Promo.', expected_output='Caption.', agent=agent_8)
        t9 = Task(description='Οδηγίες φωνής.', expected_output='Οδηγίες ρυθμού.', agent=agent_9)
        t10 = Task(
        description=(
        'Μάζεψε όλα τα δεδομένα παραγωγής. '
        'Φτιάξε το Τελικό Έγγραφο σε Markdown. '
        'Βάλε έναν ξεκάθαρο τίτλο "🎬 FLIKI SCRIPT" και από κάτω βάλε ΜΟΝΟ το κείμενο '
        'των σκηνών του σεναρίου, χωρίς τα "[Scene 1]" κλπ, απλά τις προτάσεις με κενό ανάμεσά τους, '
        'ώστε ο χρήστης να κάνει κατευθείαν Copy-Paste. '
        'Μετά, πιο κάτω, βάλε τα Prompts (Agent 4), τον Τίτλο (Agent 3) και το SEO (Agent 7).'
        ),
        expected_output='Το τελικό οργανωμένο Master Document, έτοιμο για Copy-Paste στο Fliki.',
        agent=agent_10,
        context=[t1, t2, t3, t4, t5, t6, t7, t8, t9]
        )
        # --- CREW ---
        crew = Crew(
            agents=[agent_1, agent_2, agent_3, agent_4, agent_5, agent_6, agent_7, agent_8, agent_9, agent_10],
            tasks=[t1, t2, t3, t4, t5, t6, t7, t8, t9, t10],
            max_rpm=3, # ΑΥΤΟ ΣΕ ΣΩΖΕΙ ΑΠΟ ΤΟ ERROR ΤΗΣ GOOGLE!
            verbose=False
        )
        
        result = crew.kickoff()
        
        st.success("👑 Η Αυτοκρατορία σου μίλησε! Το Πακέτο Παραγωγής είναι έτοιμο.")
        st.markdown(result.raw)