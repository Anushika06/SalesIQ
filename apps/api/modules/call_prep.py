import os
from firebase_admin import messaging, credentials, initialize_app

from shared.models import CallPrepRequest, CallBrief, ProspectBrief, Message
from shared.gemini_client import generate
from shared.firestore_client import save_call_brief, get_lead_brief, get_conversation_history

# Firebase Admin is already initialized in shared.auth


async def generate_call_prep(request: CallPrepRequest) -> CallBrief:
    """Generate a pre-call intelligence brief."""
    
    # 1. Fetch brief and history
    brief = await get_lead_brief(request.lead_id, ProspectBrief)
    history = await get_conversation_history(request.lead_id, Message)
    
    brief_summary = brief.summary if brief else "No brief available."
    history_str = "\n".join(
        [f"[{m.timestamp.isoformat()}] {m.role.upper()}: {m.content}" for m in history]
    )
    
    # 2. Generate Call Brief with Gemini
    system_prompt = (
        "You are an elite B2B sales strategist preparing a rep for a crucial call. "
        "Review the prospect brief and conversation history to create a concise, "
        "high-impact pre-call brief."
    )
    user_prompt = (
        f"Meeting Time: {request.meeting_time.isoformat()}\n"
        f"Prospect Summary: {brief_summary}\n"
        f"Conversation History:\n{history_str}\n\n"
        "Generate a call brief with an executive summary, 3 likely objections with suggested responses, "
        "competitive intel notes, a recommended opening question, and key metrics to mention."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=CallBrief.model_json_schema()
    )
    
    call_brief = CallBrief.model_validate(response_dict)

    # 3. Store in Firestore
    await save_call_brief(request.calendar_event_id, call_brief)

    # 4. Send FCM push notification (assuming topic is rep's lead_id or generic topic for demo)
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f"Call Prep Ready for Lead {request.lead_id}",
                body=call_brief.executive_summary[:100] + "..."
            ),
            topic=f"rep_alerts"  # In a real app, send to specific device token
        )
        # We run this sync function in an async context. It might block briefly.
        messaging.send(message)
    except Exception as e:
        print(f"Warning: Failed to send FCM notification: {e}")

    return call_brief
