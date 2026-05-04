import asyncio
import os
from google.cloud import dlp_v2
from shared.config import settings

async def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information (PII) from text using Cloud DLP.
    Redacts: PERSON_NAME, EMAIL_ADDRESS, PHONE_NUMBER.
    """
    # Initialize the DLP client
    dlp = dlp_v2.DlpServiceClient()

    # The Google Cloud project ID is needed for the DLP parent path
    # If not in settings, fall back to default project or GOOGLE_CLOUD_PROJECT
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", settings.VERTEX_AI_PROJECT)
    parent = f"projects/{project_id}/locations/global"

    # Construct inspect configuration dictionary
    inspect_config = {
        "info_types": [
            {"name": "PERSON_NAME"},
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
        ],
    }

    # Construct deidentify configuration dictionary
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_with_info_type_config": {}
                    }
                }
            ]
        }
    }

    # Construct item
    item = {"value": text}

    def _call():
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )
        return response.item.value

    # Run the synchronous DLP API call in a thread pool
    redacted_text = await asyncio.to_thread(_call)
    return redacted_text
