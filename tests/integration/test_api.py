import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../apps/api')))

# Mock the Firestore init and auth before importing app
with patch('firebase_admin.initialize_app'):
    with patch('google.cloud.firestore.AsyncClient'):
        from main import app

client = TestClient(app)

def test_health_check():
    # We'll mock the firestore call in the health check
    with patch("main.db.collection") as mock_collection:
        mock_doc = mock_collection.return_value.document.return_value
        mock_doc.set.return_value = None
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

# In a real scenario, we would use pytest-vcr to record Gemini API responses
# Example integration test for /api/v1/prospect/research
@patch("routers.prospect_research.generate_prospect_brief")
@patch("shared.auth.auth.verify_id_token")
def test_prospect_research_integration(mock_verify, mock_generate_brief):
    mock_verify.return_value = {"uid": "test-user"}
    
    from shared.models import ProspectBrief
    mock_generate_brief.return_value = ProspectBrief(
        summary="Integration Test",
        pain_points=[],
        trigger_events=[],
        talking_points=[],
        conversation_starter="Hello",
        confidence_score=0.8
    )

    response = client.post(
        "/api/v1/prospect/research",
        headers={"Authorization": "Bearer fake-token"},
        json={
            "linkedin_url": "http://linkedin",
            "company_website": "http://company",
            "prospect_name": "Jane"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["summary"] == "Integration Test"
