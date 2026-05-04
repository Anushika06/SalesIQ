from shared.models import MessageOptimizeRequest, OptimizedMessage, ProspectBrief
from shared.gemini_client import generate
from shared.firestore_client import get_lead_brief

async def optimize_message(request: MessageOptimizeRequest) -> OptimizedMessage:
    """
    Optimize a sales message using Gemini, tailored to the prospect brief.
    """
    # 1. Fetch ProspectBrief from Firestore
    # Assuming prospect_brief_id here maps to lead_id for the lookup we designed
    lead_id = request.prospect_brief_id
    brief = await get_lead_brief(lead_id, ProspectBrief)
    
    if not brief:
        raise ValueError(f"ProspectBrief not found for lead_id: {lead_id}")

    # 2. Ask Gemini to rewrite the message
    system_prompt = (
        "You are an elite B2B sales copywriter. Your goal is to optimize sales "
        "messages to increase reply rates. Ensure the rewritten message includes:\n"
        "- A specific hook referencing a trigger event.\n"
        "- A tailored value proposition addressing pain points.\n"
        "- A low-friction Call to Action (CTA)."
    )

    user_prompt = (
        f"Original Draft: {request.draft_message}\n"
        f"Channel: {request.channel}\n"
        f"Prospect Summary: {brief.summary}\n"
        f"Trigger Events: {', '.join(brief.trigger_events)}\n"
        f"Pain Points: {', '.join(brief.pain_points)}\n\n"
        "Rewrite the message and explain the specific changes made."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=OptimizedMessage.model_json_schema()
    )

    # Convert to Pydantic model
    # Original might not be returned exactly, so we'll ensure it's set
    if "original" not in response_dict or not response_dict["original"]:
        response_dict["original"] = request.draft_message
        
    return OptimizedMessage.model_validate(response_dict)
