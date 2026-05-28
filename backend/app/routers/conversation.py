import uuid
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from loguru import logger

from app.dependencies import get_current_user 
from app.services.llm_service import llm_service
from app.services.feedback_service import feedback_service
from app.services.progress_service import progress_service
from app.utils.language_codes import get_greeting, get_language_name
from app.utils.validators import validate_language_code, sanitize_text_input

router = APIRouter(prefix="/conversation", tags=["Conversation"])


class ConversationStartRequest(BaseModel):
    language: Optional[str] = None


class ConversationRespondRequest(BaseModel):
    session_id: str
    user_message: str
    language: Optional[str] = None


@router.post("/start", summary="Start a new conversation session")
async def start_conversation(
    request: ConversationStartRequest,
    current_user: dict = Depends(get_current_user)
):
    language = request.language or current_user.get("preferred_language", "en")
    language = validate_language_code(language)
    session_id = str(uuid.uuid4())
    greeting = get_greeting(language)
    lang_name = get_language_name(language)
    session_data = {
        "user_id": current_user["id"],
        "language": language,
        "created_at": datetime.utcnow().isoformat(),
        "turn_count": 0,
        "history": []
    }
    await redis_client.setex(f"session:{session_id}", 3600, json.dumps(session_data))
    return {
        "success": True,
        "session_id": session_id,
        "language": language,
        "language_name": lang_name,
        "greeting": greeting,
        "expires_in": 3600
    }


@router.post("/respond", summary="Send message and get AI coaching response")
async def conversation_respond(
    request: ConversationRespondRequest,
    current_user: dict = Depends(get_current_user)
):
    user_message = sanitize_text_input(request.user_message, max_length=2000)
    session_key = f"session:{request.session_id}"
    session_raw = await redis_client.get(session_key)
    if not session_raw:
        raise HTTPException(status_code=404, detail="Session expired or not found.")
    session_data = json.loads(session_raw)
    language = request.language or session_data.get("language", "en")
    history = session_data.get("history", [])
    ai_response = await llm_service.generate_conversation_response(
        user_message=user_message,
        language_code=language,
        history=history[-5:]
    )
    try:
        feedback = await llm_service.generate_speech_feedback(user_message, language)
        feedback = feedback_service.enrich_feedback(feedback, user_message, language)
    except Exception as e:
        logger.warning(f"Feedback generation failed: {e}")
        feedback = None
    conv_data = {
        "user_id": current_user["id"],
        "language": language,
        "user_message": user_message,
        "ai_response": ai_response,
        "feedback": feedback,
        "fluency_score": feedback.get("fluency_score") if feedback else None,
        "pronunciation_score": feedback.get("pronunciation_score") if feedback else None,
        "grammar_score": feedback.get("grammar_score") if feedback else None,
    }
    result = supabase.table("conversations").insert(conv_data).execute()
    conversation_id = result.data[0]["id"] if result.data else None
    history.append({"user": user_message, "ai": ai_response})
    session_data["history"] = history[-10:]
    session_data["turn_count"] = session_data.get("turn_count", 0) + 1
    await redis_client.setex(session_key, 3600, json.dumps(session_data))
    if feedback and conversation_id:
        try:
            await progress_service.update_skill_scores(current_user["id"], {
                "fluency": feedback.get("fluency_score", 0),
                "grammar": feedback.get("grammar_score", 0),
                "pronunciation": feedback.get("pronunciation_score", 0)
            })
        except Exception as e:
            logger.warning(f"Progress update failed: {e}")
    return {
        "success": True,
        "conversation_id": conversation_id,
        "ai_response": ai_response,
        "feedback": feedback,
        "turn_number": session_data.get("turn_count", 1),
        "language": language
    }


@router.get("/history", summary="Get paginated conversation history")
async def get_conversation_history(
    page: int = Query(1, ge=1),
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    limit = 20
    offset = (page - 1) * limit
    query = supabase.table("conversations").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + limit - 1)
    if language:
        query = query.eq("language", language)
    result = query.execute()
    count_result = supabase.table("conversations").select("id", count="exact").eq("user_id", current_user["id"]).execute()
    total = count_result.count or 0
    return {
        "success": True,
        "conversations": result.data or [],
        "pagination": {"page": page, "per_page": limit, "total": total, "pages": (total + limit - 1) // limit}
    }


@router.put("/{conversation_id}/save", summary="Bookmark a conversation")
async def save_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", current_user["id"]).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    conv = result.data[0]
    current_saved = conv.get("feedback", {})
    if isinstance(current_saved, dict):
        is_saved = current_saved.get("_saved", False)
    else:
        is_saved = False
    new_feedback = current_saved if isinstance(current_saved, dict) else {}
    new_feedback["_saved"] = not is_saved
    supabase.table("conversations").update({"feedback": new_feedback}).eq("id", conversation_id).execute()
    return {"success": True, "conversation_id": conversation_id, "saved": not is_saved}


@router.delete("/{conversation_id}", summary="Soft delete a conversation")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", current_user["id"]).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    supabase.table("conversations").update({"feedback": {"_deleted": True, "_deleted_at": datetime.utcnow().isoformat()}}).eq("id", conversation_id).execute()
    return {"success": True, "message": "Conversation deleted successfully."}