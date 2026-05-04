import json
import logging
from shared.gemini_client import generate
from shared.firestore_client import db

logger = logging.getLogger("salesiq-researcher")

async def perform_research(lead_id: str, company_name: str) -> dict:
    doc_ref = db.collection("leads").document(lead_id).collection("research").document("data")
    
    # Check if already exists to save API tokens
    doc_snap = await doc_ref.get()
    if doc_snap.exists:
        logger.info(f"Research for {company_name} already exists. Skipping.")
        return doc_snap.to_dict()

    prompt = f"""
    Perform deep prospect research on the company: {company_name}.
    Return a JSON object strictly matching this schema:
    {{
        "summary": "A 1-sentence summary of what the company does.",
        "recent_news": "2-3 recent_news bullet points.",
        "key_value_proposition": "A 1-sentence key_value_proposition."
    }}
    """
    
    try:
        # Trigger Gemini
        response = await generate(prompt)
        
        # Parse the JSON response
        if isinstance(response, str):
            clean_json = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
        else:
            data = response
            
        # Ensure keys exist
        data.setdefault("summary", "No summary available.")
        data.setdefault("recent_news", "No recent news found.")
        data.setdefault("key_value_proposition", "No clear value proposition identified.")
        
    except Exception as e:
        logger.error(f"Error generating research for {company_name}: {str(e)}")
        # Basic error handling in case Gemini cannot find info
        data = {
            "summary": f"Could not generate research for {company_name}.",
            "recent_news": "N/A",
            "key_value_proposition": "N/A"
        }
        
    # Save to Firestore under leads/{lead_id}/research/data
    try:
        await doc_ref.set(data)
    except Exception as e:
        logger.error(f"Error saving to Firestore: {str(e)}")
        
    return data
