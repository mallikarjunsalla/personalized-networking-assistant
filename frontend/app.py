import streamlit as st
import requests
import datetime
import logging

# Page configuration
st.set_page_config(
    page_title="Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://networking-backend-imi1.onrender.com"

# Inject premium dark theme CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif;
}

/* Deep modern background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #f1f5f9;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.2) !important;
}

/* Beautiful Title Card */
.header-container {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    backdrop-filter: blur(8px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    text-align: center;
}

.main-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    max-width: 800px;
    margin: 0 auto;
}

/* Custom badges */
.theme-badge {
    background: rgba(99, 102, 241, 0.2);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    display: inline-block;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Card representation for output starters */
.starter-card {
    background: rgba(30, 41, 59, 0.6);
    border-left: 5px solid #818cf8;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 0 12px 12px 0;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}

.starter-card:hover {
    border-left-color: #c084fc;
    background: rgba(30, 41, 59, 0.8);
    transform: translateX(4px);
}

.starter-text {
    font-size: 1.05rem;
    line-height: 1.5;
    color: #e2e8f0;
}

/* Fact Verification Styling */
.fact-box {
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.fact-verified {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.fact-unverified {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.fact-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.fact-source {
    font-size: 0.85rem;
    color: #60a5fa;
    text-decoration: none;
    margin-top: 0.5rem;
    display: inline-block;
}

.fact-source:hover {
    text-decoration: underline;
}

/* Custom button hover effects */
button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}
</style>
""", unsafe_allow_html=True)

# App Title & Header
st.markdown("""
<div class="header-container">
    <div class="main-title">🤝 Personalized Networking Assistant</div>
    <div class="subtitle">A decoupled intelligence tool designed to draft context-aware conversation starters, verify professional facts using live Wikipedia context, and refine results via active feedback loops.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar settings and connection health check
st.sidebar.image("https://img.icons8.com/nolan/96/handshake.png", width=80)
st.sidebar.markdown("## Navigation & Config")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 API Connection status")

api_healthy = False
try:
    res = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if res.status_code == 200:
        st.sidebar.success("Backend API Connected")
        api_healthy = True
    else:
        st.sidebar.warning(f"Backend returned: {res.status_code}")
except Exception:
    st.sidebar.error("Cannot connect to Backend API. Please start FastAPI server on port 8000.")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Engine Info")
st.sidebar.info(
    "**Theme Extractor:**\nDistilBERT NER\n\n"
    "**Text Generator:**\nGPT-2 Text Generation\n\n"
    "**Fact Verifier:**\nLive Wikipedia API"
)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Smart Starters", "🔍 Fact Verification", "📜 History Review"])

# Initialize session state for generation and inputs
if "current_generation" not in st.session_state:
    st.session_state.current_generation = None

# Tab 1: Smart Starters
with tab1:
    st.markdown("### Generate Context-Aware Conversation Starters")
    
    col_input, col_settings = st.columns([2, 1])
    
    with col_input:
        context_input = st.text_area(
            "Enter details about the person or situation (e.g. professional background, shared interests, recent post, or event details):",
            placeholder="E.g. Meet Alice, a Senior DevOps Engineer at Google. She likes Rust, Kubernetes, and hiking in the Pacific Northwest. She recently wrote a blog post on optimizing CI/CD workflows using GitHub Actions.",
            height=150
        )
        
    with col_settings:
        relationship = st.selectbox(
            "Target Relationship",
            options=["Colleague", "Mentor", "Client", "Recruiter"],
            index=0
        )
        
        tone = st.selectbox(
            "Message Tone",
            options=["Professional", "Casual", "Warm"],
            index=0
        )
        
        generate_button = st.button("Generate Icebreakers", type="primary", use_container_width=True)

    if generate_button:
        if not api_healthy:
            st.error("Error: Backend API is not running. Please launch the FastAPI server first.")
        elif not context_input.strip():
            st.warning("Please provide some context details about the person or situation.")
        else:
            with st.spinner("Analyzing context (DistilBERT) and generating starters (GPT-2)..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/generate",
                        json={
                            "context": context_input,
                            "relationship": relationship.lower(),
                            "tone": tone.lower()
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        st.session_state.current_generation = response.json()
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to communicate with API: {e}")

    # Display generated starters from session state (so they persist during feedback clicks)
    if st.session_state.current_generation:
        gen_data = st.session_state.current_generation
        st.markdown("---")
        st.markdown("#### ⚡ Extracted Themes (via DistilBERT)")
        
        # Display themes as badges
        themes = gen_data.get("themes", [])
        if themes:
            badge_html = ""
            for t in themes:
                badge_html += f'<span class="theme-badge">{t}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.info("No explicit themes extracted. Using general professional starters.")
            
        st.markdown("#### ✍️ Suggested Conversation Starters (via GPT-2)")
        
        for idx, starter in enumerate(gen_data.get("starters", [])):
            st.markdown(f"""
            <div class="starter-card">
                <div class="starter-text">"{starter}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Inline Feedback widgets
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
            
            with fb_col1:
                # Use a specific key for each button to avoid session conflicts
                if st.button("👍 Useful", key=f"like_{gen_data['id']}_{idx}"):
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/api/feedback",
                            json={
                                "id": gen_data["id"],
                                "starter_index": idx,
                                "rating": "thumbs_up",
                                "comment": ""
                            }
                        )
                        if res.status_code == 200:
                            st.success("Liked!", icon="✅")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
            with fb_col2:
                if st.button("👎 Not Useful", key=f"dislike_{gen_data['id']}_{idx}"):
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/api/feedback",
                            json={
                                "id": gen_data["id"],
                                "starter_index": idx,
                                "rating": "thumbs_down",
                                "comment": ""
                            }
                        )
                        if res.status_code == 200:
                            st.success("Disliked!", icon="✅")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
            with fb_col3:
                # Expander for comment input
                with st.expander("Add comment/note"):
                    comment_text = st.text_input("Feedback details", key=f"comment_text_{gen_data['id']}_{idx}", label_visibility="collapsed")
                    if st.button("Submit comment", key=f"submit_comment_{gen_data['id']}_{idx}"):
                        try:
                            res = requests.post(
                                f"{BACKEND_URL}/api/feedback",
                                json={
                                    "id": gen_data["id"],
                                    "starter_index": idx,
                                    "rating": "thumbs_up", # default positive if comment added
                                    "comment": comment_text
                                }
                            )
                            if res.status_code == 200:
                                st.success("Comment saved!", icon="✅")
                        except Exception as e:
                            st.error(f"Error: {e}")
            st.markdown("<br>", unsafe_allow_html=True)


# Tab 2: Fact Verification
with tab2:
    st.markdown("### Verify Professional Facts / Claims")
    st.markdown("Quickly lookup and factcheck technology standards, companies, or concepts before mentioning them in your network outreach.")
    
    fact_query = st.text_input(
        "Enter a topic, technology, or company name to verify:",
        placeholder="E.g. Kubernetes, Rust programming language, OpenAI, DistilBERT"
    )
    
    verify_button = st.button("Verify Claim", type="primary")
    
    if verify_button:
        if not api_healthy:
            st.error("Error: Backend API is not running. Please launch the FastAPI server first.")
        elif not fact_query.strip():
            st.warning("Please provide a search query.")
        else:
            with st.spinner("Fetching live Wikipedia context..."):
                try:
                    response = requests.get(
                        f"{BACKEND_URL}/api/factcheck",
                        params={"query": fact_query},
                        timeout=15
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("verified"):
                            st.markdown(f"""
                            <div class="fact-box fact-verified">
                                <div class="fact-title">✓ Verified Match: {data.get('title')}</div>
                                <p style="margin-bottom: 0.5rem;">{data.get('summary')}</p>
                                <a href="{data.get('source_url')}" target="_blank" class="fact-source">Read full Wikipedia source ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="fact-box fact-unverified">
                                <div class="fact-title">✗ Unverified / No Match</div>
                                <p style="margin-bottom: 0;">{data.get('message')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to communicate with API: {e}")


# Tab 3: History Review
with tab3:
    st.markdown("### History & Feedback Review")
    st.markdown("Browse previously generated icebreakers and view structured feedback metrics to monitor generation quality.")
    
    refresh_button = st.button("Refresh History")
    
    if not api_healthy:
        st.error("Error: Backend API is not running. Connect to backend to load history.")
    else:
        try:
            history_response = requests.get(f"{BACKEND_URL}/api/history", timeout=5)
            if history_response.status_code == 200:
                history_data = history_response.json()
                
                if not history_data:
                    st.info("No generation history found. Try creating some icebreakers in the first tab!")
                else:
                    # Let's count some metrics
                    total_generations = len(history_data)
                    total_feedbacks = sum(len(item.get("feedbacks", [])) for item in history_data)
                    
                    likes = 0
                    dislikes = 0
                    comments_count = 0
                    
                    for item in history_data:
                        for fb in item.get("feedbacks", []):
                            if fb.get("rating") == "thumbs_up":
                                likes += 1
                            elif fb.get("rating") == "thumbs_down":
                                dislikes += 1
                            if fb.get("comment"):
                                comments_count += 1
                                
                    # Stats display
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    with metric_col1:
                        st.metric("Total Generated Prompts", total_generations)
                    with metric_col2:
                        st.metric("Total Feedbacks", total_feedbacks)
                    with metric_col3:
                        st.metric("👍 Likes", likes)
                    with metric_col4:
                        st.metric("👎 Dislikes", dislikes)
                        
                    st.markdown("---")
                    
                    # Display history log
                    for item in history_data:
                        t_parsed = datetime.datetime.fromisoformat(item["timestamp"])
                        formatted_time = t_parsed.strftime("%Y-%m-%d %H:%M:%S")
                        
                        expander_title = f"💬 Outreaches for {item['relationship'].capitalize()} ({item['tone'].capitalize()}) - {formatted_time}"
                        with st.expander(expander_title):
                            st.write(f"**Context Input:** {item['context']}")
                            
                            # Themes
                            t_html = ""
                            for theme in item.get("themes", []):
                                t_html += f'<span class="theme-badge">{theme}</span>'
                            if t_html:
                                st.markdown(f"**Themes:** {t_html}", unsafe_allow_html=True)
                                
                            st.markdown("**Generated Starters:**")
                            for s_idx, starter in enumerate(item["starters"]):
                                # See if there's feedback for this starter
                                star_feedbacks = [fb for fb in item.get("feedbacks", []) if fb.get("starter_index") == s_idx]
                                fb_str = ""
                                if star_feedbacks:
                                    fb_details = []
                                    for f in star_feedbacks:
                                        icon = "👍" if f.get("rating") == "thumbs_up" else "👎"
                                        detail = f"{icon}"
                                        if f.get("comment"):
                                            detail += f" ({f.get('comment')})"
                                        fb_details.append(detail)
                                    fb_str = f" | *Feedback: {', '.join(fb_details)}*"
                                    
                                st.write(f"{s_idx + 1}. \"{starter}\" {fb_str}")
                                
            else:
                st.error(f"Error fetching history: {history_response.status_code}")
        except Exception as e:
            st.error(f"Failed to load history from API: {e}")
