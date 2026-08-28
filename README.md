# 🤝 Personalized Networking Assistant

An AI-powered web application that helps users start meaningful conversations at professional and technology networking events.

The assistant uses a user's interests and event details to generate short, relevant conversation starters. Users can also verify topics with Wikipedia, reuse saved networking setups, and review feedback and history.

## 🎯 Project Goal

The goal is to help users confidently approach another person at a networking event by providing a natural opening based on:

- The user's interests
- The event context
- Optional networking goals
- Optional information about the person they want to meet

The generated starters are designed to be **spoken naturally**, not copied into LinkedIn.

## ✨ Features

### 🤖 Generate Starters
Generate 2–3 personalized conversation openers.

**Required**
- Your Interests
- Event Description

**Optional**
- Networking Goal
- Person You Want to Meet

### 🔎 Fact Check
Search for a topic and get a quick Wikipedia-based reference.

### 👤 Saved Profiles
Review previous networking setups and reuse them for a new generation.

### 📜 History & Feedback
Review previous sessions, useful/not-useful feedback, notes, and download history as CSV.

### 🎨 User Interface
- Clean Streamlit interface
- Sidebar navigation
- Logged-in user display
- Light and dark themes
- Example input for quick testing
- Responsive result cards

## 🧠 AI Workflow

```text
User Interests + Event
        +
Optional Goal
        +
Optional Person Context
        ↓
Theme Extraction
   DistilBERT*
        ↓
Relevant Themes
        ↓
Conversation Generation
      GPT-2*
        ↓
Quality & Relevance Checks
        ↓
2–3 Conversation Starters
```

`*` DistilBERT and GPT-2 availability depends on the runtime environment. The backend includes a quality-safe fallback when the model pipeline is unavailable.

## 🏗️ Architecture

```text
             Streamlit Frontend
                    │
                    │ HTTP / HTTPS
                    ▼
              FastAPI Backend
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      DistilBERT   GPT-2   Wikipedia
       Themes     Starters   Fact Check
          │         │
          └────┬────┘
               ▼
       Quality Filtering
               │
               ▼
    Personalized Starters
```

## 📁 Project Structure

```text
PersonalizedNetworkingAssistant/
│
├── backend/
│   ├── main.py
│   └── services.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Check backend status |
| `/api/generate` | POST | Generate conversation starters |
| `/api/factcheck` | GET | Search Wikipedia for a topic |
| `/api/history` | GET | Retrieve networking history |
| `/api/feedback` | POST | Save starter feedback |
| `/docs` | GET | FastAPI API documentation |

## 📝 Example

### Input

**Interests**
```text
AI, cybersecurity
```

**Event**
```text
AI for Sustainable Cities
```

**Networking Goal**
```text
Learn about real-world AI projects
```

**Person**
```text
Senior AI engineer working on responsible AI
```

### Example starters

```text
What applications of AI do you think could have the biggest
impact on sustainable cities?

How are you seeing responsible AI practices change the way
technology is being used in urban projects?

I'm interested in both AI and cybersecurity. What challenges
do you think teams should consider when deploying AI in
smart-city systems?
```

These starters are intended to help the user **begin and continue a real conversation at the event**.

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PersonalizedNetworkingAssistant
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the backend

Run from the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### 4. Start the frontend

Open a second terminal:

```bash
cd frontend
python -m streamlit run app.py
```

Frontend:

```text
http://localhost:8501
```

## 🌐 Deployment

### Frontend — Streamlit Cloud

https://personalized-networking-assistant-g7szezu7y7fga5gst4xuhr.streamlit.app/

### Backend — Render

https://personalized-networking-assistant-pdcj.onrender.com

### Backend Health

https://personalized-networking-assistant-pdcj.onrender.com/health

### API Documentation

https://personalized-networking-assistant-pdcj.onrender.com/docs

For the deployed Streamlit application, configure the backend URL as a Streamlit secret:

```toml
BACKEND_URL = "https://personalized-networking-assistant-pdcj.onrender.com"
```

## 🧪 Testing

Run:

```bash
pytest -v
```

## 🛡️ Quality Checks

The backend filters generated starters that are:
- Generic or unrelated to the event
- Missing a connection to the user's interests
- Written like an email or LinkedIn message
- Based on placeholder field names
- Missing a natural question

Examples of unwanted output include:

```text
Dear Colleague
I came across your profile
Connect on LinkedIn
USER INTERESTS
EVENT DESCRIPTION
PROFILE BIO
```

## 🔐 Authentication

The current login is a **demo authentication flow** intended for project demonstration. It is not production-grade authentication.

## 💾 Data Storage

The current backend stores history in memory during runtime. A production application would use persistent database storage.

## 📌 Limitations

- History may reset when the backend restarts.
- Login is for demonstration purposes.
- GPT-2 / DistilBERT availability depends on the deployment environment.
- Wikipedia is used as a reference source and does not independently prove every claim.

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **NLP:** DistilBERT
- **Text Generation:** GPT-2
- **Fact Checking:** Wikipedia API
- **Testing:** Pytest
- **Deployment:** Streamlit Cloud + Render

## 👥 Project

**Project Title:** Personalized Networking Assistant

The project focuses on making professional networking easier by helping users prepare relevant and natural conversation openers before meeting people at events.
