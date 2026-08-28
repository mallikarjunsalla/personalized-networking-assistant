import datetime as dt
import html
import re
from typing import Any

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="NetworkAI — Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://localhost:8000"

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
DEFAULTS = {
    "logged_in": False,
    "user_email": "",
    "workspace": "Generate Starters",
    "theme": "dark",
    "interests_input": "",
    "event_input": "",
    "goal_input": "",
    "person_input": "",
    "relationship_input": "Colleague",
    "tone_input": "Professional",
    "current_generation": None,
    "fact_result": None,
    "history": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------------------------------------------------------
# Theme
# -----------------------------------------------------------------------------
DARK = {
    "bg": "#0B1020",
    "sidebar": "#101625",
    "surface": "#151C2B",
    "surface2": "#1B2436",
    "surface3": "#222D42",
    "text": "#F7F9FC",
    "muted": "#9AA7BC",
    "border": "#2B3850",
    "accent": "#7257F5",
    "accent_hover": "#836CF7",
    "accent_soft": "rgba(114,87,245,.12)",
    "success": "#35D39A",
    "warning": "#F4BE4E",
    "danger": "#F06B6B",
}
LIGHT = {
    "bg": "#F4F7FB",
    "sidebar": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface2": "#F8FAFD",
    "surface3": "#EEF2F8",
    "text": "#172033",
    "muted": "#667085",
    "border": "#D9E1EC",
    "accent": "#5B4BDB",
    "accent_hover": "#4E3EC6",
    "accent_soft": "rgba(91,75,219,.08)",
    "success": "#128A68",
    "warning": "#9A6700",
    "danger": "#C83E3E",
}
THEME = DARK if st.session_state.theme == "dark" else LIGHT


def css():
    t = THEME
    return f"""
<style>
:root {{
  --bg:{t['bg']}; --sidebar:{t['sidebar']}; --surface:{t['surface']}; --surface2:{t['surface2']};
  --surface3:{t['surface3']}; --text:{t['text']}; --muted:{t['muted']}; --border:{t['border']};
  --accent:{t['accent']}; --accent-hover:{t['accent_hover']}; --accent-soft:{t['accent_soft']};
  --success:{t['success']}; --warning:{t['warning']}; --danger:{t['danger']};
}}
html, body, [class*="css"], .stApp {{ font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important; }}
.stApp {{ background:var(--bg) !important; color:var(--text) !important; }}
header[data-testid="stHeader"] {{
  display:block !important;
  background:transparent !important;
  height:2.35rem !important;
}}
header[data-testid="stHeader"] button[aria-label="Collapse sidebar"],
header[data-testid="stHeader"] button[aria-label="Expand sidebar"] {{
  width:34px !important;
  height:34px !important;
  border-radius:9px !important;
  background:var(--surface) !important;
  border:1px solid var(--border) !important;
  color:var(--text) !important;
  box-shadow:0 4px 12px rgba(15,23,42,.08) !important;
  margin-left:8px !important;
  position:relative !important;
}}
header[data-testid="stHeader"] button[aria-label="Collapse sidebar"] svg,
header[data-testid="stHeader"] button[aria-label="Expand sidebar"] svg {{
  display:none !important;
}}
header[data-testid="stHeader"] button[aria-label="Collapse sidebar"]::after,
header[data-testid="stHeader"] button[aria-label="Expand sidebar"]::after {{
  content:"≪" !important;
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  width:100% !important;
  height:100% !important;
  font-size:1.05rem !important;
  font-weight:900 !important;
  line-height:1 !important;
}}

.stAppDeployButton, .viewerBadge_container__r5tak {{ display:none !important; }}
.block-container {{ max-width:1450px !important; padding:0.8rem 2rem 4rem !important; }}

/* Fixed app header */
.topbar-wrap {{ position:sticky; top:0; z-index:1000; padding:0.25rem 0 0.7rem; background:var(--bg); }}
.topbar {{ min-height:64px; display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.7rem 1rem;
  background:var(--surface); border:1px solid var(--border); border-radius:15px; box-shadow:0 10px 28px rgba(15,23,42,.10); }}
.top-left, .top-center, .top-right {{ display:flex; align-items:center; }}
.top-left {{ gap:.7rem; min-width:270px; }}
.top-center {{ flex:1; justify-content:center; text-align:center; }}
.top-right {{ gap:.55rem; min-width:310px; justify-content:flex-end; }}
.brand-mark {{ width:39px;height:39px;border-radius:11px;background:linear-gradient(135deg,var(--accent),#8a76ff);display:flex;align-items:center;justify-content:center;color:#fff;font-size:1rem; }}
.brand-name {{ color:var(--text);font-size:1rem;font-weight:850;line-height:1.1; }}
.brand-sub {{ color:var(--muted);font-size:.69rem;margin-top:.18rem; }}
.workspace-label {{ color:var(--muted);font-size:.62rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase; }}
.workspace-name {{ color:var(--text);font-size:.92rem;font-weight:800;margin-top:.14rem; }}
.pill {{ display:flex;align-items:center;gap:.4rem;padding:.45rem .72rem;border-radius:999px;background:var(--surface2);border:1px solid var(--border);color:var(--text);font-size:.73rem;font-weight:750;white-space:nowrap; }}
.dot {{ width:8px;height:8px;border-radius:50%;background:var(--success); }}
.dot.off {{ background:var(--danger); }}
.avatar {{ width:35px;height:35px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#8975ff);color:#fff;display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:850; }}
.user-name {{ font-size:.79rem;font-weight:800;color:var(--text); }}
.user-email {{ font-size:.65rem;color:var(--muted);margin-top:.08rem;max-width:145px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }}

/* Login page */
.login-page {{ max-width:720px; margin:2.8rem auto 1.5rem; text-align:center; }}
.login-card {{ background:var(--surface); border:1px solid var(--border); border-radius:18px; padding:2rem; box-shadow:0 12px 32px rgba(15,23,42,.08); }}
.login-icon {{ width:58px; height:58px; margin:0 auto .8rem; border-radius:16px; background:var(--accent-soft); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; font-size:1.55rem; }}
.login-kicker {{ color:var(--accent); font-size:.66rem; font-weight:900; letter-spacing:.14em; text-transform:uppercase; }}
.login-title-main {{ color:var(--text); font-size:1.85rem; font-weight:900; margin:.35rem 0 .45rem; }}
.login-sub-main {{ color:var(--muted); font-size:.82rem; line-height:1.5; max-width:500px; margin:0 auto 1rem; }}
.login-note {{ color:var(--muted); font-size:.68rem; margin-top:.75rem; }}

/* Pre-login dashboard */
.prelogin {{ max-width:980px; margin:2.2rem auto 0; }}
.prelogin-hero {{ background:var(--surface); border:1px solid var(--border); border-radius:18px; padding:2.2rem; text-align:center; box-shadow:0 10px 28px rgba(15,23,42,.06); }}
.prelogin-icon {{ width:64px;height:64px;border-radius:16px;background:var(--accent-soft);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:1.65rem;margin:0 auto .8rem; }}
.prelogin-title {{ color:var(--text);font-size:2rem;font-weight:900;line-height:1.15; }}
.prelogin-sub {{ color:var(--muted);font-size:.88rem;line-height:1.55;max-width:650px;margin:.55rem auto 0; }}
.feature-grid {{ display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem; }}
.feature-card {{ background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.05rem;text-align:left; }}
.feature-icon {{ font-size:1.1rem; }}
.feature-title {{ color:var(--text);font-weight:850;margin-top:.35rem;font-size:.84rem; }}
.feature-desc {{ color:var(--muted);font-size:.72rem;line-height:1.45;margin-top:.2rem; }}
@media (max-width: 820px) {{ .feature-grid {{ grid-template-columns:1fr; }} }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background:var(--sidebar) !important;border-right:1px solid var(--border) !important; }}
section[data-testid="stSidebar"] > div:first-child {{ padding:.8rem .85rem 1rem !important; }}
.sidebar-brand {{ display:flex;align-items:center;gap:.7rem;padding:.2rem .15rem 1rem; }}
.sidebar-title {{ color:var(--text);font-size:.98rem;font-weight:850; }}
.sidebar-sub {{ color:var(--muted);font-size:.68rem;margin-top:.15rem; }}
.sidebar-divider {{ height:1px;background:var(--border);margin:.1rem 0 1.15rem; }}
.nav-title {{ color:var(--muted);font-size:.65rem;font-weight:850;letter-spacing:.13em;text-transform:uppercase;margin:.1rem 0 .55rem; }}
.sidebar-status {{ display:flex;align-items:center;gap:.45rem;margin-top:.9rem;padding:.72rem .82rem;border:1px solid var(--border);background:var(--surface);border-radius:11px;color:var(--muted);font-size:.74rem;font-weight:700; }}

/* Buttons */
.stButton > button {{ min-height:2.65rem !important;border-radius:10px !important;background:var(--surface2) !important;border:1px solid var(--border) !important;color:var(--text) !important;font-weight:750 !important; }}
.stButton > button:hover {{ border-color:var(--accent) !important; color:var(--text) !important; }}
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {{ background:var(--accent) !important;border-color:var(--accent) !important;color:#fff !important; }}

/* Inputs */
label, .stTextInput label, .stTextArea label, .stSelectbox label {{ color:var(--text) !important;font-weight:750 !important; }}
textarea, input, [data-baseweb="select"] > div {{ background:var(--surface2) !important;color:var(--text) !important;border-color:var(--border) !important;border-radius:10px !important; }}
textarea::placeholder, input::placeholder {{ color:var(--muted) !important;opacity:1 !important; }}
[data-baseweb="select"] span {{ color:var(--text) !important; }}

/* Cards */
.panel {{ background:var(--surface);border:1px solid var(--border);border-radius:15px;padding:1.15rem; }}
.panel-title {{ color:var(--text);font-size:1rem;font-weight:850; }}
.panel-sub {{ color:var(--muted);font-size:.77rem;line-height:1.45;margin-top:.25rem; }}
.field-label {{ color:var(--text);font-size:.9rem;font-weight:800;margin-bottom:.15rem; }}
.field-help {{ color:var(--muted);font-size:.72rem;margin-bottom:.55rem;line-height:1.4; }}
.badge-required {{ color:var(--accent);font-size:.65rem;font-weight:850;margin-left:.3rem;letter-spacing:.04em;text-transform:uppercase; }}
.badge-optional {{ color:var(--muted);font-size:.65rem;font-weight:750;margin-left:.3rem;letter-spacing:.04em;text-transform:uppercase; }}
.example {{ background:var(--surface2);border:1px dashed var(--border);border-radius:12px;padding:.8rem .9rem;margin-top:.75rem; }}
.example-kicker {{ color:var(--muted);font-size:.62rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase; }}
.example-row {{ color:var(--text);font-size:.75rem;margin-top:.26rem; }}
.example-row b {{ color:var(--accent); }}
.callout {{ background:var(--accent-soft);border:1px solid var(--border);border-radius:11px;padding:.72rem .82rem;color:var(--text);font-size:.75rem;line-height:1.45; }}

/* Results */
.result-card {{ background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:0 13px 13px 0;padding:1rem 1.05rem; }}
.result-label {{ color:var(--accent);font-size:.64rem;font-weight:900;letter-spacing:.12em;text-transform:uppercase; }}
.result-text {{ color:var(--text);font-size:.96rem;line-height:1.58;margin-top:.42rem; }}
.result-meta {{ color:var(--muted);font-size:.68rem;margin-top:.55rem; }}
.empty {{ background:var(--surface);border:1px dashed var(--border);border-radius:15px;padding:3.1rem 1.4rem;text-align:center; }}
.empty-icon {{ font-size:2rem; }}
.empty-title {{ color:var(--text);font-size:1.05rem;font-weight:850;margin-top:.3rem; }}
.empty-text {{ color:var(--muted);font-size:.78rem;line-height:1.5;max-width:520px;margin:.3rem auto 0; }}

/* Tables */
[data-testid="stMetric"] {{ background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:.75rem; }}
[data-testid="stMetricLabel"] {{ color:var(--muted) !important; }}
[data-testid="stMetricValue"] {{ color:var(--text) !important; }}
[data-testid="stDataFrame"] {{ border:1px solid var(--border);border-radius:12px;overflow:hidden; }}
hr {{ border-color:var(--border) !important; }}

@media (max-width: 900px) {{
  .top-center {{ display:none; }} .top-left,.top-right {{ min-width:auto; }}
  .block-container {{ padding-left:1rem !important;padding-right:1rem !important; }}
}}
</style>
"""


st.markdown(css(), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def safe_text(v: Any) -> str:
    return str(v or "").strip()


def initials(email: str) -> str:
    local = email.split("@", 1)[0] if "@" in email else email
    parts = [p for p in re.split(r"[._\-\s]+", local) if p]
    return "".join(x[0].upper() for x in parts[:2]) or "U"


def display_name(email: str) -> str:
    local = email.split("@", 1)[0].strip()
    parts = [p for p in re.split(r"[._\-\s]+", local) if p]
    return " ".join(p.capitalize() for p in parts) or "User"


def api_health() -> bool:
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=1.5).status_code == 200
    except requests.RequestException:
        return False


def refresh_history() -> None:
    if not api_health() or not st.session_state.user_email:
        return
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history",
            params={"user_email": st.session_state.user_email.strip().lower()},
            timeout=5,
        )
        if response.status_code == 200:
            st.session_state.history = response.json()
    except requests.RequestException:
        pass


def parse_legacy_context(context: str) -> dict[str, str]:
    text = safe_text(context)
    result = {"interests": "", "event": "", "goal": "", "person": ""}
    patterns = {
        "interests": r"(?:USER INTERESTS|Interests):\s*(.*?)(?=\n(?:EVENT|Event|NETWORKING GOAL|Networking Goal|PERSON CONTEXT|Person):|$)",
        "event": r"(?:EVENT|Event|Event Details):\s*(.*?)(?=\n(?:NETWORKING GOAL|Networking Goal|PERSON CONTEXT|Person):|$)",
        "goal": r"(?:NETWORKING GOAL|Networking Goal):\s*(.*?)(?=\n(?:PERSON CONTEXT|Person):|$)",
        "person": r"(?:PERSON CONTEXT|Person):\s*(.*)$",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, flags=re.I | re.S)
        if m:
            result[key] = safe_text(m.group(1))
    if not any(result.values()) and text:
        # Very old records: Profile Bio + Event Details.
        m = re.search(r"Profile Bio:\s*(.*?)\s*Event Details:\s*(.*)$", text, flags=re.I | re.S)
        if m:
            result["interests"] = safe_text(m.group(1))
            result["event"] = safe_text(m.group(2))
    return result


EXAMPLE = {
    "interests_input": "AI, cybersecurity",
    "event_input": "AI for Sustainable Cities",
    "goal_input": "Learn about real-world AI projects",
    "person_input": "Senior AI engineer working on responsible AI",
}


def apply_example() -> None:
    """Populate widget-backed inputs from a button callback.

    Streamlit callbacks run before the next script rerun, which makes it safe
    to update widget keys here. Updating those keys later in the same run
    after the widgets have been instantiated raises StreamlitAPIException.
    """
    for key, value in EXAMPLE.items():
        st.session_state[key] = value
    st.session_state.current_generation = None


def apply_saved_setup(parsed: dict[str, str]) -> None:
    """Restore saved widget values from a button callback."""
    st.session_state.interests_input = parsed.get("interests", "")
    st.session_state.event_input = parsed.get("event", "")
    st.session_state.goal_input = parsed.get("goal", "")
    st.session_state.person_input = parsed.get("person", "")
    st.session_state.current_generation = None
    st.session_state.workspace = "Generate Starters"


# -----------------------------------------------------------------------------
# Sidebar + topbar
# -----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="brand-mark">🤝</div><div><div class="sidebar-title">NetworkAI</div><div class="sidebar-sub">Personalized networking workspace</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if not st.session_state.logged_in:
            st.markdown('<div class="nav-title">Sign in</div>', unsafe_allow_html=True)
            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="login_password",
            )
            if st.button(
                "Sign in to NetworkAI",
                type="primary",
                use_container_width=True,
                key="login_submit",
            ):
                if email.strip() and password.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_email = email.strip()
                    st.session_state.workspace = "Generate Starters"
                    refresh_history()
                    st.rerun()
                else:
                    st.error("Enter both email and password.")
            st.caption("Demo login: use any non-empty email and password.")
            return

        st.markdown('<div class="nav-title">Navigation</div>', unsafe_allow_html=True)
        items = [
            ("Generate Starters", "🤖"),
            ("Fact Check", "🔎"),
            ("Saved Profiles", "👤"),
            ("History & Feedback", "📜"),
        ]
        for name, icon in items:
            active = st.session_state.workspace == name
            if st.button(
                f"{'● ' if active else ''}{icon}  {name}",
                key=f"nav_{name}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.workspace = name
                st.rerun()

        healthy = api_health()
        label = "AI Ready" if healthy else "API Offline"
        color = THEME["success"] if healthy else THEME["danger"]
        st.markdown(
            f'<div class="sidebar-status"><span style="width:8px;height:8px;border-radius:50%;background:{color};display:inline-block"></span>{label}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        toggle = "☀️  Light mode" if st.session_state.theme == "dark" else "🌙  Dark mode"
        if st.button(toggle, use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

        if st.button("↩  Sign out", use_container_width=True, key="logout"):
            for key, value in DEFAULTS.items():
                st.session_state[key] = value
            st.rerun()


def render_topbar(healthy: bool) -> None:
    workspace = html.escape(st.session_state.workspace)
    status = "AI Ready" if healthy else "API Offline"
    status_class = "" if healthy else "off"
    name = html.escape(display_name(st.session_state.user_email))
    email = html.escape(st.session_state.user_email)
    ini = html.escape(initials(st.session_state.user_email))
    st.markdown(
        f'''
<div class="topbar-wrap">
  <div class="topbar">
    <div class="top-left">
      <div class="brand-mark">🤝</div>
      <div><div class="brand-name">NetworkAI</div><div class="brand-sub">Personalized Networking Assistant</div></div>
    </div>
    <div class="top-center"><div><div class="workspace-label">Current workspace</div><div class="workspace-name">{workspace}</div></div></div>
    <div class="top-right">
      <div class="pill"><span class="dot {status_class}"></span>{status}</div>
      <div class="avatar">{ini}</div>
      <div><div class="user-name">{name}</div><div class="user-email">{email}</div></div>
    </div>
  </div>
</div>
''',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Generate page
# -----------------------------------------------------------------------------
def generate_request() -> None:
    healthy = api_health()
    if not healthy:
        st.error("The FastAPI backend is offline. Start it on port 8000.")
        return

    interests = safe_text(st.session_state.interests_input)
    event = safe_text(st.session_state.event_input)
    goal = safe_text(st.session_state.goal_input)
    person = safe_text(st.session_state.person_input)

    if not interests or not event:
        st.warning("Your interests and event description are required.")
        return

    payload = {
        "interests": interests,
        "event_description": event,
        "networking_goal": goal,
        "person_context": person,
        "user_email": st.session_state.user_email,
        "relationship": st.session_state.relationship_input.lower(),
        "tone": st.session_state.tone_input.lower(),
    }

    with st.spinner("Preparing relevant conversation starters..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/generate", json=payload, timeout=45)
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")
            return

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        st.error(f"Generation failed: {detail}")
        return

    data = response.json()
    st.session_state.current_generation = data
    refresh_history()
    st.toast("Relevant starters are ready.", icon="✨")


def render_generate() -> None:
    st.markdown("# Generate conversation starters")
    st.markdown(
        '<div class="panel-sub" style="font-size:.88rem;margin-top:-.45rem;margin-bottom:1.1rem;">'
        "Prepare a natural opening you can say to another person at a professional or tech event. "
        "Event + interests are the core inputs; the other fields add optional personalization."
        "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Your context</div>', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Your interests <span class="badge-required">Required</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-help">Topics you genuinely want to discuss.</div>', unsafe_allow_html=True)
            st.text_area(
                "Interests",
                key="interests_input",
                placeholder="AI, cybersecurity, cloud computing",
                height=110,
                label_visibility="collapsed",
            )

            st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Networking goal <span class="badge-optional">Optional</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-help">What would make the conversation useful for you?</div>', unsafe_allow_html=True)
            st.text_input(
                "Goal",
                key="goal_input",
                placeholder="Learn about real-world projects / find a collaborator",
                label_visibility="collapsed",
            )

            st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Relationship <span class="badge-optional">Optional</span></div>', unsafe_allow_html=True)
            st.selectbox("Relationship", ["Colleague", "Mentor", "Client", "Recruiter"], key="relationship_input", label_visibility="collapsed")
            st.selectbox("Tone", ["Professional", "Warm", "Casual"], key="tone_input", label_visibility="collapsed")

    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Event & person context</div>', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Event description <span class="badge-required">Required</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-help">Give the AI the event, conference, topic, or session context.</div>', unsafe_allow_html=True)
            st.text_area(
                "Event",
                key="event_input",
                placeholder="AI for Sustainable Cities — a conference on AI and urban innovation.",
                height=110,
                label_visibility="collapsed",
            )

            st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Person you want to meet <span class="badge-optional">Optional</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="field-help">Use this when you know something about the person. Do not add private/sensitive information.</div>', unsafe_allow_html=True)
            st.text_area(
                "Person",
                key="person_input",
                placeholder="Senior AI engineer working on responsible AI.",
                height=92,
                label_visibility="collapsed",
            )

            st.markdown(
                '<div class="callout" style="margin-top:.65rem;">'
                "These starters are designed to be <b>spoken naturally</b> at the event — not copied into LinkedIn."
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="example"><div class="example-kicker">Simple example</div>'
        '<div class="example-row"><b>Interests:</b> AI, cybersecurity</div>'
        '<div class="example-row"><b>Event:</b> AI for Sustainable Cities</div>'
        '<div class="example-row"><b>Goal:</b> Learn about real-world AI projects</div>'
        '<div class="example-row"><b>Person:</b> Senior AI engineer working on responsible AI</div></div>',
        unsafe_allow_html=True,
    )

    e1, e2, _ = st.columns([1.1, 1.55, 3])
    with e1:
        st.button(
            "✨ Try this example",
            use_container_width=True,
            key="try_example",
            on_click=apply_example,
        )
    with e2:
        if st.button("✨ Generate 2–3 conversation starters", type="primary", use_container_width=True, key="generate"):
            generate_request()

    st.markdown("<div style='height:1.15rem'></div>", unsafe_allow_html=True)

    generation = st.session_state.current_generation
    if not generation:
        st.markdown(
            '<div class="empty"><div class="empty-icon">💬</div><div class="empty-title">Ready when you are</div>'
            '<div class="empty-text">Add your interests and event, then generate short, open-ended starters grounded in the information you provided.</div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown("## Your conversation starters")
    themes = [safe_text(x) for x in generation.get("themes", []) if safe_text(x)]
    if themes:
        tags = " · ".join(html.escape(x) for x in themes[:7])
        st.markdown(f'<div class="field-help" style="margin-bottom:.75rem;">Relevant themes: {tags}</div>', unsafe_allow_html=True)

    starters = generation.get("starters", [])[:3]
    for idx, starter in enumerate(starters):
        st.markdown(
            f'<div class="result-card"><div class="result-label">Opening {idx + 1}</div>'
            f'<div class="result-text">“{html.escape(safe_text(starter))}”</div>'
            '<div class="result-meta">Speak naturally · Open-ended · Relevant to the event</div></div>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1.0, 1.1, 3.3])
        gen_id = generation.get("id")
        with c1:
            if st.button("👍 Useful", key=f"useful_{gen_id}_{idx}", use_container_width=True):
                submit_feedback(gen_id, idx, "thumbs_up")
        with c2:
            if st.button("👎 Not useful", key=f"notuseful_{gen_id}_{idx}", use_container_width=True):
                submit_feedback(gen_id, idx, "thumbs_down")
        with c3:
            with st.expander("Add a note", expanded=False):
                note = st.text_input("Feedback note", key=f"note_{gen_id}_{idx}", placeholder="What should be improved?", label_visibility="collapsed")
                if st.button("Save note", key=f"save_note_{gen_id}_{idx}") and note.strip():
                    submit_feedback(gen_id, idx, "thumbs_up", note.strip())
        st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)


def submit_feedback(gen_id: str, idx: int, rating: str, comment: str = "") -> None:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/feedback",
            json={
                "id": gen_id,
                "starter_index": idx,
                "rating": rating,
                "comment": comment,
                "user_email": st.session_state.user_email,
            },
            timeout=5,
        )
        if response.status_code == 200:
            st.toast("Feedback saved.", icon="✅")
            refresh_history()
        else:
            st.warning("Could not save feedback.")
    except requests.RequestException:
        st.warning("Could not reach the feedback service.")


# -----------------------------------------------------------------------------
# Fact check
# -----------------------------------------------------------------------------
def render_fact_check() -> None:
    st.markdown("# Quick fact check")
    st.markdown(
        '<div class="panel-sub" style="font-size:.88rem;margin-top:-.45rem;margin-bottom:1.1rem;">'
        "Look up a technology, company, concept, or person before using it in a conversation. "
        "Wikipedia provides a quick reference, not authoritative proof of every claim."
        "</div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        query = st.text_input("Topic", value="", placeholder="e.g. blockchain in healthcare", key="fact_query")
        if st.button("🔎 Verify topic", type="primary", key="verify"):
            if not query.strip():
                st.warning("Enter a topic first.")
            elif not api_health():
                st.error("The FastAPI backend is offline.")
            else:
                try:
                    response = requests.get(f"{BACKEND_URL}/api/factcheck", params={"query": query.strip()}, timeout=12)
                    if response.status_code == 200:
                        st.session_state.fact_result = response.json()
                    else:
                        st.error("Fact check failed.")
                except requests.RequestException as exc:
                    st.error(f"Could not reach the fact-check service: {exc}")

    result = st.session_state.fact_result
    if not result:
        st.markdown('<div class="empty"><div class="empty-icon">🔎</div><div class="empty-title">Nothing checked yet</div><div class="empty-text">Search a topic to get a quick Wikipedia-backed reference.</div></div>', unsafe_allow_html=True)
        return

    verified = bool(result.get("verified"))
    title = safe_text(result.get("title")) or "No matching article"
    summary = safe_text(result.get("summary")) or safe_text(result.get("message"))
    source = safe_text(result.get("source_url"))
    icon = "✅" if verified else "⚠️"
    st.markdown(
        f'<div class="result-card" style="border-left-color:{THEME["success"] if verified else THEME["warning"]};">'
        f'<div class="result-label">{icon} {"Reference found" if verified else "No exact match"}</div>'
        f'<div class="panel-title" style="margin-top:.35rem;">{html.escape(title)}</div>'
        f'<div class="result-text" style="font-size:.88rem;">{html.escape(summary)}</div>'
        f'{f"<div style=\'margin-top:.65rem;\'><a href=\'{html.escape(source)}\' target=\'_blank\'>Open Wikipedia source ↗</a></div>" if source else ""}'
        '</div>',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Saved profiles
# -----------------------------------------------------------------------------
def render_saved_profiles() -> None:
    st.markdown("# Saved profiles")
    st.markdown('<div class="panel-sub" style="font-size:.88rem;margin-top:-.45rem;margin-bottom:1rem;">Reuse a previous networking setup without re-entering the same context.</div>', unsafe_allow_html=True)
    refresh_history()
    history = st.session_state.history or []
    search = st.text_input("Search", placeholder="Search by interest, event, goal, or person...", key="profile_search")

    if not history:
        st.markdown('<div class="empty"><div class="empty-icon">👤</div><div class="empty-title">No saved profiles yet</div><div class="empty-text">Generate your first conversation set and the setup will appear here.</div></div>', unsafe_allow_html=True)
        return

    displayed = 0
    for index, entry in enumerate(history):
        parsed = {
            "interests": safe_text(entry.get("interests")),
            "event": safe_text(entry.get("event_description")),
            "goal": safe_text(entry.get("networking_goal")),
            "person": safe_text(entry.get("person_context")),
        }
        if not any(parsed.values()):
            parsed = parse_legacy_context(entry.get("context", ""))
        searchable = " ".join(parsed.values()).lower()
        if search.strip() and search.strip().lower() not in searchable:
            continue
        displayed += 1

        timestamp = safe_text(entry.get("timestamp"))[:19].replace("T", " ")
        with st.container(border=True):
            top = st.columns([4, 1])
            with top[0]:
                st.markdown(f'<div class="panel-title">Networking session {index + 1}</div>', unsafe_allow_html=True)
            with top[1]:
                st.markdown(f'<div class="field-help" style="text-align:right;">{html.escape(timestamp)}</div>', unsafe_allow_html=True)

            a, b = st.columns(2)
            with a:
                st.markdown(f'<div class="field-help"><b>Interests</b><br>{html.escape(parsed["interests"] or "—")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-help"><b>Goal</b><br>{html.escape(parsed["goal"] or "—")}</div>', unsafe_allow_html=True)
            with b:
                st.markdown(f'<div class="field-help"><b>Event</b><br>{html.escape(parsed["event"] or "—")}</div>', unsafe_allow_html=True)
                if parsed["person"]:
                    st.markdown(f'<div class="field-help"><b>Person</b><br>{html.escape(parsed["person"])}</div>', unsafe_allow_html=True)

            st.button(
                "Use this setup",
                key=f"use_profile_{index}",
                use_container_width=False,
                on_click=apply_saved_setup,
                args=(parsed,),
            )

    if displayed == 0:
        st.info("No saved profile matches that search.")


# -----------------------------------------------------------------------------
# History & feedback
# -----------------------------------------------------------------------------
def render_history() -> None:
    st.markdown("# History & feedback")
    st.markdown('<div class="panel-sub" style="font-size:.88rem;margin-top:-.45rem;margin-bottom:1rem;">Review your previous generated starters and which ones you marked useful.</div>', unsafe_allow_html=True)
    refresh_history()
    history = st.session_state.history or []

    if not history:
        st.markdown('<div class="empty"><div class="empty-icon">📜</div><div class="empty-title">No history yet</div><div class="empty-text">Your generated conversations and feedback will appear here.</div></div>', unsafe_allow_html=True)
        return

    total_gen = len(history)
    total_fb = sum(len(e.get("feedbacks", [])) for e in history)
    useful = sum(1 for e in history for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_up")
    not_useful = sum(1 for e in history for f in e.get("feedbacks", []) if f.get("rating") == "thumbs_down")

    a, b, c, d = st.columns(4)
    a.metric("Generations", total_gen)
    b.metric("Feedback", total_fb)
    c.metric("Useful", useful)
    d.metric("Not useful", not_useful)

    rows = []
    for entry in history:
        parsed = {
            "event": safe_text(entry.get("event_description")),
        }
        if not parsed["event"]:
            parsed = parse_legacy_context(entry.get("context", ""))
        starters = entry.get("starters", [])
        for idx, starter in enumerate(starters):
            fbs = [f for f in entry.get("feedbacks", []) if f.get("starter_index") == idx]
            rows.append(
                {
                    "Time": safe_text(entry.get("timestamp"))[:19].replace("T", " "),
                    "Event": parsed.get("event", "—"),
                    "Starter": safe_text(starter),
                    "Rating": " ".join("👍" if f.get("rating") == "thumbs_up" else "👎" for f in fbs) or "—",
                    "Notes": " | ".join(safe_text(f.get("comment")) for f in fbs if safe_text(f.get("comment"))) or "—",
                }
            )

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇ Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"networking_history_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )



# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
render_sidebar()

if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="prelogin">
          <div class="prelogin-hero">
            <div class="prelogin-icon">🤝</div>
            <div class="prelogin-title">Personalized Networking Assistant</div>
            <div class="prelogin-sub">
              Prepare natural conversation openers for professional and technology events,
              verify topics quickly, and review the networking strategies that worked for you.
              Sign in from the left sidebar to begin.
            </div>
          </div>

          <div class="feature-grid">
            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <div class="feature-title">Generate Starters</div>
              <div class="feature-desc">Use your interests and event context to prepare 2–3 natural opening questions.</div>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🔎</div>
              <div class="feature-title">Quick Fact Check</div>
              <div class="feature-desc">Look up a topic with Wikipedia as a quick reference before or during an event.</div>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📜</div>
              <div class="feature-title">History & Feedback</div>
              <div class="feature-desc">Review past networking sessions and see which starters you found useful.</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

healthy = api_health()
render_topbar(healthy)

if st.session_state.workspace == "Generate Starters":
    render_generate()
elif st.session_state.workspace == "Fact Check":
    render_fact_check()
elif st.session_state.workspace == "Saved Profiles":
    render_saved_profiles()
else:
    render_history()
