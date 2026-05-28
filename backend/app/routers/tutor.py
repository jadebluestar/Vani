from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from loguru import logger

from app.dependencies import get_current_user
from app.database import supabase
from app.utils.validators import validate_rating

router = APIRouter(tags=["Tutor"])


class BookSessionRequest(BaseModel):
    tutor_id: str
    scheduled_at: str
    duration_minutes: int = 60


class CompleteSessionRequest(BaseModel):
    rating: float
    feedback: Optional[str] = None


@router.get("/tutors/search", summary="Search and filter available tutors")
async def search_tutors(
    language: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    current_user: dict = Depends(get_current_user)
):
    offset = (page - 1) * limit
    result = supabase.table("tutors").select("*, users(id, name, preferred_language, district)").eq("verified", True).order("rating", desc=True).range(offset, offset + limit - 1).execute()
    tutors = result.data or []
    if language:
        tutors = [t for t in tutors if language in (t.get("languages") or [])]
    if min_price is not None:
        tutors = [t for t in tutors if t.get("hourly_rate", 0) >= min_price]
    if max_price is not None:
        tutors = [t for t in tutors if t.get("hourly_rate", 0) <= max_price]
    if min_rating is not None:
        tutors = [t for t in tutors if (t.get("rating") or 0) >= min_rating]
    formatted = []
    for t in tutors:
        user_info = t.pop("users", {}) or {}
        formatted.append({**t, "name": user_info.get("name", "Tutor"), "district": user_info.get("district")})
    return {"success": True, "tutors": formatted, "total": len(formatted), "pagination": {"page": page, "per_page": limit}}


@router.post("/tutor/session/book", summary="Book a tutoring session")
async def book_session(
    request: BookSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    tutor_result = supabase.table("tutors").select("*").eq("id", request.tutor_id).eq("verified", True).execute()
    if not tutor_result.data:
        raise HTTPException(status_code=404, detail="Tutor not found or not verified.")
    tutor = tutor_result.data[0]
    hours = request.duration_minutes / 60
    total_cost = int(tutor["hourly_rate"] * hours)
    if current_user["coins_balance"] < total_cost:
        raise HTTPException(status_code=400, detail=f"Insufficient coins. You need {total_cost} coins but have {current_user['coins_balance']}.")
    if tutor["user_id"] == current_user["id"]:
        raise HTTPException(status_code=400, detail="You cannot book a session with yourself.")
    session_data = {"tutor_id": request.tutor_id, "learner_id": current_user["id"], "scheduled_at": request.scheduled_at, "duration_minutes": request.duration_minutes, "amount_paid": total_cost, "status": "scheduled"}
    result = supabase.table("tutor_sessions").insert(session_data).execute()
    session = result.data[0]
    supabase.table("users").update({"coins_balance": current_user["coins_balance"] - total_cost}).eq("id", current_user["id"]).execute()
    return {"success": True, "session": session, "coins_deducted": total_cost, "coins_remaining": current_user["coins_balance"] - total_cost}


@router.put("/tutor/session/{session_id}/complete", summary="Mark session as completed with rating")
async def complete_session(
    session_id: str,
    request: CompleteSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    validate_rating(request.rating)
    result = supabase.table("tutor_sessions").select("*, tutors(user_id, rating, total_sessions)").eq("id", session_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found.")
    session = result.data[0]
    tutor_user_id = (session.get("tutors") or {}).get("user_id")
    if current_user["id"] not in [session["learner_id"], tutor_user_id]:
        raise HTTPException(status_code=403, detail="Not authorized to complete this session.")
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Session is already completed.")
    supabase.table("tutor_sessions").update({"status": "completed", "completed_at": datetime.utcnow().isoformat(), "feedback": request.feedback}).eq("id", session_id).execute()
    tutor_data = session.get("tutors") or {}
    old_rating = tutor_data.get("rating", 0) or 0
    old_count = tutor_data.get("total_sessions", 0) or 0
    new_count = old_count + 1
    new_rating = ((old_rating * old_count) + request.rating) / new_count
    supabase.table("tutors").update({"rating": round(new_rating, 2), "total_sessions": new_count}).eq("id", session["tutor_id"]).execute()
    if session.get("amount_paid") and tutor_user_id:
        tutor_user = supabase.table("users").select("coins_balance").eq("id", tutor_user_id).execute()
        if tutor_user.data:
            current_balance = tutor_user.data[0]["coins_balance"]
            supabase.table("users").update({"coins_balance": current_balance + session["amount_paid"]}).eq("id", tutor_user_id).execute()
    return {"success": True, "session_id": session_id, "rating_given": request.rating, "tutor_new_rating": round(new_rating, 2), "coins_transferred": session.get("amount_paid", 0)}


@router.get("/tutor/sessions/history", summary="Get session history for learner or tutor")
async def get_sessions_history(
    role: str = Query("learner"),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    current_user: dict = Depends(get_current_user)
):
    limit = 20
    offset = (page - 1) * limit
    if role == "tutor":
        tutor_result = supabase.table("tutors").select("id").eq("user_id", current_user["id"]).execute()
        if not tutor_result.data:
            return {"success": True, "sessions": [], "message": "You are not registered as a tutor."}
        tutor_id = tutor_result.data[0]["id"]
        query = supabase.table("tutor_sessions").select("*, users!tutor_sessions_learner_id_fkey(name, phone)").eq("tutor_id", tutor_id)
    else:
        query = supabase.table("tutor_sessions").select("*, tutors(*, users(name))").eq("learner_id", current_user["id"])
    if status:
        query = query.eq("status", status)
    result = query.order("scheduled_at", desc=True).range(offset, offset + limit - 1).execute()
    return {"success": True, "sessions": result.data or [], "role": role, "pagination": {"page": page, "per_page": limit}}