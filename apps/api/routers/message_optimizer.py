from fastapi import APIRouter, Depends

from shared.models import MessageOptimizeRequest, OptimizedMessage
from shared.auth import verify_token
from modules.message_optimizer import optimize_message

router = APIRouter(prefix="/message", tags=["Message Optimizer"])

@router.post("/optimize", response_model=OptimizedMessage)
async def optimize_draft_message(
    request: MessageOptimizeRequest,
    user: dict = Depends(verify_token)
):
    """
    Optimize a draft message based on prospect insights.
    """
    return await optimize_message(request)
