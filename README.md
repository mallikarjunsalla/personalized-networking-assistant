# 🤝 Personalized Networking Assistant

An AI-powered web application that helps users start meaningful **face-to-face conversations at professional and technology networking events**.

The assistant takes the user's interests and event context, optionally considers a networking goal and information about the person they want to meet, extracts relevant themes, and generates 2–3 short, natural conversation openers. It also provides Wikipedia-backed topic verification, saved networking sessions, and feedback tracking.

## 🎯 Project Goal

The goal is to help a user answer:

> **“I am at a professional or tech event. How can I naturally approach someone and start a meaningful conversation based on our interests and the event?”**

The generated starters are designed to be **spoken naturally at the event**, not copied and pasted into LinkedIn.

## ✨ Features

### 1. Generate Conversation Starters
- Required:
  - **Your Interests**
  - **Event Description**
- Optional:
  - **Networking Goal**
  - **Person You Want to Meet**
- Generates 2–3 event-focused conversation openers.
- Includes relevance checks to avoid generic, broken, or placeholder output.
- Supports optional GPT-2 generation with a quality-safe fallback.

### 2. Quick Fact Check
Users can enter a topic and retrieve a short reference from Wikipedia.

> Note: a matching Wikipedia article is treated as a reference, not as proof that every claim is true.

### 3. Saved Profiles
Users can review previous networking setups and restore one for another generation session.

### 4. History & Feedback
- View previous generation sessions.
- Track useful / not useful feedback.
- Add feedback comments.
- Download history as CSV.

### 5. User Experience
- Separate navigation for:
  - Generate Starters
  - Fact Check
  - Saved Profiles
  - History & Feedback
- Light and dark theme support.
- Logged-in user displayed in the top bar.
- Responsive Streamlit interface.

## 🧠 AI / Processing Flow

```text
User Interests + Event
          +
   Optional Goal
          +
 Optional Person Context
          │
          ▼
     Theme Extraction
        (DistilBERT)
          │
          ▼
 Relevant Themes / Terms
          │
          ▼
 Conversation Generation
        (GPT-2*)
          │
          ▼
   Quality / Relevance Filter
          │
          ▼
    2–3 Final Starters
```

`*` GPT-2 is optional. If GPT-2 is unavailable or its output fails the quality checks, the backend uses quality-safe templates.

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   Streamlit Frontend │
                    │      frontend/       │
                    └──────────┬───────────┘
                               │ HTTP/HTTPS
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │       backend/       │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼──────────────────┐
             ▼                 ▼                  ▼
        DistilBERT           GPT-2          Wikipedia API
      theme extraction      generation       fact checking
             │                 │
             └─────────────────┘
                       │
                       ▼
                Quality filtering
                       │
                       ▼
             Personalized starters
```

## 📁 Project Structure

```text
PersonalizedNetworkingAssistant/
│
├── backend/
│   ├── __init__.py
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

## 🔌 Backend API

The FastAPI backend provides:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Backend health check |
| `/api/generate` | POST | Generate personalized starters |
| `/api/factcheck` | GET | Verify a topic using Wikipedia |
| `/api/history` | GET | Retrieve generation history |
| `/api/feedback` | POST | Submit starter feedback |
| `/docs` | GET | FastAPI Swagger documentation |

## 📝 Generate Request

The current API supports structured inputs:

```json
{
  "interests": "AI, cybersecurity",
  "event_description": "AI for Sustainable Cities",
  "networking_goal": "Learn about real-world AI projects",
  "person_context": "Senior AI engineer working on responsible AI",
  "user_email": "user@example.com"
}
```

The backend requires **interests** and **event_description**. The other fields are optional.

## 💡 Example

### Input

**Interests**

```text
AI, cybersecurity
```

**Event**

```text
AI for Sustainable Cities
```

**Goal**

```text
Learn about real-world AI projects
```

**Person**

```text
Senior AI engineer working on responsible AI
```

### Example output

```text
“I’m interested in AI. Given your work in responsible AI,
what part of that work connects most with what’s being
discussed at AI for Sustainable Cities?”

“I’m exploring AI and cybersecurity. Which area do you
think is getting the most interesting attention at this event?”

“I’m here to learn about real-world AI projects. From your
experience, what would you recommend someone interested
in AI pay attention to at this event?”
```

The purpose is to give the user a **natural opening question** that can be spoken to another attendee.

## 💻 Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PersonalizedNetworkingAssistant
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the FastAPI backend

Run from the **project root**:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### 4. Start the Streamlit frontend

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

### Backend
The FastAPI backend can be deployed as a Python Web Service.

Example start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend
The Streamlit frontend can be deployed using the repository entrypoint:

```text
frontend/app.py
```

For cloud deployment, configure the frontend with the public backend URL instead of `localhost`.

Example:

```text
BACKEND_URL=https://your-backend-domain.example.com
```

## 🔐 Authentication

The current frontend provides a **demo/local login flow** using an email and password input.

It is intended for the project demonstration and should not be considered production-grade authentication.

## 💾 Data Storage

The current backend keeps history in an **in-memory list** during runtime.

This is suitable for a prototype/demo, but production deployment should use persistent storage such as PostgreSQL or another database.

## 🧪 Testing

Run:

```bash
pytest -v
```

The repository includes `pytest.ini` for the test configuration.

## 🛡️ Quality & Safety Checks

The backend is designed to reject poor generation output when it:
- contains placeholder labels,
- uses generic email/LinkedIn wording,
- lacks a question,
- does not connect to the supplied interests,
- does not relate to the event,
- or otherwise fails basic relevance checks.

Examples of patterns intentionally rejected include:

```text
USER INTERESTS
EVENT DESCRIPTION
PROFILE BIO
Dear Colleague
I came across your profile
Connect on LinkedIn
```

## 🚀 Why This Project Is Different

The main use case is **real-world event networking**, not generic text generation.

Instead of simply asking an LLM:

> “Write me a networking message.”

the application uses:

```text
Event context
      +
User interests
      +
Optional networking goal
      +
Optional person context
      ↓
Context-aware conversation openers
      ↓
Relevance filtering
      ↓
Feedback + history
```

This makes the assistant focused on helping users **approach people and begin meaningful conversations in person**.

## 📌 Current Limitations

- History is currently stored in memory and may reset when the backend restarts.
- Login is a demo authentication flow.
- GPT-2 is optional and may fall back to template-based generation.
- Wikipedia is used as a reference source for quick topic verification.

## 🔗 Deployment

**Frontend:** `https://personalized-networking-assistant-g7szezu7y7fga5gst4xuhr.streamlit.app/`

**Backend:** `https://personalized-networking-assistant-pdcj.onrender.com`

**Backend Health:** `https://personalized-networking-assistant-pdcj.onrender.com/health`

**API Docs:** `https://personalized-networking-assistant-pdcj.onrender.com/docs`

## 👥 Project

**Project Title:** Personalized Networking Assistant

**Technology Stack**
- Python
- FastAPI
- Streamlit
- DistilBERT
- GPT-2
- Wikipedia API
- Pytest

---

### Quick Start

```bash
# Terminal 1
cd PersonalizedNetworkingAssistant
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2
cd PersonalizedNetworkingAssistant/frontend
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```
