import uuid
import time
import logging
from fastapi import FastAPI, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.firestore_client import db
from shared.config import settings
from pydantic import BaseModel

# Use Python's built-in logging — no Google Cloud auth required locally
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("salesiq-api")

class ResearchRequest(BaseModel):
    company_name: str

from routers import (
    prospect_research,
    message_optimizer,
    objection_simulator,
    followup_strategist,
    ab_tester,
    call_prep,
    response_analyzer
)

app = FastAPI(title="SalesIQ API", version="1.0.0")

# CORS — allow Vite dev server and Firebase Hosting
origins = [
    "http://localhost:5173",
    f"https://{settings.VERTEX_AI_PROJECT}.web.app",
    f"https://{settings.VERTEX_AI_PROJECT}.firebaseapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms) "
        f"[req={request_id[:8]}]"
    )
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(exc),
            "instance": str(request.url),
        },
    )

# Routers
app.include_router(prospect_research.router, prefix="/api/v1")
app.include_router(message_optimizer.router, prefix="/api/v1")
app.include_router(objection_simulator.router, prefix="/api/v1")
app.include_router(followup_strategist.router, prefix="/api/v1")
app.include_router(ab_tester.router, prefix="/api/v1")
app.include_router(call_prep.router, prefix="/api/v1")
app.include_router(response_analyzer.router, prefix="/api/v1")

@app.post("/api/v1/research/{lead_id}")
async def trigger_research(lead_id: str, request: ResearchRequest):
    from services.researcher import perform_research
    result = await perform_research(lead_id, request.company_name)
    return result

@app.get("/api/v1/leads/{lead_id}")
async def get_lead(lead_id: str, background_tasks: BackgroundTasks):
    doc_ref = db.collection("leads").document(lead_id)
    doc_snap = await doc_ref.get()

    lead_data = doc_snap.to_dict() if doc_snap.exists else {"company": "Google", "name": "Sundar Pichai"}
    company_name = lead_data.get("company", "Google")

    from services.researcher import perform_research
    background_tasks.add_task(perform_research, lead_id, company_name)

    return {"status": "success", "message": f"Background tasks for {company_name} started."}

@app.get("/health")
async def health_check():
    """Health check endpoint pinging Firestore."""
    try:
        from google.cloud import firestore
        doc_ref = db.collection("health").document("ping")
        await doc_ref.set({"timestamp": firestore.SERVER_TIMESTAMP})
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)},
        )
