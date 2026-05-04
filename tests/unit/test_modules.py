import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from shared.models import ProspectResearchRequest, ProspectBrief
from modules.prospect_research import generate_prospect_brief

@pytest.mark.asyncio
@patch("modules.prospect_research.save_lead_brief", new_callable=AsyncMock)
@patch("modules.prospect_research.generate", new_callable=AsyncMock)
@patch("modules.prospect_research.redact_pii", new_callable=AsyncMock)
async def test_generate_prospect_brief(mock_redact_pii, mock_generate, mock_save_lead_brief):
    # Setup mocks
    mock_redact_pii.return_value = "Redacted content"
    mock_generate.return_value = {
        "summary": "Great prospect",
        "pain_points": ["Cost", "Time"],
        "trigger_events": ["New CEO"],
        "talking_points": ["Point 1", "Point 2", "Point 3"],
        "conversation_starter": "Hey!",
        "confidence_score": 0.9
    }
    
    # Execute
    req = ProspectResearchRequest(
        linkedin_url="http://linkedin.com/in/johndoe",
        company_website="http://example.com",
        prospect_name="John Doe"
    )
    result = await generate_prospect_brief("lead-123", req)
    
    # Assert
    assert isinstance(result, ProspectBrief)
    assert result.summary == "Great prospect"
    assert result.confidence_score == 0.9
    
    mock_redact_pii.assert_called()
    mock_generate.assert_called_once()
    mock_save_lead_brief.assert_called_once_with("lead-123", result)

@pytest.mark.asyncio
@patch("modules.prospect_research.generate", new_callable=AsyncMock)
async def test_generate_prospect_brief_timeout(mock_generate):
    # Simulate timeout
    mock_generate.side_effect = Exception("Gemini Timeout")
    
    req = ProspectResearchRequest(
        linkedin_url="http://linkedin.com/in/johndoe",
        company_website="http://example.com",
        prospect_name="John Doe"
    )
    
    with pytest.raises(Exception, match="Gemini Timeout"):
        await generate_prospect_brief("lead-123", req)
