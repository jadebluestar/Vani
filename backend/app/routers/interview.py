import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from loguru import logger

from app.dependencies import get_current_user
from app.database import supabase
from app.services.llm_service import llm_service
from app.services.progress_service import progress_service
from app.websocket_manager import interview_manager
from app.utils.validators import validate_language_code, sanitize_text_input

router = APIRouter(prefix="/interview", tags=["Interview"])

INTERVIEW_QUESTIONS = [
    {"id": "q001", "question": "Tell me about yourself and your background.", "category": "behavioral", "difficulty": 1},
    {"id": "q002", "question": "What are your greatest strengths?", "category": "behavioral", "difficulty": 1},
    {"id": "q003", "question": "Describe a challenging situation you faced and how you handled it.", "category": "situational", "difficulty": 2},
    {"id": "q004", "question": "Where do you see yourself in 5 years?", "category": "behavioral", "difficulty": 2},
    {"id": "q005", "question": "Why do you want to work for this company?", "category": "behavioral", "difficulty": 2},
    {"id": "q006", "question": "Tell me about a time you worked in a team.", "category": "behavioral", "difficulty": 2},
    {"id": "q007", "question": "How do you handle stress and pressure at work?", "category": "situational", "difficulty": 3},
    {"id": "q008", "question": "What is your biggest weakness and how are you working on it?", "category": "behavioral", "difficulty": 3},
    {"id": "q009", "question": "Describe your ideal work environment.", "category": "behavioral", "difficulty": 2},
    {"id": "q010", "question": "How do you prioritize your tasks when you have multiple deadlines?", "category": "situational", "difficulty": 3},
    {"id": "q011", "question": "Tell me about a time you showed leadership.", "category": "behavioral", "difficulty": 3},
    {"id": "q012", "question": "How do you handle criticism from your manager?", "category": "situational", "difficulty": 4},
    {"id": "q013", "question": "Describe a project you're most proud of.", "category": "behavioral", "difficulty": 3},
    {"id": "q014", "question": "What motivates you in your work?", "category": "behavioral", "difficulty": 1},
    {"id": "q015", "question": "How would your previous colleagues describe you?", "category": "behavioral", "difficulty": 3},
]


class InterviewRespondRequest(BaseModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    user_answer: str
    category: str = "behavioral"
    difficulty: int = 1
    language: str = "en"


@router.get("/questions", summary="Get interview questions with filters")
async def get_questions(
    category: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    language: Optional[str] = Query("en"),
    limit: int = Query(10, le=50),
    current_user: dict = Depends(get_current_user)
):
    questions = INTERVIEW_QUESTIONS.copy()
    if category:
        questions = [q for q in questions if q["category"] == category]
    if difficulty:
        questions = [q for q in questions if q["difficulty"] == difficulty]
    if language and language != "en":
        try:
            ai_question = await llm_service.get_next_interview_question(
                category=category or "behavioral",
                difficulty=difficulty or 2,
                previous_questions=[q["question"] for q in questions[:5]],
                language_code=language
            )
            questions.insert(0, {"id": f"ai_{uuid.uuid4().hex[:8]}", "question": ai_question, "category": category or "behavioral", "difficulty": difficulty or 2, "ai_generated": True})
        except Exception as e:
            logger.warning(f"Could not generate AI question: {e}")
    return {"success": True, "questions": questions[:limit], "total": len(questions)}


@router.post("/respond", summary="Submit interview answer and get feedback")
async def interview_respond(
    request: InterviewRespondRequest,
    current_user: dict = Depends(get_current_user)
):
    user_answer = sanitize_text_input(request.user_answer, max_length=3000)
    language = validate_language_code(request.language)
    question_text = request.question_text
    if not question_text and request.question_id:
        q_match = next((q for q in INTERVIEW_QUESTIONS if q["id"] == request.question_id), None)
        question_text = q_match["question"] if q_match else "Tell me about yourself."
    if not question_text:
        question_text = "Tell me about yourself."
    try:
        evaluation = await llm_service.evaluate_interview_answer(
            question=question_text,
            answer=user_answer,
            category=request.category,
            difficulty=request.difficulty,
            language_code=language
        )
        score = evaluation.get("score", 50)
        interview_data = {
            "user_id": current_user["id"],
            "question": question_text,
            "user_answer": user_answer,
            "ai_feedback": json.dumps(evaluation),
            "question_category": request.category,
            "difficulty_level": request.difficulty,
            "score": score,
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", [])
        }
        result = supabase.table("interviews").insert(interview_data).execute()
        interview_id = result.data[0]["id"] if result.data else None
        try:
            await progress_service.update_skill_scores(current_user["id"], {
                "speaking": score,
                "vocabulary": evaluation.get("content_score", score),
                "fluency": evaluation.get("communication_score", score)
            })
        except Exception as e:
            logger.warning(f"Progress update failed: {e}")
        return {"success": True, "interview_id": interview_id, "score": score, "evaluation": evaluation, "question": question_text}
    except Exception as e:
        logger.error(f"Interview evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/feedback/{interview_id}", summary="Get detailed feedback for an interview response")
async def get_interview_feedback(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = supabase.table("interviews").select("*").eq("id", interview_id).eq("user_id", current_user["id"]).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Interview record not found.")
    record = result.data[0]
    try:
        if isinstance(record["ai_feedback"], str):
            record["ai_feedback"] = json.loads(record["ai_feedback"])
    except Exception:
        pass
    return {"success": True, "interview": record}


@router.websocket("/live/{session_id}")
async def live_interview_ws(websocket: WebSocket, session_id: str):
    user_id = None
    try:
        init_msg = await websocket.receive_json()
        if init_msg.get("type") != "join":
            await websocket.send_json({"type": "error", "message": "First message must be {type: 'join'}"})
            await websocket.close()
            return
        token = init_msg.get("token", "")
        from jose import jwt as jose_jwt
        from app.config import settings as app_settings
        try:
            payload = jose_jwt.decode(token, app_settings.JWT_SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
        except Exception:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return
        await interview_manager.connect(websocket, session_id, user_id)
        category = init_msg.get("category", "behavioral")
        language = init_msg.get("language", "en")
        difficulty = init_msg.get("difficulty", 2)
        interview_manager.set_session_metadata(session_id, {"user_id": user_id, "category": category, "language": language, "difficulty": difficulty, "questions_asked": [], "scores": [], "question_num": 0})
        await websocket.send_json({"type": "connected", "message": "Welcome to your AI interview session!", "session_id": session_id})
        meta = interview_manager.get_session_metadata(session_id)
        question = await llm_service.get_next_interview_question(category=category, difficulty=difficulty, previous_questions=[], language_code=language)
        meta["question_num"] = 1
        meta["current_question"] = question
        meta["questions_asked"].append(question)
        interview_manager.set_session_metadata(session_id, meta)
        await websocket.send_json({"type": "question", "question": question, "question_num": 1, "total_questions": 5})
        while True:
            msg = await websocket.receive_json()
            meta = interview_manager.get_session_metadata(session_id)
            if msg.get("type") == "answer":
                answer = msg.get("text", "").strip()
                if not answer:
                    continue
                current_q = meta.get("current_question", "")
                await websocket.send_json({"type": "thinking", "message": "Analyzing your answer..."})
                try:
                    evaluation = await llm_service.evaluate_interview_answer(question=current_q, answer=answer, category=category, difficulty=difficulty, language_code=language)
                    score = evaluation.get("score", 50)
                    meta["scores"].append(score)
                    supabase.table("interviews").insert({"user_id": user_id, "question": current_q, "user_answer": answer, "ai_feedback": json.dumps(evaluation), "question_category": category, "difficulty_level": difficulty, "score": score}).execute()
                    await websocket.send_json({"type": "feedback", "score": score, "evaluation": evaluation, "question_num": meta["question_num"]})
                    if meta["question_num"] >= 5:
                        avg_score = sum(meta["scores"]) / len(meta["scores"]) if meta["scores"] else 0
                        await websocket.send_json({"type": "complete", "summary": {"total_questions": 5, "average_score": round(avg_score, 1), "scores": meta["scores"]}})
                        break
                except Exception as e:
                    logger.error(f"WS evaluation error: {e}")
                    await websocket.send_json({"type": "error", "message": "Evaluation failed"})
            elif msg.get("type") == "next":
                if meta["question_num"] >= 5:
                    continue
                next_q = await llm_service.get_next_interview_question(category=category, difficulty=difficulty, previous_questions=meta["questions_asked"], language_code=language)
                meta["question_num"] += 1
                meta["current_question"] = next_q
                meta["questions_asked"].append(next_q)
                interview_manager.set_session_metadata(session_id, meta)
                await websocket.send_json({"type": "question", "question": next_q, "question_num": meta["question_num"], "total_questions": 5})
            elif msg.get("type") == "disconnect":
                break
    except WebSocketDisconnect:
        logger.info(f"WS disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        interview_manager.disconnect(websocket, session_id)


@router.get("/history", summary="Get interview history with scores")
async def get_interview_history(
    page: int = Query(1, ge=1),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    limit = 20
    offset = (page - 1) * limit
    query = supabase.table("interviews").select("id, question, score, question_category, difficulty_level, strengths, improvements, created_at").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + limit - 1)
    if category:
        query = query.eq("question_category", category)
    result = query.execute()
    records = result.data or []
    for r in records:
        for field in ["strengths", "improvements"]:
            if isinstance(r.get(field), str):
                try:
                    r[field] = json.loads(r[field])
                except Exception:
                    pass
    count_result = supabase.table("interviews").select("id", count="exact").eq("user_id", current_user["id"]).execute()
    total = count_result.count or 0
    avg_score = sum(r["score"] for r in records if r.get("score")) / len(records) if records else 0
    return {"success": True, "interviews": records, "average_score": round(avg_score, 1), "pagination": {"page": page, "per_page": limit, "total": total, "pages": (total + limit - 1) // limit}}