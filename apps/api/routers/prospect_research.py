import uuid
from fastapi import APIRouter, Depends

from shared.models import ProspectResearchRequest, ProspectBrief
from shared.auth import verify_token
from modules.prospect_research import generate_prospect_brief

router = APIRouter(prefix="/prospect", tags=["Prospect Research"])

@router.post("/research", response_model=ProspectBrief)
async def research_prospect(
    request: ProspectResearchRequest,
    user: dict = Depends(verify_token)
):
    """
    Generate a research brief for a given prospect.
    """
    # For now, generate a random lead_id. In reality, it might be provided or created beforehand.
    lead_id = str(uuid.uuid4())
    return await generate_prospect_brief(lead_id, request)
