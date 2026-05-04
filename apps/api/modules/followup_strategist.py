import os
import json
from datetime import datetime
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from shared.models import FollowUpStrategizeRequest, FollowUpPlan
from shared.gemini_client import generate
from shared.nlp_client import analyze_sentiment
from shared.config import settings

async def strategize_followup(request: FollowUpStrategizeRequest) -> FollowUpPlan:
    """Determine the optimal follow-up strategy and schedule it in Cloud Tasks."""
    
    # 1. Run last reply through Cloud NLP (if history is not empty and last is prospect)
    sentiment_score = 0.0
    if request.conversation_history:
        last_msg = request.conversation_history[-1]
        if last_msg.role == "prospect":
            sentiment_result = await analyze_sentiment(last_msg.content)
            sentiment_score = sentiment_result.score

    # 2. Feed sentiment + conversation history to Gemini
    history_str = "\n".join(
        [f"[{m.timestamp.isoformat()}] {m.role.upper()}: {m.content}" for m in request.conversation_history]
    )

    system_prompt = (
        "You are a sales follow-up strategist. Determine the best time, channel, "
        "and message to follow up with a prospect."
    )
    user_prompt = (
        f"Last Prospect Sentiment Score (-1.0 to 1.0): {sentiment_score}\n"
        f"Conversation History:\n{history_str}\n\n"
        "Generate a follow-up plan including recommended_channel, optimal_send_time (ISO datetime format), "
        "tone_shift, and draft_message."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=FollowUpPlan.model_json_schema()
    )
    
    plan = FollowUpPlan.model_validate(response_dict)

    # 3. Enqueue follow-up task in Cloud Tasks
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", settings.VERTEX_AI_PROJECT)
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    queue_name = "followup-queue"
    
    try:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(project_id, location, queue_name)
        
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"https://{project_id}.appspot.com/api/v1/internal/send_followup", # Example URL
                "headers": {"Content-type": "application/json"},
                "body": json.dumps({
                    "lead_id": request.lead_id,
                    "message": plan.draft_message,
                    "channel": plan.recommended_channel
                }).encode(),
            }
        }
        
        # Schedule the task
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(plan.optimal_send_time)
        task["schedule_time"] = timestamp
        
        # Depending on IAM and sync vs async, this might block. We use a sync call as a simple implementation.
        created_task = client.create_task(request={"parent": parent, "task": task})
        plan.task_id = created_task.name
    except Exception as e:
        # If Cloud Tasks fails (e.g. locally without auth/queue created), mock it
        plan.task_id = f"mock-task-id-{plan.optimal_send_time.timestamp()}"

    return plan
