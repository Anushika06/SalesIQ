from fastapi import APIRouter, Depends

from shared.models import FollowUpStrategizeRequest, FollowUpPlan
from shared.auth import verify_token
from modules.followup_strategist import strategize_followup

router = APIRouter(prefix="/followup", tags=["Follow-up Strategist"])

@router.post("/strategize", response_model=FollowUpPlan)
async def strategize(
    request: FollowUpStrategizeRequest,
    user: dict = Depends(verify_token)
):
    """Determine follow-up strategy and queue it."""
    return await strategize_followup(request)
