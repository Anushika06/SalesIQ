from shared.models import MessageOptimizeRequest, OptimizedMessage, ProspectBrief
from shared.gemini_client import generate
from shared.firestore_client import get_lead_brief

async def optimize_message(request: MessageOptimizeRequest) -> OptimizedMessage:
    """
    Optimize a sales message using Gemini, tailored to the prospect brief.
    """
    # 1. Fetch Company Research from Firestore
    from shared.firestore_client import db
    lead_id = request.prospect_brief_id
    doc_ref = db.collection("leads").document(lead_id).collection("research").document("data")
    doc_snap = await doc_ref.get()
    
    if not doc_snap.exists:
        # Fallback: generate without research context
        brief = {
            "summary": "No research data available.",
            "recent_news": "N/A",
            "key_value_proposition": "N/A"
        }
        
    brief = doc_snap.to_dict()

    # 2. Ask Gemini to rewrite the message
    system_prompt = (
        "You are an elite B2B sales copywriter. Your goal is to optimize sales "
        "messages to increase reply rates. Ensure the rewritten message includes:\n"
        "- A specific hook referencing recent news.\n"
        "- A tailored value proposition addressing their company.\n"
        "- A low-friction Call to Action (CTA)."
    )

    user_prompt = (
        f"Original Draft: {request.draft_message}\n"
        f"Channel: {request.channel}\n"
        f"Prospect Summary: {brief.get('summary', '')}\n"
        f"Recent News: {brief.get('recent_news', '')}\n"
        f"Value Proposition: {brief.get('key_value_proposition', '')}\n\n"
        'Return a JSON object with exactly these keys: "original", "rewritten", "changes" (list of strings), "channel_specific_notes".'
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Parse JSON if returned as string
    import json
    if isinstance(response_dict, str):
        try:
            response_dict = json.loads(response_dict.strip().removeprefix("```json").removesuffix("```").strip())
        except json.JSONDecodeError:
            response_dict = {}

    # Ensure required fields always exist
    response_dict.setdefault("original", request.draft_message)
    response_dict.setdefault("rewritten", response_dict.get("original", request.draft_message))
    response_dict.setdefault("changes", ["Message optimized for persuasion."])
    response_dict.setdefault("channel_specific_notes", f"Optimized for {request.channel}.")

    return OptimizedMessage.model_validate(response_dict)
