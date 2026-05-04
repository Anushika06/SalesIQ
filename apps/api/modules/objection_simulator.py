from typing import List
import uuid

from shared.models import (
    ObjectionSimulateRequest, 
    SimulatedObjections, 
    ObjectionRespondRequest, 
    ObjectionScore
)
from shared.gemini_client import generate
from shared.firestore_client import save_conversation_session

async def simulate_objections(request: ObjectionSimulateRequest) -> SimulatedObjections:
    """Generate 3 realistic objections based on product and persona."""
    system_prompt = (
        "You are playing the role of a target B2B persona being pitched a product. "
        "Generate realistic objections you would raise."
    )
    user_prompt = (
        f"Target Persona: {request.target_persona}\n"
        f"Product Description: {request.product_description}\n\n"
        "Generate exactly 3 distinct, realistic objections."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=SimulatedObjections.model_json_schema()
    )
    
    return SimulatedObjections.model_validate(response_dict)

async def score_objection_response(session_id: str, request: ObjectionRespondRequest) -> ObjectionScore:
    """Score a rep's response to an objection and provide improvement tips."""
    system_prompt = (
        "You are an expert sales coach. Score the sales rep's response to an objection. "
        "Score on 3 dimensions: clarity (0-10), empathy (0-10), forward_momentum (0-10). "
        "The overall score should be the sum (0-30). "
        "Provide specific improvement tips."
    )
    user_prompt = (
        f"Objection raised: {request.objection}\n"
        f"Rep's Response: {request.rep_response}\n\n"
        "Evaluate the response."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=ObjectionScore.model_json_schema()
    )
    
    score = ObjectionScore.model_validate(response_dict)
    
    # Store session history
    session_data = {
        "objection": request.objection,
        "rep_response": request.rep_response,
        "scores": score.model_dump()
    }
    await save_conversation_session(session_id, session_data)
    
    return score
