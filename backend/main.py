from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime
import logging

from backend.services import ThemeExtractor, StarterGenerator, FactChecker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personalized Networking Assistant API",
    description="Backend services for theme extraction, message generation, and Wikipedia fact-checking.",
    version="1.0.0"
)
@app.get("/")
def home():
    return {"status": "healthy", "message": "Backend is running flawlessly"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for the Streamlit dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
theme_extractor = ThemeExtractor()
starter_generator = StarterGenerator()
fact_checker = FactChecker()

# In-memory history database
history_db = []

# Schemas
class GenerateRequest(BaseModel):
    context: str
    relationship: Optional[str] = "colleague"
    tone: Optional[str] = "professional"

class GenerateResponse(BaseModel):
    id: str
    context: str
    relationship: str
    tone: str
    themes: List[str]
    starters: List[str]
    timestamp: str
    feedbacks: List[dict] = []

class FeedbackRequest(BaseModel):
    id: str
    starter_index: int
    rating: str  # "thumbs_up" or "thumbs_down"
    comment: Optional[str] = ""

class FeedbackResponse(BaseModel):
    status: str
    message: str

class FactCheckResponse(BaseModel):
    verified: bool
    message: str
    title: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_starters(payload: GenerateRequest):
    if not payload.context.strip():
        raise HTTPException(status_code=400, detail="Context string cannot be empty.")
    
    try:
        # Extract themes/entities
        themes = theme_extractor.extract_themes(payload.context)
        
        # Generate smart starters
        starters = starter_generator.generate_starters(
            context=payload.context,
            themes=themes,
            relationship=payload.relationship,
            tone=payload.tone
        )
        
        # Create history entry
        entry = {
            "id": str(uuid.uuid4()),
            "context": payload.context,
            "relationship": payload.relationship,
            "tone": payload.tone,
            "themes": themes,
            "starters": starters,
            "timestamp": datetime.datetime.now().isoformat(),
            "feedbacks": []
        }
        history_db.append(entry)
        
        return entry
    except Exception as e:
        logger.error(f"Error in /api/generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/api/factcheck", response_model=FactCheckResponse)
async def factcheck(query: str = Query(..., description="The claim or topic to fact-check against Wikipedia.")):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    
    try:
        result = fact_checker.verify_topic(query)
        return result
    except Exception as e:
        logger.error(f"Error in /api/factcheck endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Factcheck failed: {str(e)}")

@app.get("/api/history", response_model=List[GenerateResponse])
async def get_history():
    # Return history items sorted by timestamp descending
    return sorted(history_db, key=lambda x: x["timestamp"], reverse=True)

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    for entry in history_db:
        if entry["id"] == payload.id:
            # Check if starter index is valid
            if payload.starter_index < 0 or payload.starter_index >= len(entry["starters"]):
                raise HTTPException(status_code=400, detail="Invalid starter index.")
            
            feedback_data = {
                "starter_index": payload.starter_index,
                "rating": payload.rating,
                "comment": payload.comment,
                "timestamp": datetime.datetime.now().isoformat()
            }
            entry["feedbacks"].append(feedback_data)
            return {"status": "success", "message": "Feedback submitted successfully."}
            
    raise HTTPException(status_code=404, detail="Generated starters history record not found.")

@app.get("/health")
def health():
    return {"status": "healthy"}
