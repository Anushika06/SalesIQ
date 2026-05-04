import uuid
from fastapi import APIRouter, Depends

from shared.models import ObjectionSimulateRequest, SimulatedObjections, ObjectionRespondRequest, ObjectionScore
from shared.auth import verify_token
from modules.objection_simulator import simulate_objections, score_objection_response

router = APIRouter(prefix="/objection", tags=["Objection Simulator"])

@router.post("/simulate", response_model=SimulatedObjections)
async def simulate(
    request: ObjectionSimulateRequest,
    user: dict = Depends(verify_token)
):
    """Simulate realistic objections based on a product and persona."""
    return await simulate_objections(request)

@router.post("/respond", response_model=ObjectionScore)
async def respond(
    request: ObjectionRespondRequest,
    user: dict = Depends(verify_token)
):
    """Score a rep's response to an objection."""
    session_id = str(uuid.uuid4())
    return await score_objection_response(session_id, request)
