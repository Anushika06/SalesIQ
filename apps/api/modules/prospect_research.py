import uuid
from shared.models import ProspectResearchRequest, ProspectBrief
from shared.gemini_client import generate
from shared.dlp_client import redact_pii
from shared.firestore_client import save_lead_brief

async def simulate_scraping(url: str) -> str:
    """Mock function to simulate scraping a website or LinkedIn."""
    return f"Scraped content from {url}. Contains John Doe, johndoe@example.com, 555-1234."

async def generate_prospect_brief(lead_id: str, request: ProspectResearchRequest) -> ProspectBrief:
    """
    Generate a prospect brief using Gemini.
    """
    # 1. Simulate scraping
    raw_linkedin = await simulate_scraping(request.linkedin_url)
    raw_website = await simulate_scraping(request.company_website)
    raw_content = f"LinkedIn: {raw_linkedin}\nWebsite: {raw_website}"

    # 2. Redact PII before storing/logging
    redacted_content = await redact_pii(raw_content)

    # 3. Use Gemini to synthesize brief
    system_prompt = (
        "You are an expert B2B sales researcher. Analyze the following information "
        "about a prospect and their company to generate a comprehensive sales brief. "
        "Focus on actionable insights for the sales rep."
    )
    
    user_prompt = (
        f"Prospect Name: {request.prospect_name}\n"
        f"Company Info (Redacted):\n{redacted_content}\n\n"
        "Generate a brief with a summary, pain points, trigger events, 3 talking points, "
        "a personalized conversation starter, and a confidence score."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=ProspectBrief.model_json_schema()
    )

    # Convert to Pydantic model
    brief = ProspectBrief.model_validate(response_dict)

    # 4. Store in Firestore
    await save_lead_brief(lead_id, brief)

    return brief
