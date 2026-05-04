from typing import TypeVar, Type, Optional, List, Dict, Any
from google.cloud import firestore
from pydantic import BaseModel

from shared.config import settings

# Initialize Firestore Async Client
db = firestore.AsyncClient(project=settings.VERTEX_AI_PROJECT, database=settings.FIRESTORE_DB)

T = TypeVar('T', bound=BaseModel)

async def _set_document(collection_name: str, doc_id: str, data: Dict[str, Any]) -> str:
    """Helper to set a document with server timestamps."""
    doc_ref = db.collection(collection_name).document(doc_id)
    
    # Check if doc exists to determine if we update or create
    doc_snap = await doc_ref.get()
    
    if doc_snap.exists:
        data["updated_at"] = firestore.SERVER_TIMESTAMP
        await doc_ref.update(data)
    else:
        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP
        await doc_ref.set(data)
        
    return doc_id

async def _add_document(collection_name: str, data: Dict[str, Any]) -> str:
    """Helper to add a document with auto-generated ID and server timestamps."""
    data["created_at"] = firestore.SERVER_TIMESTAMP
    data["updated_at"] = firestore.SERVER_TIMESTAMP
    
    doc_ref = db.collection(collection_name).document()
    await doc_ref.set(data)
    return doc_ref.id

async def _get_document(collection_name: str, doc_id: str, model_class: Type[T]) -> Optional[T]:
    """Helper to get a document and parse it into a Pydantic model."""
    doc_ref = db.collection(collection_name).document(doc_id)
    doc_snap = await doc_ref.get()
    
    if not doc_snap.exists:
        return None
        
    data = doc_snap.to_dict()
    # Optional: convert server timestamps to datetime if model expects it,
    # though Firestore handles some datetime mapping automatically.
    return model_class.model_validate(data)

async def _query_documents(collection_name: str, model_class: Type[T], filters: List[tuple] = None) -> List[T]:
    """Helper to query documents and parse them into Pydantic models."""
    query = db.collection(collection_name)
    
    if filters:
        for f in filters:
            query = query.where(filter=firestore.FieldFilter(f[0], f[1], f[2]))
            
    docs = query.stream()
    results = []
    async for doc in docs:
        data = doc.to_dict()
        results.append(model_class.model_validate(data))
        
    return results

# Specific collection operations based on requirements
async def save_lead_brief(lead_id: str, brief_data: BaseModel) -> str:
    """Store the resulting brief in Firestore under leads/{lead_id}/brief"""
    # Specifically the requirement says: "Store the resulting brief in Firestore under leads/{lead_id}/brief"
    # Wait, leads/{lead_id}/brief is a subcollection or just a field?
    # Usually it implies a subcollection: leads/{lead_id}/brief/{brief_id} or leads/{lead_id} with field "brief"
    # Assuming it's a subcollection document: leads/{lead_id}/brief/latest or similar,
    # or just updating the lead document. Let's just update the lead document with a brief field
    # or write to leads/{lead_id} with a 'brief' subcollection
    doc_ref = db.collection("leads").document(lead_id).collection("briefs").document("latest")
    data = brief_data.model_dump()
    data["created_at"] = firestore.SERVER_TIMESTAMP
    data["updated_at"] = firestore.SERVER_TIMESTAMP
    await doc_ref.set(data)
    return lead_id

async def save_conversation_session(session_id: str, session_data: dict) -> str:
    return await _set_document("conversations", session_id, session_data)

async def save_message(message_data: dict) -> str:
    return await _add_document("messages", message_data)

async def save_ab_variants(lead_id: str, variants_data: List[dict]):
    batch = db.batch()
    for variant in variants_data:
        variant["lead_id"] = lead_id
        variant["created_at"] = firestore.SERVER_TIMESTAMP
        variant["updated_at"] = firestore.SERVER_TIMESTAMP
        doc_ref = db.collection("ab_variants").document()
        batch.set(doc_ref, variant)
    await batch.commit()

async def save_call_brief(calendar_event_id: str, brief_data: BaseModel) -> str:
    data = brief_data.model_dump()
    return await _set_document("call_briefs", calendar_event_id, data)

async def get_lead_brief(lead_id: str, model_class: Type[T]) -> Optional[T]:
    # Match the storage location of save_lead_brief
    doc_ref = db.collection("leads").document(lead_id).collection("briefs").document("latest")
    doc_snap = await doc_ref.get()
    if doc_snap.exists:
        return model_class.model_validate(doc_snap.to_dict())
    return None

async def get_conversation_history(lead_id: str, model_class: Type[T]) -> List[T]:
    # Query messages collection by lead_id ordered by timestamp
    query = db.collection("messages").where(
        filter=firestore.FieldFilter("lead_id", "==", lead_id)
    ).order_by("timestamp")
    
    docs = query.stream()
    results = []
    async for doc in docs:
        results.append(model_class.model_validate(doc.to_dict()))
    return results
