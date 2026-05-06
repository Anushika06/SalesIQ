import json
import os
import time
import logging
from typing import Optional, Union, Dict, Any

from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from shared.config import settings

# Fallback local logger (Cloud Logging skipped to avoid auth noise)
local_logger = logging.getLogger("gemini-client")
local_logger.setLevel(logging.INFO)

# ── Credential resolution ────────────────────────────────────────────────────
# Force the absolute path regardless of CWD
_KEY_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.abspath("salesiq-key.json")
)

if not os.path.exists(_KEY_PATH):
    raise FileNotFoundError(
        f"Service account key not found at: {_KEY_PATH}\n"
        "Set GOOGLE_APPLICATION_CREDENTIALS in apps/api/.env"
    )

# Build an explicit credentials object — bypasses ADC / user credential collision
credentials = service_account.Credentials.from_service_account_file(
    _KEY_PATH
)
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
local_logger.info(f"Loaded service account: {credentials.service_account_email}")

# ── Vertex AI init ───────────────────────────────────────────────────────────
vertexai.init(
    project=settings.VERTEX_AI_PROJECT,
    location='global',
    credentials=scoped_credentials,          # explicit — no ADC fallback
)

# ── Retry helper ─────────────────────────────────────────────────────────────
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def _call_gemini_with_retry(model: GenerativeModel, contents: list, generation_config: dict) -> Any:
    return await model.generate_content_async(
        contents=contents,
        generation_config=generation_config,
    )

# ── Public generate function ─────────────────────────────────────────────────
async def generate(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, Any], str]:
    """
    Generate content using Gemini via Vertex AI.
    Returns a dict when response_schema is provided, otherwise a plain string.
    """
    start_time = time.time()

    try:
        # Pass credentials directly into the model — the nuclear fix
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
        )

        generation_config: Dict[str, Any] = {"temperature": 0.2}
        if response_schema:
            generation_config["response_mime_type"] = "application/json"
            generation_config["response_schema"] = response_schema

        response = await _call_gemini_with_retry(
            model=model,
            contents=[user_prompt],
            generation_config=generation_config,
        )

        duration_ms = int((time.time() - start_time) * 1000)
        local_logger.info(f"Gemini OK — {duration_ms}ms | model={settings.GEMINI_MODEL_NAME}")

        if response_schema:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                local_logger.warning(f"Gemini returned non-JSON: {response.text[:200]}")
                return {"error": "Invalid JSON returned", "raw": response.text}

        return response.text

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        local_logger.error(
            f"Gemini FAILED — {duration_ms}ms | model={settings.GEMINI_MODEL_NAME} | "
            f"error_type={type(e).__name__} | detail={e}"
        )
        raise
