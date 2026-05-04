from google.cloud import bigquery
import os
from datetime import datetime

from shared.models import ABTestGenerateRequest, ABTestResult, ProspectBrief
from shared.gemini_client import generate
from shared.firestore_client import save_ab_variants, get_lead_brief
from shared.config import settings

async def generate_ab_variants(request: ABTestGenerateRequest) -> ABTestResult:
    """Generate A/B test variants and log them."""
    
    # 1. Fetch Prospect Brief
    brief = await get_lead_brief(request.prospect_brief_id, ProspectBrief)
    brief_summary = brief.summary if brief else "No brief available."
    
    # 2. Generate variants with Gemini
    system_prompt = (
        "You are an expert sales copywriter running an A/B test. "
        "Generate different variants of a base message using distinct psychological angles: "
        "authority, curiosity, reciprocity, etc."
    )
    user_prompt = (
        f"Base Message: {request.base_message}\n"
        f"Prospect Summary: {brief_summary}\n"
        f"Number of Variants: {request.num_variants}\n\n"
        "Generate exactly the requested number of variants. "
        "Predict estimated open rate and reply rate for each."
    )

    response_dict = await generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_schema=ABTestResult.model_json_schema()
    )
    
    result = ABTestResult.model_validate(response_dict)

    # 3. Store in Firestore
    variants_data = [v.model_dump() for v in result.variants]
    await save_ab_variants(request.prospect_brief_id, variants_data)

    # 4. Log to BigQuery
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", settings.VERTEX_AI_PROJECT)
        bq_client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.salesiq.ab_tests"
        
        rows_to_insert = []
        for i, variant in enumerate(result.variants):
            rows_to_insert.append({
                "variant_id": f"var_{request.prospect_brief_id}_{i}_{int(datetime.utcnow().timestamp())}",
                "lead_id": request.prospect_brief_id,
                "angle": variant.angle,
                "predicted_open_rate": variant.estimated_open_rate,
                "predicted_reply_rate": variant.estimated_reply_rate,
                "created_at": datetime.utcnow().isoformat()
            })
            
        errors = bq_client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            print(f"Encountered errors while inserting rows to BQ: {errors}")
    except Exception as e:
        # Ignore BQ errors locally if table doesn't exist yet
        print(f"Warning: Failed to log to BigQuery: {e}")

    return result
