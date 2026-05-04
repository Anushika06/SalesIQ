from fastapi import APIRouter, Depends

from shared.models import ResponseAnalyzeRequest, ResponseAnalysis
from shared.auth import verify_token
from modules.response_analyzer import analyze_response

router = APIRouter(prefix="/response", tags=["Response Analyzer"])

@router.post("/analyze", response_model=ResponseAnalysis)
async def analyze_incoming_response(
    request: ResponseAnalyzeRequest,
    user: dict = Depends(verify_token)
):
    """Analyze incoming prospect response and recommend next actions."""
    return await analyze_response(request)
