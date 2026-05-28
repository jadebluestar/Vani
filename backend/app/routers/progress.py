from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from app.dependencies import get_current_user
from app.services.progress_service import progress_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/dashboard", summary="Get user progress dashboard data")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        stats = await progress_service.get_user_stats(current_user["id"])
        skill_data = await progress_service.get_skill_breakdown(current_user["id"])
        return {
            "success": True,
            "dashboard": {
                "user_name": current_user.get("name", "Learner"),
                "preferred_language": current_user.get("preferred_language", "en"),
                "total_practice_minutes": stats["practice_minutes"],
                "total_sessions": stats["total_sessions"],
                "confidence_score": stats["confidence_score"],
                "streak_days": stats["streak_days"],
                "coins_balance": current_user.get("coins_balance", 0),
                "weekly_activity": stats["weekly_activity"],
                "session_breakdown": {
                    "conversations": stats["conversations_count"],
                    "interviews": stats["interviews_count"],
                    "tutor_sessions": stats["tutor_sessions_count"]
                },
                "skill_summary": {k: v["score"] for k, v in skill_data.get("skills", {}).items()}
            }
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Could not load dashboard data.")


@router.get("/skills", summary="Get detailed skill scores for radar chart")
async def get_skills(current_user: dict = Depends(get_current_user)):
    try:
        skill_data = await progress_service.get_skill_breakdown(current_user["id"])
        return {"success": True, "skills": skill_data["skills"], "radar_chart_data": skill_data["radar_chart_data"], "user_id": current_user["id"]}
    except Exception as e:
        logger.error(f"Skills error: {e}")
        raise HTTPException(status_code=500, detail="Could not load skill data.")


@router.get("/confidence-timeline", summary="Get 30-day confidence score timeline")
async def get_confidence_timeline(
    days: int = Query(30, ge=7, le=90),
    current_user: dict = Depends(get_current_user)
):
    try:
        timeline = await progress_service.get_confidence_timeline(current_user["id"], days)
        scores_with_data = [t["confidence"] for t in timeline if t["confidence"] is not None]
        if len(scores_with_data) >= 2:
            first_half = scores_with_data[:len(scores_with_data)//2]
            second_half = scores_with_data[len(scores_with_data)//2:]
            trend = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
        else:
            trend = 0
        return {"success": True, "timeline": timeline, "days": days, "trend": round(trend, 1), "trend_direction": "up" if trend > 1 else ("down" if trend < -1 else "stable"), "data_points": len(scores_with_data)}
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        raise HTTPException(status_code=500, detail="Could not load confidence timeline.")


@router.get("/recommendations", summary="Get AI-powered practice recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    try:
        skill_data = await progress_service.get_skill_breakdown(current_user["id"])
        skill_scores = {k: v["score"] for k, v in skill_data.get("skills", {}).items()}
        language = current_user.get("preferred_language", "en")
        recommendations = await llm_service.get_recommendations(skill_scores, language)
        if not recommendations or not skill_scores:
            recommendations = [
                {"priority": "high", "skill": "speaking", "recommendation": "Start with 5 minutes of daily conversation practice in your native language", "time_required": "5 minutes", "exercise_type": "speaking"},
                {"priority": "high", "skill": "fluency", "recommendation": "Read a short paragraph aloud and record yourself to hear your progress", "time_required": "10 minutes", "exercise_type": "speaking"},
                {"priority": "medium", "skill": "vocabulary", "recommendation": "Learn 5 new professional English words each day with pronunciation", "time_required": "5 minutes", "exercise_type": "vocabulary"},
                {"priority": "medium", "skill": "grammar", "recommendation": "Practice forming sentences using past, present, and future tenses", "time_required": "10 minutes", "exercise_type": "grammar"},
                {"priority": "low", "skill": "pronunciation", "recommendation": "Focus on commonly mispronounced English sounds", "time_required": "5 minutes", "exercise_type": "speaking"}
            ]
        return {"success": True, "recommendations": recommendations, "based_on": skill_scores, "language": language}
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Could not generate recommendations.")