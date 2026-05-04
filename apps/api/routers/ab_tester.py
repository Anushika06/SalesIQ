from fastapi import APIRouter, Depends

from shared.models import ABTestGenerateRequest, ABTestResult
from shared.auth import verify_token
from modules.ab_tester import generate_ab_variants

router = APIRouter(prefix="/ab", tags=["A/B Email Tester"])

@router.post("/generate", response_model=ABTestResult)
async def generate_variants(
    request: ABTestGenerateRequest,
    user: dict = Depends(verify_token)
):
    """Generate and log A/B test variants."""
    return await generate_ab_variants(request)
