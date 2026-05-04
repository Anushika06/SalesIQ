import uuid
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import logging as cloud_logging
import asyncio

from shared.firestore_client import db
from shared.config import settings

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

# Setup CORS
# In production, restrict to Firebase Hosting domain (e.g. https://<project>.web.app)
origins = [
    "http://localhost:5173",  # Vite default
    f"https://{settings.VERTEX_AI_PROJECT}.web.app",
    f"https://{settings.VERTEX_AI_PROJECT}.firebaseapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup structured logging
logging_client = cloud_logging.Client()
logger = logging_client.logger("salesiq-api-logger")

@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.log_struct({
        "event": "http_request",
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "duration_ms": int(process_time * 1000)
    }, severity="INFO")
    
    response.headers["X-Request-ID"] = request_id
    return response

# RFC 7807 Problem Details Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.log_struct({
        "event": "unhandled_exception",
        "request_id": getattr(request.state, "request_id", "unknown"),
        "error": str(exc)
    }, severity="ERROR")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(exc),
            "instance": str(request.url)
        }
    )

# Routers
app.include_router(prospect_research.router, prefix="/api/v1")
app.include_router(message_optimizer.router, prefix="/api/v1")
app.include_router(objection_simulator.router, prefix="/api/v1")
app.include_router(followup_strategist.router, prefix="/api/v1")
app.include_router(ab_tester.router, prefix="/api/v1")
app.include_router(call_prep.router, prefix="/api/v1")
app.include_router(response_analyzer.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint pinging Firestore."""
    try:
        from google.cloud import firestore
        # Ping Firestore
        doc_ref = db.collection("health").document("ping")
        await doc_ref.set({"timestamp": firestore.SERVER_TIMESTAMP})
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)}
        )
