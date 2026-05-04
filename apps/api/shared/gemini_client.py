import json
import time
import asyncio
import logging
from typing import Optional, Union, Dict, Any
from google.cloud import logging as cloud_logging
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from shared.config import settings

# Setup Cloud Logging
logging_client = cloud_logging.Client()
logger = logging_client.logger("gemini-client-logger")
# Fallback local logger
local_logger = logging.getLogger("gemini-client")
local_logger.setLevel(logging.INFO)

# Initialize Vertex AI
vertexai.init(project=settings.VERTEX_AI_PROJECT, location=settings.VERTEX_AI_LOCATION)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def _call_gemini_with_retry(
    model: GenerativeModel,
    contents: list,
    generation_config: dict
) -> Any:
    # Since generate_content_async is preferred for async contexts
    response = await model.generate_content_async(
        contents=contents,
        generation_config=generation_config
    )
    return response

async def generate(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Dict[str, Any]] = None
) -> Union[Dict[str, Any], str]:
    """
    Generate content using Gemini via Vertex AI.
    If response_schema is provided, returns JSON/dict, otherwise returns str.
    """
    start_time = time.time()
    
    try:
        model = GenerativeModel(
            model_name=settings.GEMINI_MODEL_NAME,
            system_instruction=system_prompt
        )
        
        generation_config = {"temperature": 0.2}
        if response_schema:
            generation_config["response_mime_type"] = "application/json"
            # In Vertex AI Python SDK, response_schema can be passed if supported,
            # but setting response_mime_type="application/json" often expects 
            # schema as part of generation_config or prompt. Let's pass it if API supports it,
            # otherwise prompt engineering is required. Vertex AI supports response_schema.
            generation_config["response_schema"] = response_schema
            
        # Call Gemini model
        response = await _call_gemini_with_retry(
            model=model,
            contents=[user_prompt],
            generation_config=generation_config
        )
        
        duration = time.time() - start_time
        logger.log_struct({
            "event": "gemini_generation",
            "duration_ms": int(duration * 1000),
            "model": settings.GEMINI_MODEL_NAME,
            "status": "success"
        }, severity="INFO")
        
        if response_schema:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # If Gemini doesn't return perfect JSON despite mime_type
                return {"error": "Invalid JSON returned", "raw": response.text}
        
        return response.text

    except Exception as e:
        duration = time.time() - start_time
        logger.log_struct({
            "event": "gemini_generation",
            "duration_ms": int(duration * 1000),
            "model": settings.GEMINI_MODEL_NAME,
            "status": "error",
            "error_message": str(e)
        }, severity="ERROR")
        raise e
