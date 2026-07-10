import streamlit as st
import requests
import datetime
import logging
import pandas as pd

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Networking Assistant · Pro",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://networking-backend-1mi1.onrender.com"

# ─────────────────────────────────────────────────────────────
#  SILENT BACKEND HEALTH CHECK
# ─────────────────────────────────────────────────────────────
api_healthy = False
try:
    _h = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
    if _h.status_code == 200:
        api_healthy = True
except Exception:
    pass

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  ·  NO header hiding — sidebar toggle stays alive
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

/* ── App Background ──────────────────────────────────────── */
.stApp {
    background-color: #121214 !important;
    color: #E2E8F0 !important;
}

/* ── Hide ONLY deploy / share / fork buttons — NOT the header ── */
.stAppDeployButton          { display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }
button[title="View app in Streamlit Community Cloud"] { display: none !important; }
/* reduce default top padding so page starts cleanly */
.block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #1A1A20 !important;
    border-right: 1px solid #2A2A35 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
}

/* ── Login card ──────────────────────────────────────────── */
.login-card {
    background: #1E1E24;
    border: 1px solid #2E2E3A;
    border-radius: 14px;
    padding: 1.4rem 1.2rem;
    margin-bottom: 1rem;
}
.login-title {
    font-size: 1rem;
    font-weight: 700;
    color: #C4B5FD;
    margin-bottom: 0.1rem;
    letter-spacing: 0.02em;
}
.login-sub {
    font-size: 0.73rem;
    color: #64748B;
    margin-bottom: 1rem;
}

/* ── Profile card ────────────────────────────────────────── */
.profile-card {
    background: linear-gradient(135deg, #1E1E2A 0%, #16161E 100%);
    border: 1px solid #2E2E3A;
    border-radius: 14px;
    padding: 1.25rem 1.1rem;
    margin-bottom: 1rem;
    text-align: center;
}
.profile-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #8B5CF6, #6366F1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.65rem auto;
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    box-shadow: 0 0 18px rgba(139, 92, 246, 0.35);
    letter-spacing: 0.02em;
}
.profile-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 0.15rem;
}
.profile-email {
    font-size: 0.72rem;
    color: #64748B;
    margin-bottom: 0.55rem;
}
.tier-badge {
    display: inline-block;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #A78BFA;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
}

/* ── Sidebar nav label ────────────────────────────────────── */
.nav-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4B5563;
    margin: 1.1rem 0 0.4rem 0;
}

/* ── Section heading cards ───────────────────────────────── */
.section-card {
    background: #1E1E24;
    border: 1px solid #2A2A35;
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
}
.section-header {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #2A2A35;
}
.section-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.icon-violet { background: rgba(139, 92, 246, 0.15); }
.icon-blue   { background: rgba(59, 130, 246, 0.15); }
.icon-teal   { background: rgba(20, 184, 166, 0.15); }

.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0;
}
.section-desc {
    font-size: 0.78rem;
    color: #64748B;
    margin: 0;
}

/* ── Starter output cards ────────────────────────────────── */
.starter-card {
    background: #16161E;
    border-left: 3px solid #8B5CF6;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.1rem;
    margin-bottom: 0.9rem;
    transition: border-left-color 0.2s ease, background 0.2s ease;
}
.starter-card:hover {
    border-left-color: #6366F1;
    background: #1A1A24;
}
.starter-num {
    font-size: 0.68rem;
    font-weight: 700;
    color: #8B5CF6;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.starter-text {
    font-size: 0.97rem;
    color: #E2E8F0;
    line-height: 1.55;
}

/* ── Theme badges ────────────────────────────────────────── */
.theme-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem; }
.theme-badge {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.25);
    color: #A5B4FC;
    border-radius: 20px;
    padding: 0.22rem 0.7rem;
    font-size: 0.74rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.badge-dot {
    width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
}
.dot-green  { background: #10B981; }
.dot-yellow { background: #F59E0B; }
.dot-grey   { background: #475569; }

/* ── Fact check result cards ─────────────────────────────── */
.fact-card {
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.fact-verified {
    background: rgba(16, 185, 129, 0.07);
    border: 1px solid rgba(16, 185, 129, 0.25);
}
.fact-unverified {
    background: rgba(245, 158, 11, 0.07);
    border: 1px solid rgba(245, 158, 11, 0.25);
}
.fact-title-v { color: #34D399; font-weight: 600; font-size: 0.88rem; }
.fact-title-u { color: #FBBF24; font-weight: 600; font-size: 0.88rem; }
.fact-summary {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-top: 0.3rem;
    line-height: 1.45;
}
.fact-link {
    font-size: 0.76rem;
    color: #60A5FA;
    text-decoration: none;
    margin-top: 0.35rem;
    display: inline-block;
}
.fact-link:hover { text-decoration: underline; }

/* ── Verification status banner ──────────────────────────── */
.status-banner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 0.9rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 1.1rem;
}
.status-verified   { background: rgba(16,185,129,0.1);  border: 1px solid rgba(16,185,129,0.3);  color: #34D399; }
.status-pending    { background: rgba(245,158,11,0.1);   border: 1px solid rgba(245,158,11,0.3);   color: #FBBF24; }
.status-none       { background: rgba(71,85,105,0.15);   border: 1px solid rgba(71,85,105,0.3);   color: #94A3B8; }

/* ── Feedback row buttons ────────────────────────────────── */
.feedback-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.4rem;
}

/* ── Page hero ───────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #1E1E2A 0%, #16161E 100%);
    border: 1px solid #2A2A35;
    border-radius: 16px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.75rem;
    text-align: center;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #8B5CF6, #6366F1, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 0.88rem;
    color: #64748B;
    max-width: 680px;
    margin: 0 auto;
    line-height: 1.55;
}

/* ── Gate screen ─────────────────────────────────────────── */
.gate-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 1rem;
    text-align: center;
}
.gate-icon { font-size: 3rem; margin-bottom: 1rem; }
.gate-title { font-size: 1.5rem; font-weight: 700; color: #8B5CF6; margin-bottom: 0.4rem; }
.gate-sub { font-size: 0.88rem; color: #64748B; }

/* ── Tab styling ─────────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-size: 0.83rem !important;
    font-weight: 600 !important;
}

/* ── Streamlit overrides ─────────────────────────────────── */
div[data-testid="stTextArea"] textarea {
    background: #16161E !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.2) !important;
}
div[data-testid="stTextInput"] input {
    background: #16161E !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.2) !important;
}
div[data-testid="stSelectbox"] > div {
    background: #16161E !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
}

/* Metric card tweaks */
div[data-testid="metric-container"] {
    background: #16161E !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
div[data-testid="metric-container"] label {
    font-size: 0.73rem !important;
    color: #64748B !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: #2A2A35 !important; margin: 1.25rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False,
    "user_email": "",
    "user_name": "Mallikarjun Salla",
    "user_initials": "MS",
    "current_generation": None,
    "fact_checks": {},
    "fact_status": "none",      # "none" | "pending" | "verified"
    "profile_bio": "",
    "event_description": "",
    "local_history": [],
    "workspace": "🤖 AI Generation Hub",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
#  HELPER: silently refresh history from backend
# ─────────────────────────────────────────────────────────────
def refresh_history():
    if api_healthy:
        try:
            r = requests.get(f"{BACKEND_URL}/api/history", timeout=3)
            if r.status_code == 200:
                st.session_state.local_history = r.json()
        except Exception:
            pass

refresh_history()


# ─────────────────────────────────────────────────────────────
#  HELPER: parse combined context string back into bio / event
# ─────────────────────────────────────────────────────────────
def split_context(ctx: str):
    bio, event = ctx, ""
    if "Profile Bio:" in ctx and "Event Details:" in ctx:
        try:
            parts = ctx.split("Event Details:")
            bio   = parts[0].replace("Profile Bio:", "").strip()
            event = parts[1].strip()
        except Exception:
            pass
    return bio, event


# ═════════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Brand mark ────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.55rem;padding:0 0.25rem 1rem 0.25rem;">
        <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#8B5CF6,#6366F1);
                    display:flex;align-items:center;justify-content:center;font-size:1rem;">🤝</div>
        <div>
            <div style="font-size:0.88rem;font-weight:700;color:#F1F5F9;line-height:1.2;">Networking AI</div>
            <div style="font-size:0.68rem;color:#475569;">Portfolio · SaaS Edition</div>
        </div>
    </div>
    <hr style="margin:0 0 1rem 0;">
    """, unsafe_allow_html=True)

    # ── LOGIN / PROFILE BLOCK ─────────────────────────────────
    if not st.session_state.logged_in:
        # ── Login portal ──────────────────────────────────────
        st.markdown("""
        <div class="login-card">
            <div class="login-title">🔐 User Login Portal</div>
            <div class="login-sub">Sign in to access your AI workspace</div>
        </div>
        """, unsafe_allow_html=True)

        login_email    = st.text_input("Email address", placeholder="you@example.com",  key="l_email")
        login_password = st.text_input("Password",      placeholder="••••••••••",       key="l_pass", type="password")
        login_btn      = st.button("Sign In →", type="primary", use_container_width=True)

        if login_btn:
            if login_email.strip() and login_password.strip():
                st.session_state.logged_in  = True
                st.session_state.user_email = login_email.strip()
                # Derive initials from email local-part
                local = login_email.split("@")[0]
                parts = local.replace(".", " ").replace("_", " ").split()
                st.session_state.user_initials = "".join(p[0].upper() for p in parts[:2]) or "U"
                st.toast("Signed in successfully!", icon="✅")
                st.rerun()
            else:
                st.warning("Please enter both email and password.")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.caption("Demo: use any email + password to sign in.")

    else:
        # ── Profile card ───────────────────────────────────────
        initials = st.session_state.user_initials
        email    = st.session_state.user_email
        name     = st.session_state.user_name

        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-avatar">{initials}</div>
            <div class="profile-name">{name}</div>
            <div class="profile-email">{email}</div>
            <span class="tier-badge">Pro Developer</span>
        </div>
        """, unsafe_allow_html=True)

        # API status indicator (compact, no loud card)
        status_icon  = "🟢" if api_healthy else "🔴"
        status_label = "Backend Online" if api_healthy else "Backend Offline"
        st.markdown(
            f"<div style='font-size:0.72rem;color:#64748B;text-align:center;margin-bottom:0.75rem;'>"
            f"{status_icon} {status_label}</div>",
            unsafe_allow_html=True
        )

        # ── Workspace navigation ────────────────────────────────
        st.markdown("<div class='nav-label'>Navigation</div>", unsafe_allow_html=True)
        workspace = st.radio(
            "nav",
            options=[
                "🤖 AI Generation Hub",
                "👤 User Profiles & Bio Management",
                "📊 Interaction Logs & Auditing",
            ],
            index=["🤖 AI Generation Hub",
                   "👤 User Profiles & Bio Management",
                   "📊 Interaction Logs & Auditing"].index(st.session_state.workspace),
            label_visibility="collapsed",
        )
        st.session_state.workspace = workspace

        st.markdown("<hr>", unsafe_allow_html=True)

        # Logout
        if st.button("↩ Logout", use_container_width=True):
            for k in ["logged_in", "user_email", "user_initials", "current_generation",
                      "fact_checks", "fact_status", "profile_bio", "event_description"]:
                st.session_state[k] = defaults[k]
            st.session_state.workspace = "🤖 AI Generation Hub"
            st.toast("You have been signed out.", icon="👋")
            st.rerun()


# ═════════════════════════════════════════════════════════════
#  MAIN PANEL  —  GATE if not logged in
# ═════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="gate-container">
        <div class="gate-icon">🔐</div>
        <div class="gate-title">Authentication Required</div>
        <div class="gate-sub">
            Please sign in using the sidebar login portal to access<br>
            your AI-powered Networking Assistant workspace.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════
#  AUTHENTICATED — PAGE HERO
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-title">🤝 Personalized Networking Assistant</div>
    <div class="hero-sub">
        Enterprise-grade LLM orchestration platform — generate context-aware conversation
        starters, verify professional claims via live Wikipedia context, and maintain a
        complete interaction audit trail.
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
#  WORKSPACE ROUTING
# ═════════════════════════════════════════════════════════════
ws = st.session_state.workspace


# ─────────────────────────────────────────────────────────────
#  WORKSPACE 1 ·  AI GENERATION HUB
# ─────────────────────────────────────────────────────────────
if ws == "🤖 AI Generation Hub":

    # ══════════════════════════════════════════════════════════
    #  CONDITION 1 — USER INPUT AREA MODULE
    # ══════════════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon icon-violet">📥</div>
            <div>
                <div class="section-title">User Input Area Module</div>
                <div class="section-desc">Provide target professional context and networking event details</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col_bio, col_event = st.columns(2)

        with col_bio:
            st.markdown("**Profile Bio Input** — *Target Professional Context*")
            profile_bio = st.text_area(
                "profile_bio",
                value=st.session_state.profile_bio,
                placeholder=(
                    "E.g. Meet Alice, a Senior DevOps Engineer at Google. She loves Rust, "
                    "Kubernetes, and hiking in the Pacific Northwest. She recently published "
                    "a blog post on optimising CI/CD workflows using GitHub Actions."
                ),
                height=155,
                label_visibility="collapsed",
                key="bio_input",
            )

        with col_event:
            st.markdown("**Event Description Input** — *Networking Event Context*")
            event_desc = st.text_area(
                "event_desc",
                value=st.session_state.event_description,
                placeholder=(
                    "E.g. Attending KubeCon North America — networking lounge session. "
                    "Goal: connect with senior engineers, learn about open-source DevOps tooling "
                    "and explore potential mentorship opportunities."
                ),
                height=155,
                label_visibility="collapsed",
                key="event_input",
            )

        col_rel, col_tone, _ = st.columns([1, 1, 2])
        with col_rel:
            relationship = st.selectbox("Target Relationship", ["Colleague", "Mentor", "Client", "Recruiter"])
        with col_tone:
            tone = st.selectbox("Conversation Tone", ["Professional", "Casual", "Warm"])

    # Sync to state
    st.session_state.profile_bio      = profile_bio
    st.session_state.event_description = event_desc

    st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  CONDITION 2 — GENERATION ENGINE CONTROL & OUTPUT VIEW
    # ══════════════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon icon-blue">⚡</div>
            <div>
                <div class="section-title">Generation Engine Control & Output View</div>
                <div class="section-desc">Orchestrate AI generation and Wikipedia fact-verification pipeline</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Action triggers ────────────────────────────────────────
    btn_col1, btn_col2, _ = st.columns([1.3, 1.3, 3])

    with btn_col1:
        gen_btn = st.button("✨  Generate Starters", type="primary", use_container_width=True)
    with btn_col2:
        fact_btn = st.button("🔍  Request Fact Check", type="secondary", use_container_width=True)

    # ── Generate handler ───────────────────────────────────────
    if gen_btn:
        if not api_healthy:
            st.error("Backend API is offline. Please start the FastAPI server on port 8000.", icon="🔌")
        elif not profile_bio.strip() or not event_desc.strip():
            st.warning("Both **Profile Bio** and **Event Description** fields are required.")
        else:
            combined = f"Profile Bio:\n{profile_bio.strip()}\n\nEvent Details:\n{event_desc.strip()}"
            st.session_state.fact_checks  = {}
            st.session_state.fact_status  = "none"

            with st.spinner("Invoking DistilBERT NER → GPT-2 generation pipeline…"):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/api/generate",
                        json={"context": combined, "relationship": relationship.lower(), "tone": tone.lower()},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.session_state.current_generation = resp.json()
                        st.session_state.fact_status = "pending"
                        st.toast("Conversation starters generated!", icon="✅")
                        refresh_history()
                    else:
                        st.error(f"Engine error {resp.status_code}: {resp.json().get('detail', 'Unknown')}")
                except Exception as e:
                    st.error(f"Cannot reach Generation Engine: {e}")

    # ── Fact-check handler ─────────────────────────────────────
    if fact_btn:
        if not st.session_state.current_generation:
            st.warning("Run **Generate Starters** first to extract themes for fact-checking.")
        elif not api_healthy:
            st.error("Backend API is offline — fact-check unavailable.", icon="🔌")
        else:
            themes = st.session_state.current_generation.get("themes", [])
            if not themes:
                st.info("No named entities were extracted from the current profile — nothing to verify.")
            else:
                st.session_state.fact_checks = {}
                all_verified = True
                with st.spinner("Querying live Wikipedia API for each extracted entity…"):
                    for theme in themes:
                        try:
                            cr = requests.get(f"{BACKEND_URL}/api/factcheck", params={"query": theme}, timeout=10)
                            if cr.status_code == 200:
                                result = cr.json()
                                st.session_state.fact_checks[theme] = result
                                if not result.get("verified"):
                                    all_verified = False
                            else:
                                st.session_state.fact_checks[theme] = {"verified": False, "message": "API error."}
                                all_verified = False
                        except Exception as e:
                            st.session_state.fact_checks[theme] = {"verified": False, "message": str(e)}
                            all_verified = False
                st.session_state.fact_status = "verified" if all_verified else "pending"
                st.toast("Wikipedia verification complete!", icon="🔍")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Fact Verification Status banner ───────────────────────
    fact_status = st.session_state.fact_status
    if fact_status == "verified":
        st.markdown("""<div class="status-banner status-verified">
            ✅&nbsp; Fact Verification Status: <strong>Verified</strong>
            &nbsp;·&nbsp; All extracted entities confirmed via Wikipedia
        </div>""", unsafe_allow_html=True)
    elif fact_status == "pending":
        st.markdown("""<div class="status-banner status-pending">
            ⚠️&nbsp; Fact Verification Status: <strong>Pending / Partial</strong>
            &nbsp;·&nbsp; Click "Request Fact Check" to verify all themes
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="status-banner status-none">
            ○&nbsp; Fact Verification Status: <strong>Not Run</strong>
            &nbsp;·&nbsp; Generate starters then request a fact check
        </div>""", unsafe_allow_html=True)

    # ── Output block ───────────────────────────────────────────
    if st.session_state.current_generation:
        gen = st.session_state.current_generation

        # Themes row
        themes = gen.get("themes", [])
        if themes:
            badge_html = '<div class="theme-row">'
            for t in themes:
                fc = st.session_state.fact_checks.get(t)
                if fc is None:
                    dot, label = "dot-grey",   t
                elif fc.get("verified"):
                    dot, label = "dot-green",  f"✓ {t}"
                else:
                    dot, label = "dot-yellow", f"⚠ {t}"
                badge_html += (
                    f'<span class="theme-badge">'
                    f'<span class="badge-dot {dot}"></span>{label}</span>'
                )
            badge_html += "</div>"
            st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("**Suggested Conversation Starters**")

        for idx, starter in enumerate(gen.get("starters", [])):
            st.markdown(f"""
            <div class="starter-card">
                <div class="starter-num">Starter {idx + 1}</div>
                <div class="starter-text">"{starter}"</div>
            </div>""", unsafe_allow_html=True)

            fb_like, fb_dis, fb_cmt = st.columns([0.9, 1.1, 5])
            with fb_like:
                if st.button("👍", key=f"like_{gen['id']}_{idx}", help="Mark as useful"):
                    if api_healthy:
                        try:
                            requests.post(f"{BACKEND_URL}/api/feedback",
                                json={"id": gen["id"], "starter_index": idx,
                                      "rating": "thumbs_up", "comment": ""})
                            st.toast("Feedback saved!", icon="👍")
                            refresh_history()
                        except Exception:
                            pass
            with fb_dis:
                if st.button("👎", key=f"dis_{gen['id']}_{idx}", help="Mark as not useful"):
                    if api_healthy:
                        try:
                            requests.post(f"{BACKEND_URL}/api/feedback",
                                json={"id": gen["id"], "starter_index": idx,
                                      "rating": "thumbs_down", "comment": ""})
                            st.toast("Feedback saved!", icon="👎")
                            refresh_history()
                        except Exception:
                            pass
            with fb_cmt:
                with st.expander("Add a note"):
                    note = st.text_input("Note", key=f"note_{gen['id']}_{idx}",
                                         label_visibility="collapsed",
                                         placeholder="Optional feedback comment…")
                    if st.button("Submit", key=f"note_sub_{gen['id']}_{idx}"):
                        if note.strip() and api_healthy:
                            try:
                                requests.post(f"{BACKEND_URL}/api/feedback",
                                    json={"id": gen["id"], "starter_index": idx,
                                          "rating": "thumbs_up", "comment": note})
                                st.toast("Note saved!", icon="📝")
                                refresh_history()
                            except Exception:
                                pass

        # ── Wikipedia context snippets ─────────────────────────
        if st.session_state.fact_checks:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("**🔍 Live Wikipedia Context Results**")
            for theme, fc in st.session_state.fact_checks.items():
                if fc.get("verified"):
                    st.markdown(f"""
                    <div class="fact-card fact-verified">
                        <div class="fact-title-v">✓ {theme}</div>
                        <div class="fact-summary">{fc.get('summary','')}</div>
                        <a href="{fc.get('source_url','#')}" target="_blank" class="fact-link">
                            View on Wikipedia ↗
                        </a>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="fact-card fact-unverified">
                        <div class="fact-title-u">⚠ {theme} — No Wikipedia Match</div>
                        <div class="fact-summary">{fc.get('message','No details available.')}</div>
                    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  CONDITION 3 — DATA & STORAGE LAYER
    # ══════════════════════════════════════════════════════════
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon icon-teal">💾</div>
            <div>
                <div class="section-title">System Data & Storage Layer</div>
                <div class="section-desc">Persistent profile database and interaction audit trail</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_profiles, tab_audit = st.tabs(["📋  Logged User Profiles", "📊  Interaction Audit Logs"])

    # ── TAB 1 : Logged User Profiles ──────────────────────────
    with tab_profiles:
        if not st.session_state.local_history:
            st.info("No profile records yet. Generate starters above to populate this table.")
        else:
            rows = []
            for entry in st.session_state.local_history:
                bio, event = split_context(entry.get("context", ""))
                rows.append({
                    "Timestamp":        entry.get("timestamp", "")[:19].replace("T", " "),
                    "User Bio":         (bio[:90] + "…") if len(bio) > 90 else bio,
                    "Event Context":    (event[:70] + "…") if len(event) > 70 else event,
                    "Themes":           ", ".join(entry.get("themes", [])) or "—",
                    "Relationship":     entry.get("relationship", "").capitalize(),
                    "Tone":             entry.get("tone", "").capitalize(),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── TAB 2 : Interaction Audit Logs ────────────────────────
    with tab_audit:
        if not st.session_state.local_history:
            st.info("No audit data yet. Complete a generation session to see logs here.")
        else:
            # ── Aggregate metrics row
            total_gen  = len(st.session_state.local_history)
            total_fb   = sum(len(e.get("feedbacks", [])) for e in st.session_state.local_history)
            total_like = sum(
                sum(1 for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_up")
                for e in st.session_state.local_history)
            total_dis  = sum(
                sum(1 for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_down")
                for e in st.session_state.local_history)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("API Requests",      total_gen)
            m2.metric("Total Feedbacks",   total_fb)
            m3.metric("👍 Likes",           total_like)
            m4.metric("👎 Dislikes",        total_dis)

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

            # ── Full audit table
            audit_rows = []
            for entry in st.session_state.local_history:
                for s_idx, starter in enumerate(entry.get("starters", [])):
                    fbs = [f for f in entry.get("feedbacks", []) if f.get("starter_index") == s_idx]
                    rating_str  = ", ".join("👍" if f["rating"] == "thumbs_up" else "👎" for f in fbs) or "—"
                    comment_str = " | ".join(f["comment"] for f in fbs if f.get("comment")) or "—"
                    audit_rows.append({
                        "Timestamp":        entry.get("timestamp", "")[:19].replace("T", " "),
                        "Relationship":     entry.get("relationship", "").capitalize(),
                        "Tone":             entry.get("tone", "").capitalize(),
                        "Starter (preview)":(starter[:75] + "…") if len(starter) > 75 else starter,
                        "Rating":           rating_str,
                        "Auditor Notes":    comment_str,
                        "Transaction ID":   entry.get("id", ""),
                    })

            df_audit = pd.DataFrame(audit_rows)
            st.dataframe(df_audit, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            dl_col, _ = st.columns([1.4, 4])
            with dl_col:
                csv_bytes = df_audit.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇  Download CSV Log",
                    data=csv_bytes,
                    file_name=f"audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            col_refresh, _ = st.columns([1.4, 4])
            with col_refresh:
                if st.button("↺  Refresh Logs", use_container_width=True):
                    refresh_history()
                    st.toast("Audit logs refreshed!", icon="🔄")


# ─────────────────────────────────────────────────────────────
#  WORKSPACE 2 · USER PROFILES & BIO MANAGEMENT
# ─────────────────────────────────────────────────────────────
elif ws == "👤 User Profiles & Bio Management":

    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon icon-violet">👤</div>
            <div>
                <div class="section-title">User Profiles & Bio Management</div>
                <div class="section-desc">Browse, search, and restore previously saved professional profiles</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.local_history:
        st.info("No profiles stored yet. Head to **AI Generation Hub** and run your first generation.")
    else:
        search = st.text_input("🔍  Filter profiles by keyword", placeholder="E.g. Google, Kubernetes, Alice…")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        for idx, entry in enumerate(st.session_state.local_history):
            bio, event  = split_context(entry["context"])
            themes_str  = ", ".join(entry.get("themes", [])) or "None"
            created     = entry.get("timestamp", "")[:19].replace("T", " ")

            if search.strip() and all(
                search.lower() not in t.lower()
                for t in [bio, event, themes_str]
            ):
                continue

            with st.container():
                st.markdown(f"""
                <div style="background:#1E1E24;border:1px solid #2A2A35;border-radius:12px;
                            padding:1.1rem 1.3rem;margin-bottom:0.85rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
                        <strong style="color:#A78BFA;font-size:0.92rem;">
                            Profile #{idx + 1} &nbsp;·&nbsp; {entry['relationship'].capitalize()}
                        </strong>
                        <span style="font-size:0.71rem;color:#475569;">{created}</span>
                    </div>
                    <div style="font-size:0.85rem;margin-bottom:0.35rem;">
                        <span style="color:#64748B;font-weight:600;">Bio:</span>&nbsp; {bio[:200]}
                    </div>
                    <div style="font-size:0.85rem;margin-bottom:0.35rem;">
                        <span style="color:#64748B;font-weight:600;">Event:</span>&nbsp; {event[:160] if event else '—'}
                    </div>
                    <div style="font-size:0.78rem;color:#475569;">
                        <span style="font-weight:600;">Themes:</span>&nbsp; {themes_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                load_col, _ = st.columns([1.5, 5])
                with load_col:
                    if st.button("Load into Hub", key=f"load_{entry['id']}", use_container_width=True):
                        st.session_state.profile_bio       = bio
                        st.session_state.event_description = event
                        st.session_state.workspace         = "🤖 AI Generation Hub"
                        st.toast("Profile restored — switched to AI Generation Hub.", icon="👤")
                        st.rerun()


# ─────────────────────────────────────────────────────────────
#  WORKSPACE 3 · INTERACTION LOGS & AUDITING
# ─────────────────────────────────────────────────────────────
elif ws == "📊 Interaction Logs & Auditing":

    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon icon-teal">📊</div>
            <div>
                <div class="section-title">Interaction Logs & Auditing</div>
                <div class="section-desc">Full system metrics, feedback analysis, and exportable audit trails</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.local_history:
        st.info("No audit data captured yet. Run a generation session to populate the logs.")
    else:
        total_gen  = len(st.session_state.local_history)
        total_fb   = sum(len(e.get("feedbacks", [])) for e in st.session_state.local_history)
        total_like = sum(
            sum(1 for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_up")
            for e in st.session_state.local_history)
        total_dis  = sum(
            sum(1 for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_down")
            for e in st.session_state.local_history)

        st.markdown("#### 📈 System Metrics Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total API Requests", total_gen)
        c2.metric("Total Feedbacks",    total_fb)
        c3.metric("👍 Likes",            total_like)
        c4.metric("👎 Dislikes",         total_dis)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("#### 📜 Complete Audit Trail")

        audit_rows = []
        for entry in st.session_state.local_history:
            for s_idx, starter in enumerate(entry.get("starters", [])):
                fbs = [f for f in entry.get("feedbacks", []) if f.get("starter_index") == s_idx]
                rating_str  = ", ".join("👍" if f["rating"] == "thumbs_up" else "👎" for f in fbs) or "—"
                comment_str = " | ".join(f["comment"] for f in fbs if f.get("comment")) or "—"
                audit_rows.append({
                    "Timestamp":         entry.get("timestamp", "")[:19].replace("T", " "),
                    "Relationship":      entry.get("relationship", "").capitalize(),
                    "Tone":              entry.get("tone", "").capitalize(),
                    "Starter (preview)": (starter[:75] + "…") if len(starter) > 75 else starter,
                    "Rating":            rating_str,
                    "Auditor Notes":     comment_str,
                    "Transaction ID":    entry.get("id", ""),
                })

        df_full = pd.DataFrame(audit_rows)
        st.dataframe(df_full, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        dl_c, ref_c, _ = st.columns([1.4, 1.4, 3])
        with dl_c:
            st.download_button(
                "⬇  Download CSV Log",
                data=df_full.to_csv(index=False).encode("utf-8"),
                file_name=f"audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with ref_c:
            if st.button("↺  Refresh", use_container_width=True):
                refresh_history()
                st.toast("Logs refreshed!", icon="🔄")
