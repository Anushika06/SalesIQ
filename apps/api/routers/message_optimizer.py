from fastapi import APIRouter, Depends, HTTPException
import traceback

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
    try:
        return await optimize_message(request)
    except Exception as e:
        error_msg = f"Gemini/Optimization Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=str(e))
