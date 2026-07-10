import streamlit as st
import requests
import datetime
import logging
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Personalized Networking Assistant | SaaS Portal",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://networking-backend-1mi1.onrender.com"

# Quietly check backend connectivity
api_healthy = False
try:
    res = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
    if res.status_code == 200:
        api_healthy = True
except Exception:
    pass

# Inject premium dark theme CSS and custom workspace menu styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main font override */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

/* Deep modern background */
.stApp {
    background: linear-gradient(135deg, #070b13 0%, #101625 50%, #070b13 100%) !important;
    color: #f1f5f9 !important;
}

/* Clean up Streamlit Default Components */
header[data-testid="stHeader"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}
div[data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
}
div[data-testid="stToolbar"] {
    display: none !important;
    visibility: hidden !important;
}
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}
.stAppDeployButton {
    display: none !important;
    visibility: hidden !important;
}
.viewerBadge_container__1712a {
    display: none !important;
}

/* Reduce Streamlit container padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
    color: #818cf8 !important;
}

/* Sidebar Account Card */
.user-profile-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}
.avatar-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}
.user-avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white;
    font-weight: 700;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.35);
}
.user-info {
    display: flex;
    flex-direction: column;
}
.user-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #f8fafc;
}
.user-email {
    font-size: 0.75rem;
    color: #94a3b8;
}
.user-tier-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #fbbf24;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    text-align: center;
    text-transform: uppercase;
}

/* Sidebar Titles */
.sidebar-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #6366f1;
    margin: 1.25rem 0.5rem 0.5rem 0.5rem;
    text-transform: uppercase;
}

/* Styled radio navigation buttons in sidebar */
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: rgba(30, 41, 59, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-radius: 8px !important;
    padding: 0.65rem 0.85rem !important;
    margin-bottom: 0.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    color: #94a3b8 !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: rgba(99, 102, 241, 0.08) !important;
    border-color: rgba(99, 102, 241, 0.2) !important;
    color: #f1f5f9 !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"][data-checked="true"] {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.1) !important;
}
/* Hide native radio button elements inside our styled labels */
div[data-testid="stRadio"] label[data-baseweb="radio"] div[data-checked] {
    display: none !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] input {
    display: none !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] div {
    padding: 0 !important;
    margin: 0 !important;
}

/* Beautiful Title Card */
.header-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.3) 100%);
    border: 1px solid rgba(99, 102, 241, 0.15);
    padding: 1.75rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    text-align: center;
}
.main-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.subtitle {
    font-size: 1rem;
    color: #94a3b8;
    max-width: 800px;
    margin: 0 auto;
}

/* Container cards for separate modules */
.module-card {
    background: rgba(30, 41, 59, 0.35) !important;
    border: 1px solid rgba(99, 102, 241, 0.12) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
}

/* Suggested Icebreaker Cards */
.starter-card {
    background: rgba(17, 24, 39, 0.45) !important;
    border-left: 4px solid #6366f1 !important;
    border-top: 1px solid rgba(255, 255, 255, 0.02) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.02) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.02) !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.starter-card:hover {
    border-left-color: #a855f7 !important;
    background: rgba(17, 24, 39, 0.7) !important;
    transform: translateX(4px) !important;
}
.starter-text {
    font-size: 1.02rem !important;
    line-height: 1.5 !important;
    color: #f1f5f9 !important;
    font-weight: 450 !important;
}

/* Theme Badges */
.theme-badge {
    background: rgba(99, 102, 241, 0.12) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    border-radius: 20px !important;
    padding: 0.25rem 0.75rem !important;
    margin-right: 0.5rem !important;
    margin-bottom: 0.5rem !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.35rem !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}
.badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.dot-verified {
    background-color: #10b981 !important;
}
.dot-unverified {
    background-color: #f59e0b !important;
}

/* Fact Verification status styles */
.fact-container {
    background: rgba(15, 23, 42, 0.55) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin-top: 0.75rem !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
}
.fact-title-verified {
    color: #34d399 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    margin-bottom: 0.3rem !important;
}
.fact-title-unverified {
    color: #fbbf24 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    margin-bottom: 0.3rem !important;
}
.fact-summary {
    font-size: 0.88rem !important;
    line-height: 1.4 !important;
    color: #cbd5e1 !important;
    margin-bottom: 0.4rem !important;
}
.fact-link {
    font-size: 0.78rem !important;
    color: #60a5fa !important;
    text-decoration: none !important;
}
.fact-link:hover {
    text-decoration: underline !important;
}

/* Custom interactive buttons styling */
button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.25s ease !important;
}
button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
}

button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #f1f5f9 !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.25s ease !important;
}
button[kind="secondary"]:hover {
    background: rgba(30, 41, 59, 0.8) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
}
</style>
""", unsafe_allow_html=True)


# Initialize session state variables
if "current_generation" not in st.session_state:
    st.session_state.current_generation = None
if "fact_checks" not in st.session_state:
    st.session_state.fact_checks = {}
if "profile_bio" not in st.session_state:
    st.session_state.profile_bio = ""
if "event_description" not in st.session_state:
    st.session_state.event_description = ""
if "local_history" not in st.session_state:
    st.session_state.local_history = []

# Fetch history quietly to populate the state
def refresh_history_data():
    if api_healthy:
        try:
            res = requests.get(f"{BACKEND_URL}/api/history", timeout=3)
            if res.status_code == 200:
                st.session_state.local_history = res.json()
        except Exception:
            pass

refresh_history_data()


# ----------------------------------------------------
# SIDEBAR Restructuring
# ----------------------------------------------------
st.sidebar.markdown(f"""
<div class="user-profile-card">
    <div class="avatar-container">
        <div class="user-avatar">US</div>
        <div class="user-info">
            <div class="user-name">Active User</div>
            <div class="user-email">portfolio.user@saas.io</div>
        </div>
    </div>
    <div class="user-tier-badge">Premium Account</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='sidebar-title'>Workspace Control Panel</div>", unsafe_allow_html=True)

# Radio workspace navigation selector
workspace = st.sidebar.radio(
    "Workspaces",
    options=[
        "🤖 AI Generation Hub",
        "👤 User Profiles & Bio Management",
        "📊 Interaction Logs & Auditing"
    ],
    key="workspace_nav",
    label_visibility="collapsed"
)


# Helper function to parse user context into bio & event details if matching layout prefix
def parse_context_details(ctx_str):
    bio_part = ctx_str
    event_part = ""
    if "Profile Bio:" in ctx_str and "Event Details:" in ctx_str:
        try:
            parts = ctx_str.split("Event Details:")
            bio_part = parts[0].replace("Profile Bio:", "").strip()
            event_part = parts[1].strip()
        except Exception:
            pass
    return bio_part, event_part


# ----------------------------------------------------
# WORKSPACE: AI Generation Hub
# ----------------------------------------------------
if workspace == "🤖 AI Generation Hub":
    # App Title & Header
    st.markdown("""
    <div class="header-container">
        <div class="main-title">🤝 Personalized Networking Assistant</div>
        <div class="subtitle">An enterprise-grade LLM intelligence portal designed to orchestrate context-aware conversation starters, verify technology references using Wikipedia context, and record real-time feedback auditing.</div>
    </div>
    """, unsafe_allow_html=True)

    # 1. User Input Area Module
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.subheader("📥 User Input Area Module")
    st.markdown("<p style='color: #94a3b8; font-size: 0.92rem; margin-top: -0.5rem;'>Enter context details to configure the generation. These details are stored persistently in the database.</p>", unsafe_allow_html=True)
    
    col_bio, col_event = st.columns(2)
    with col_bio:
        profile_bio_input = st.text_area(
            "Profile Bio Input (User context)",
            value=st.session_state.profile_bio,
            placeholder="E.g. Meet Alice, a Senior DevOps Engineer at Google. She likes Rust, Kubernetes, and hiking in the Pacific Northwest. She recently wrote a blog post on optimizing CI/CD workflows.",
            height=130,
            key="profile_bio_widget"
        )
    with col_event:
        event_description_input = st.text_area(
            "Event Description Input (Networking context)",
            value=st.session_state.event_description,
            placeholder="E.g. Chatting at KubeCon networking lounge, aiming to get advice on DevOps best practices, CI/CD pipelines, or seeking a mentor.",
            height=130,
            key="event_description_widget"
        )
        
    col_rel, col_tone = st.columns(2)
    with col_rel:
        relationship = st.selectbox(
            "Target Relationship",
            options=["Colleague", "Mentor", "Client", "Recruiter"],
            index=0
        )
    with col_tone:
        tone = st.selectbox(
            "Message Tone",
            options=["Professional", "Casual", "Warm"],
            index=0
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Sync input state
    st.session_state.profile_bio = profile_bio_input
    st.session_state.event_description = event_description_input

    # 2. Generation Engine Control Module
    st.markdown("<div class='module-card' style='padding: 1rem 1.5rem !important;'>", unsafe_allow_html=True)
    col_btn_gen, col_btn_fact, col_btn_spacer = st.columns([1, 1, 2])
    
    with col_btn_gen:
        generate_button = st.button("Generate Starters", type="primary", use_container_width=True)
    with col_btn_fact:
        fact_check_button = st.button("Request Fact Check", type="secondary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Action Trigger logic
    if generate_button:
        if not api_healthy:
            st.error("Backend API Connection Offline: Please launch the FastAPI backend server on port 8000.", icon="🔌")
        elif not profile_bio_input.strip() or not event_description_input.strip():
            st.warning("Please fill out both the Profile Bio Input and the Event Description Input to orchestrate the generator.")
        else:
            # Combine inputs cleanly as per architectural specifications
            combined_context = f"Profile Bio:\n{profile_bio_input.strip()}\n\nEvent Details:\n{event_description_input.strip()}"
            st.session_state.fact_checks = {}  # Clear previous check results
            
            with st.spinner("Invoking generation engine (DistilBERT theme parsing + GPT-2 starter generation)..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/generate",
                        json={
                            "context": combined_context,
                            "relationship": relationship.lower(),
                            "tone": tone.lower()
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        st.session_state.current_generation = response.json()
                        st.toast("Icebreakers generated successfully!", icon="✅")
                        refresh_history_data()
                    else:
                        st.error(f"Generation Engine Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to communicate with Generation Engine: {e}")

    if fact_check_button:
        if not st.session_state.current_generation:
            st.warning("No active generation found. Please generate conversation starters first before running fact check.")
        elif not api_healthy:
            st.error("Backend API Connection Offline. Fact-checker service unavailable.", icon="🔌")
        else:
            themes = st.session_state.current_generation.get("themes", [])
            if not themes:
                st.info("No explicit themes extracted from your profile input to fact-check.")
            else:
                st.session_state.fact_checks = {}
                with st.spinner("Requesting live Wikipedia context verification..."):
                    for theme in themes:
                        try:
                            check_res = requests.get(
                                f"{BACKEND_URL}/api/factcheck",
                                params={"query": theme},
                                timeout=10
                            )
                            if check_res.status_code == 200:
                                st.session_state.fact_checks[theme] = check_res.json()
                            else:
                                st.session_state.fact_checks[theme] = {"verified": False, "message": "Wikipedia verification returned error code."}
                        except Exception as e:
                            st.session_state.fact_checks[theme] = {"verified": False, "message": f"Connection lost: {e}"}
                st.toast("Wikipedia context lookup completed!", icon="🔍")

    # 3. Output Display & Chat Module
    if st.session_state.current_generation:
        gen_data = st.session_state.current_generation
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Output Display & Chat Module")
        
        # Display themes as beautiful badges (dynamic colors based on fact check status)
        st.markdown("#### **Extracted Themes & Entities**")
        themes = gen_data.get("themes", [])
        if themes:
            badge_html = ""
            for theme in themes:
                # Check status
                if theme in st.session_state.fact_checks:
                    is_verified = st.session_state.fact_checks[theme].get("verified", False)
                    if is_verified:
                        badge_html += f'<span class="theme-badge theme-badge-verified"><span class="badge-dot dot-verified"></span>✓ Verified: {theme}</span>'
                    else:
                        badge_html += f'<span class="theme-badge theme-badge-unverified"><span class="badge-dot dot-unverified"></span>⚠ Unverified: {theme}</span>'
                else:
                    badge_html += f'<span class="theme-badge">{theme}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.info("No explicit professional themes were extracted from the inputs.")

        st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
        st.markdown("#### **Suggested Conversation Starters**")
        
        # Render the starters with inline feedback controls
        for idx, starter in enumerate(gen_data.get("starters", [])):
            st.markdown(f"""
            <div class="starter-card">
                <div class="starter-text">"{starter}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            col_fb_like, col_fb_dislike, col_fb_comment = st.columns([1, 1.2, 5])
            
            with col_fb_like:
                if st.button("👍 Useful", key=f"like_{gen_data['id']}_{idx}"):
                    if api_healthy:
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
                                st.toast("Saved thumbs-up feedback!", icon="👍")
                                refresh_history_data()
                        except Exception as e:
                            st.error(f"Error submitting rating: {e}")
                    else:
                        st.error("API disconnected.")
            
            with col_fb_dislike:
                if st.button("👎 Not Useful", key=f"dislike_{gen_data['id']}_{idx}"):
                    if api_healthy:
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
                                st.toast("Saved thumbs-down feedback!", icon="👎")
                                refresh_history_data()
                        except Exception as e:
                            st.error(f"Error submitting rating: {e}")
                    else:
                        st.error("API disconnected.")
                        
            with col_fb_comment:
                with st.expander("📝 Custom Feedback Comment"):
                    c_text = st.text_input("Enter comment details", key=f"cmt_in_{gen_data['id']}_{idx}", label_visibility="collapsed")
                    if st.button("Submit comment", key=f"cmt_sub_{gen_data['id']}_{idx}"):
                        if api_healthy and c_text.strip():
                            try:
                                res = requests.post(
                                    f"{BACKEND_URL}/api/feedback",
                                    json={
                                        "id": gen_data["id"],
                                        "starter_index": idx,
                                        "rating": "thumbs_up",
                                        "comment": c_text
                                    }
                                )
                                if res.status_code == 200:
                                    st.toast("Comment submitted successfully!", icon="📝")
                                    refresh_history_data()
                            except Exception as e:
                                st.error(f"Error submitting comment: {e}")
                        elif not c_text.strip():
                            st.warning("Please type a comment before submitting.")
                        else:
                            st.error("API disconnected.")
            st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255, 255, 255, 0.05); margin: 0.5rem 0;'>", unsafe_allow_html=True)

        # Render Wikipedia Source Snippet Context if user ran fact-check
        if st.session_state.fact_checks:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 🔍 Wikipedia Fact-Checking Context Details")
            for theme, fact_data in st.session_state.fact_checks.items():
                if fact_data.get("verified"):
                    st.markdown(f"""
                    <div class="fact-container">
                        <div class="fact-title-verified">✓ {theme} (Wikipedia Page Verified)</div>
                        <div class="fact-summary">{fact_data.get('summary')}</div>
                        <a href="{fact_data.get('source_url')}" target="_blank" class="fact-link">View Wikipedia reference ↗</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="fact-container" style="border-left: 3px solid #f59e0b !important;">
                        <div class="fact-title-unverified">⚠ {theme} (No Wikipedia Match Found)</div>
                        <div class="fact-summary">{fact_data.get('message', 'No source details available. Check spelling.')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Integrated Data & Storage Layer View
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.subheader("📁 Local Data Store")
    st.markdown("<p style='color: #94a3b8; font-size: 0.92rem; margin-top: -0.5rem;'>Interactive overview of persistent profiles and generation records.</p>", unsafe_allow_html=True)

    store_tab_profiles, store_tab_audit = st.tabs(["👤 Saved User Profiles", "📊 System Interaction Audit Logs"])
    
    with store_tab_profiles:
        if not st.session_state.local_history:
            st.info("No generated user profiles recorded. Try generating starters above!")
        else:
            profile_records = []
            for entry in st.session_state.local_history:
                bio, event = parse_context_details(entry.get("context", ""))
                profile_records.append({
                    "Timestamp": entry.get("timestamp", "")[:19].replace("T", " "),
                    "User Bio Profile": bio[:100] + "..." if len(bio) > 100 else bio,
                    "Event Context": event[:80] + "..." if len(event) > 80 else event,
                    "Themes Extracted": ", ".join(entry.get("themes", [])) or "None",
                    "Relationship": entry.get("relationship", "").capitalize()
                })
            df_profiles = pd.DataFrame(profile_records)
            st.dataframe(df_profiles, use_container_width=True)

    with store_tab_audit:
        if not st.session_state.local_history:
            st.info("No system interaction logs available yet.")
        else:
            audit_records = []
            for entry in st.session_state.local_history:
                # Count feedbacks
                likes = sum(1 for fb in entry.get("feedbacks", []) if fb.get("rating") == "thumbs_up")
                dislikes = sum(1 for fb in entry.get("feedbacks", []) if fb.get("rating") == "thumbs_down")
                audit_records.append({
                    "Transaction ID": entry.get("id", ""),
                    "Timestamp": entry.get("timestamp", "")[:19].replace("T", " "),
                    "Tone Parameter": entry.get("tone", "").capitalize(),
                    "Starters Count": len(entry.get("starters", [])),
                    "👍 Likes": likes,
                    "👎 Dislikes": dislikes,
                    "Total Feedbacks": len(entry.get("feedbacks", []))
                })
            df_audit = pd.DataFrame(audit_records)
            st.dataframe(df_audit, use_container_width=True)
            
            # Simple refresh controls
            if st.button("Refresh Persistent Storage View"):
                refresh_history_data()
                st.toast("Storage tables updated!", icon="🔄")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# WORKSPACE: User Profiles & Bio Management
# ----------------------------------------------------
elif workspace == "👤 User Profiles & Bio Management":
    st.markdown("""
    <div class="header-container">
        <div class="main-title">👤 User Profiles & Bio Management</div>
        <div class="subtitle">CRM Workspace to audit, search, and manage context profiles recorded across past networking sessions.</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.local_history:
        st.info("No profile records detected in backend storage database. Try generating icebreakers in the AI Hub first!")
    else:
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        st.subheader("🔍 Search Profiles & Restore")
        
        search_query = st.text_input("Filter profiles by keyword (bio or themes):", placeholder="E.g. Google, Rust, Alice...")
        
        # Display list of cards representing each profile
        for idx, entry in enumerate(st.session_state.local_history):
            bio, event = parse_context_details(entry["context"])
            themes_str = ", ".join(entry["themes"])
            
            # Match search criteria
            if search_query.strip() and (
                search_query.lower() not in bio.lower() and
                search_query.lower() not in event.lower() and
                search_query.lower() not in themes_str.lower()
            ):
                continue
                
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <strong style="color:#a5b4fc; font-size:1.05rem;">Profile #{idx + 1} - Relationship: {entry['relationship'].capitalize()}</strong>
                    <span style="font-size:0.75rem; color:#94a3b8;">Created: {entry['timestamp'][:19].replace('T', ' ')}</span>
                </div>
                <div style="font-size:0.9rem; margin-bottom:0.5rem;"><strong>Bio context:</strong> {bio}</div>
                <div style="font-size:0.9rem; margin-bottom:0.5rem;"><strong>Event details:</strong> {event}</div>
                <div style="font-size:0.85rem; color:#94a3b8;"><strong>Themes:</strong> {themes_str or "None"}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add action button to restore/load this profile to active workspace
            col_load, _ = st.columns([1.5, 5])
            with col_load:
                if st.button("Load into Generation Hub", key=f"load_prof_{entry['id']}_{idx}", use_container_width=True):
                    # Set the values in session state
                    st.session_state.profile_bio = bio
                    st.session_state.event_description = event
                    # Switch workspaces
                    st.session_state.workspace_nav = "🤖 AI Generation Hub"
                    st.toast("Profile loaded successfully! Switched to AI Generation Hub.", icon="👤")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# WORKSPACE: Interaction Logs & Auditing
# ----------------------------------------------------
elif workspace == "📊 Interaction Logs & Auditing":
    st.markdown("""
    <div class="header-container">
        <div class="main-title">📊 Interaction Logs & Auditing</div>
        <div class="subtitle">System metrics control panel showcasing model execution parameters, feedback ratios, and complete audit tracking logs.</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.local_history:
        st.info("No audit data captured. Please complete at least one generation session.")
    else:
        # Aggregated Metrics Calculation
        total_generations = len(st.session_state.local_history)
        total_feedbacks = sum(len(item.get("feedbacks", [])) for item in st.session_state.local_history)
        
        likes = 0
        dislikes = 0
        comments_count = 0
        
        for item in st.session_state.local_history:
            for fb in item.get("feedbacks", []):
                if fb.get("rating") == "thumbs_up":
                    likes += 1
                elif fb.get("rating") == "thumbs_down":
                    dislikes += 1
                if fb.get("comment"):
                    comments_count += 1
                    
        # Metric display row
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        st.subheader("📈 System Metrics Overview")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.metric("Total API Requests", total_generations)
        with m_col2:
            st.metric("Logged Feedbacks", total_feedbacks)
        with m_col3:
            st.metric("👍 Total Likes", likes)
        with m_col4:
            st.metric("👎 Total Dislikes", dislikes)
        st.markdown("</div>", unsafe_allow_html=True)

        # Auditing table
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        st.subheader("📜 Detailed Audit Trails")
        
        audit_log = []
        for entry in st.session_state.local_history:
            for s_idx, starter in enumerate(entry.get("starters", [])):
                # Get feedback for this starter
                starter_feedbacks = [fb for fb in entry.get("feedbacks", []) if fb.get("starter_index") == s_idx]
                
                feedback_str = "No Feedback"
                comment_str = ""
                if starter_feedbacks:
                    fb_ratings = []
                    fb_comments = []
                    for f in starter_feedbacks:
                        fb_ratings.append("👍" if f.get("rating") == "thumbs_up" else "👎")
                        if f.get("comment"):
                            fb_comments.append(f.get("comment"))
                    feedback_str = ", ".join(fb_ratings)
                    comment_str = " | ".join(fb_comments)
                
                audit_log.append({
                    "Timestamp": entry.get("timestamp", "")[:19].replace("T", " "),
                    "Relationship": entry.get("relationship", "").capitalize(),
                    "Tone": entry.get("tone", "").capitalize(),
                    "Suggested Starter": starter[:80] + "..." if len(starter) > 80 else starter,
                    "Rating Value": feedback_str,
                    "Auditor Notes": comment_str
                })
                
        df_audit_full = pd.DataFrame(audit_log)
        st.dataframe(df_audit_full, use_container_width=True)
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        col_down_csv, _ = st.columns([1.5, 5])
        with col_down_csv:
            csv_data = df_audit_full.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV Audit Log",
                data=csv_data,
                file_name=f"networking_assistant_audit_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
