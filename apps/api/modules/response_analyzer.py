from shared.models import ResponseAnalyzeRequest, ResponseAnalysis, Message
from shared.gemini_client import generate
from shared.nlp_client import analyze_sentiment, extract_entities
from shared.firestore_client import get_conversation_history

async def analyze_response(request: ResponseAnalyzeRequest) -> ResponseAnalysis:
    """Analyze an incoming message and recommend next actions."""
    
    # 1. NLP Analysis
    sentiment_result = await analyze_sentiment(request.incoming_message)
    entities_result = await extract_entities(request.incoming_message)
    
    entities_str = ", ".join([f"{e.name} ({e.type})" for e in entities_result])
    
    # 2. Fetch Conversation History
    history = await get_conversation_history(request.lead_id, Message)
    history_str = "\n".join(
        [f"[{m.timestamp.isoformat()}] {m.role.upper()}: {m.content}" for m in history[-5:]] # last 5 msgs
    )

    # 3. Use Gemini to analyze and formulate response
    system_prompt = (
        "You are an AI sales assistant analyzing incoming prospect messages. "
        "Determine the prospect's intent, quantify buying signals and urgency, "
        "recommend the next action, and draft a tailored response."
    )
    user_prompt = (
        f"Incoming Message: {request.incoming_message}\n"
        f"NLP Sentiment Score: {sentiment_result.score}\n"
        f"NLP Entities Found: {entities_str}\n"
        f"Recent History:\n{history_str}\n\n"
        "Analyze the message and provide sentiment (positive/neutral/negative), "
        "intent (interested/stalling/objecting/ghosting/other), buying signal strength (0-100), "
        "urgency score (0-100), recommend next_action, and write a draft_response."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=ResponseAnalysis.model_json_schema()
    )
    
    return ResponseAnalysis.model_validate(response_dict)
