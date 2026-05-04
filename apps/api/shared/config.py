from typing import Optional
from pydantic_settings import BaseSettings
from google.cloud import secretmanager
import os

class Settings(BaseSettings):
    VERTEX_AI_PROJECT: str
    VERTEX_AI_LOCATION: str
    GEMINI_MODEL_NAME: str
    FIRESTORE_DB: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

def fetch_secret(secret_id: str, project_id: str) -> str:
    """Fetch a secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        # Fallback to environment variables if secret manager fails, useful for local dev
        val = os.environ.get(secret_id)
        if val is not None:
            return val
        raise e

def load_settings() -> Settings:
    # First, try to load settings locally
    try:
        settings = Settings()
        return settings
    except Exception as e:
        # If env variables aren't sufficient, setup fallback project
        if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            os.environ["GOOGLE_CLOUD_PROJECT"] = "promptwars"
            
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        
        try:
            # Try Secret Manager
            return Settings(
                VERTEX_AI_PROJECT=fetch_secret("VERTEX_AI_PROJECT", project_id),
                VERTEX_AI_LOCATION=fetch_secret("VERTEX_AI_LOCATION", project_id),
                GEMINI_MODEL_NAME=fetch_secret("GEMINI_MODEL_NAME", project_id),
                FIRESTORE_DB=fetch_secret("FIRESTORE_DB", project_id),
            )
        except Exception as sm_error:
            # Fallback to hackathon-friendly defaults if secret manager fails
            return Settings(
                VERTEX_AI_PROJECT=os.getenv("VERTEX_AI_PROJECT", "promptwars"),
                VERTEX_AI_LOCATION=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
                GEMINI_MODEL_NAME=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro"),
                FIRESTORE_DB=os.getenv("FIRESTORE_DB", "(default)"),
                GOOGLE_APPLICATION_CREDENTIALS=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                GOOGLE_CLOUD_PROJECT=project_id,
            )

settings = load_settings()
