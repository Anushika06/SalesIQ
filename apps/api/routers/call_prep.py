from fastapi import APIRouter, Depends

from shared.models import CallPrepRequest, CallBrief
from shared.auth import verify_token
from modules.call_prep import generate_call_prep

router = APIRouter(prefix="/callprep", tags=["Sales Call Prep"])

@router.post("/generate", response_model=CallBrief)
async def prepare_for_call(
    request: CallPrepRequest,
    user: dict = Depends(verify_token) # Normally verify token, but might be called via Eventarc. 
    # Eventarc requests might use a different service account auth. Let's keep it simple for now.
):
    """Generate a pre-call brief and notify the rep."""
    return await generate_call_prep(request)
