from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.permissions import get_current_user
from app.rag.pipeline import generate_rag_response
from app.db.mongodb import db
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    conversation_id: str
    is_guest: bool = False
    requested_scope: Optional[dict] = None

@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    user_profile = current_user if current_user else {"role": "guest"}
    
    if request.is_guest:
        # Verify guest session exists or create one
        session = await db.guest_sessions.find_one({"guest_session_id": request.conversation_id})
        if not session:
            raise HTTPException(status_code=404, detail="Guest session not found")
            
    response = await generate_rag_response(
        question=request.question,
        conversation_id=request.conversation_id,
        user_profile=user_profile,
        is_guest=request.is_guest,
        requested_scope=request.requested_scope
    )
    
    return response

@router.post("/guest/session")
async def create_guest_session():
    session_id = str(uuid.uuid4())
    from datetime import datetime, timedelta
    from app.config import settings
    
    session = {
        "guest_session_id": session_id,
        "messages": [],
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=settings.GUEST_SESSION_TTL_HOURS),
        "status": "active"
    }
    await db.guest_sessions.insert_one(session)
    return {"guest_session_id": session_id, "expires_at": session["expires_at"]}
