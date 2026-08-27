from datetime import datetime, timezone
import logging
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from backend.services import FactChecker, StarterGenerator, ThemeExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personalized Networking Assistant API",
    description="Backend for personalized face-to-face networking starters and Wikipedia-backed topic references.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

theme_extractor = ThemeExtractor()
starter_generator = StarterGenerator()
fact_checker = FactChecker()
history_db: list[dict] = []


class GenerateRequest(BaseModel):
    # New structured inputs.
    interests: Optional[str] = ""
    event_description: Optional[str] = ""
    networking_goal: Optional[str] = ""
    person_context: Optional[str] = ""
    user_email: Optional[str] = ""

    # Backward-compatible fields used by the earlier frontend.
    context: Optional[str] = ""
    relationship: Optional[str] = "colleague"
    tone: Optional[str] = "professional"

    @model_validator(mode="after")
    def validate_required_inputs(self):
        if not self.interests and self.context:
            import re
            match = re.search(r"USER INTERESTS:\s*(.*)", self.context, flags=re.I)
            self.interests = match.group(1).strip() if match else self.interests
        if not self.event_description and self.context:
            import re
            match = re.search(r"EVENT:\s*(.*)", self.context, flags=re.I)
            self.event_description = match.group(1).strip() if match else self.event_description
        if not self.networking_goal and self.context:
            import re
            match = re.search(r"NETWORKING GOAL:\s*(.*)", self.context, flags=re.I)
            self.networking_goal = match.group(1).strip() if match else self.networking_goal
        if not self.person_context and self.context:
            import re
            match = re.search(r"PERSON CONTEXT:\s*(.*)", self.context, flags=re.I)
            self.person_context = match.group(1).strip() if match else self.person_context
        if not (self.interests or "").strip() or not (self.event_description or "").strip():
            raise ValueError("Both interests and event_description are required.")
        return self


class GenerateResponse(BaseModel):
    id: str
    context: str
    interests: str
    event_description: str
    networking_goal: str
    person_context: str
    user_email: str
    relationship: str
    tone: str
    themes: List[str]
    starters: List[str]
    timestamp: str
    feedbacks: List[dict] = Field(default_factory=list)
    generation_source: str = "quality-safe"


class FeedbackRequest(BaseModel):
    id: str
    starter_index: int = Field(ge=0)
    rating: str
    comment: Optional[str] = ""
    user_email: Optional[str] = ""

    @model_validator(mode="after")
    def validate_rating(self):
        if self.rating not in {"thumbs_up", "thumbs_down"}:
            raise ValueError("rating must be thumbs_up or thumbs_down")
        return self


class FeedbackResponse(BaseModel):
    status: str
    message: str


class FactCheckResponse(BaseModel):
    verified: bool
    message: str
    title: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None


def _context_text(req: GenerateRequest) -> str:
    return "\n".join(
        [
            f"Interests: {req.interests.strip()}",
            f"Event: {req.event_description.strip()}",
            f"Networking Goal: {req.networking_goal.strip() if req.networking_goal else 'Make a meaningful professional connection'}",
            f"Person: {req.person_context.strip() if req.person_context else 'Not provided'}",
        ]
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_starters(payload: GenerateRequest):
    try:
        interests = (payload.interests or "").strip()
        event = (payload.event_description or "").strip()
        goal = (payload.networking_goal or "").strip()
        person = (payload.person_context or "").strip()

        # Interests are explicit themes; event/person add contextual themes.
        themes = theme_extractor.extract_themes(
            f"Event: {event}. Interests: {interests}. Person: {person}",
            preferred_terms=[x.strip() for x in interests.replace(";", ",").split(",") if x.strip()],
        )

        starters = starter_generator.generate_starters(
            context=_context_text(payload),
            themes=themes,
            relationship=(payload.relationship or "colleague").strip(),
            tone=(payload.tone or "professional").strip(),
            interests=interests,
            event=event,
            goal=goal,
            person=person,
        )

        if len(starters) < 2:
            raise RuntimeError("The generation quality filter could not produce enough relevant starters.")

        entry = {
            "id": str(uuid.uuid4()),
            "context": _context_text(payload),
            "interests": interests,
            "event_description": event,
            "networking_goal": goal,
            "person_context": person,
            "user_email": (payload.user_email or "").strip().lower(),
            "relationship": (payload.relationship or "colleague").strip().lower(),
            "tone": (payload.tone or "professional").strip().lower(),
            "themes": themes,
            "starters": starters[:3],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feedbacks": [],
            "generation_source": "gpt2-validated" if starter_generator.gpt2 else "quality-safe-template",
        }
        history_db.append(entry)
        return entry
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")


@app.get("/api/factcheck", response_model=FactCheckResponse)
async def factcheck(query: str = Query(..., min_length=1)):
    try:
        return fact_checker.verify_topic(query)
    except Exception as exc:
        logger.exception("Factcheck failed")
        raise HTTPException(status_code=500, detail=f"Factcheck failed: {exc}")


@app.get("/api/history", response_model=List[GenerateResponse])
async def get_history(user_email: Optional[str] = Query(default=None)):
    rows = history_db
    if user_email:
        email = user_email.strip().lower()
        rows = [x for x in rows if x.get("user_email", "") == email]
    return sorted(rows, key=lambda x: x["timestamp"], reverse=True)


@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    for entry in history_db:
        if entry["id"] == payload.id:
            if payload.user_email and entry.get("user_email") != payload.user_email.strip().lower():
                raise HTTPException(status_code=403, detail="Feedback does not belong to this user.")
            if payload.starter_index >= len(entry["starters"]):
                raise HTTPException(status_code=400, detail="Invalid starter index.")
            entry["feedbacks"].append(
                {
                    "starter_index": payload.starter_index,
                    "rating": payload.rating,
                    "comment": (payload.comment or "").strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            return {"status": "success", "message": "Feedback submitted successfully."}
    raise HTTPException(status_code=404, detail="Generated starters history record not found.")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "personalized-networking-assistant"}
