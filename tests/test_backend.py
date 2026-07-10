from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("backend.main.theme_extractor.extract_themes")
@patch("backend.main.starter_generator.generate_starters")
def test_generate_starters(mock_generate, mock_extract):
    # Setup mocks
    mock_extract.return_value = ["Python", "Machine Learning"]
    mock_generate.return_value = [
        "Hi, I noticed your interest in Python.",
        "Hello, let's connect about Machine Learning.",
        "Hey, dynamic test starter!"
    ]
    
    # Test valid request
    payload = {
        "context": "Interested in Python and ML",
        "relationship": "colleague",
        "tone": "professional"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["context"] == payload["context"]
    assert data["themes"] == ["Python", "Machine Learning"]
    assert len(data["starters"]) == 3
    assert data["starters"][0] == "Hi, I noticed your interest in Python."
    
    # Test invalid empty context request
    response_invalid = client.post("/api/generate", json={"context": ""})
    assert response_invalid.status_code == 400

@patch("backend.main.fact_checker.verify_topic")
def test_factcheck(mock_verify):
    mock_verify.return_value = {
        "verified": True,
        "message": "Successfully verified against Wikipedia article: 'Python (programming language)'",
        "title": "Python (programming language)",
        "summary": "Python is a high-level general-purpose programming language.",
        "source_url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
    }
    
    response = client.get("/api/factcheck?query=Python")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["title"] == "Python (programming language)"
    
    # Test validation error
    response_empty = client.get("/api/factcheck?query=")
    assert response_empty.status_code == 400

def test_feedback_and_history():
    # Insert a dummy item directly into the backend history database for testing
    from backend.main import history_db
    dummy_id = "test-uuid-123"
    history_db.append({
        "id": dummy_id,
        "context": "Context text",
        "relationship": "colleague",
        "tone": "professional",
        "themes": ["Python"],
        "starters": ["Starter 1", "Starter 2"],
        "timestamp": "2026-07-09T23:42:06",
        "feedbacks": []
    })
    
    # Test history retrieval
    response = client.get("/api/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert any(x["id"] == dummy_id for x in history)
    
    # Test submitting feedback
    feedback_payload = {
        "id": dummy_id,
        "starter_index": 0,
        "rating": "thumbs_up",
        "comment": "Great starter!"
    }
    response_fb = client.post("/api/feedback", json=feedback_payload)
    assert response_fb.status_code == 200
    assert response_fb.json() == {"status": "success", "message": "Feedback submitted successfully."}
    
    # Verify that feedback is recorded
    response_history = client.get("/api/history")
    history_updated = response_history.json()
    item = [x for x in history_updated if x["id"] == dummy_id][0]
    assert len(item["feedbacks"]) == 1
    assert item["feedbacks"][0]["comment"] == "Great starter!"
    assert item["feedbacks"][0]["rating"] == "thumbs_up"
    
    # Test invalid index feedback
    feedback_invalid_index = {
        "id": dummy_id,
        "starter_index": 5,
        "rating": "thumbs_down"
    }
    response_invalid_fb = client.post("/api/feedback", json=feedback_invalid_index)
    assert response_invalid_fb.status_code == 400
    
    # Test non-existent id feedback
    feedback_nonexistent_id = {
        "id": "non-existent-id",
        "starter_index": 0,
        "rating": "thumbs_up"
    }
    response_nonexistent_fb = client.post("/api/feedback", json=feedback_nonexistent_id)
    assert response_nonexistent_fb.status_code == 404

def test_real_factcheck_endpoint():
    response = client.get("/api/factcheck?query=Python")
    print("\n--- REAL ENDPOINT TEST ---")
    print("STATUS CODE:", response.status_code)
    print("RESPONSE BODY:", response.text)
    print("--------------------------")
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True



