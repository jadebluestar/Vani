from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from loguru import logger
from app.database import supabase


class ProgressService:
    """Handles all progress tracking calculations."""

    SKILL_NAMES = ["speaking", "listening", "vocabulary", "grammar", "pronunciation", "fluency"]

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        try:
            conv_result = supabase.table("conversations").select("id, created_at, fluency_score, grammar_score, pronunciation_score").eq("user_id", user_id).execute()
            conversations = conv_result.data or []
            int_result = supabase.table("interviews").select("id, created_at, score").eq("user_id", user_id).execute()
            interviews = int_result.data or []
            session_result = supabase.table("tutor_sessions").select("id, created_at, duration_minutes").eq("learner_id", user_id).eq("status", "completed").execute()
            tutor_sessions = session_result.data or []
            total_sessions = len(conversations) + len(interviews) + len(tutor_sessions)
            practice_minutes = len(conversations) * 5 + len(interviews) * 10 + sum(s.get("duration_minutes", 0) or 0 for s in tutor_sessions)
            confidence_score = self._calculate_confidence(conversations, interviews)
            all_dates = [c["created_at"][:10] for c in conversations + interviews]
            streak = self._calculate_streak(all_dates)
            weekly_activity = self._get_weekly_activity(conversations + interviews)
            return {
                "total_sessions": total_sessions, "practice_minutes": practice_minutes, "confidence_score": confidence_score,
                "streak_days": streak, "weekly_activity": weekly_activity, "conversations_count": len(conversations),
                "interviews_count": len(interviews), "tutor_sessions_count": len(tutor_sessions)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"total_sessions": 0, "practice_minutes": 0, "confidence_score": 0, "streak_days": 0, "weekly_activity": [], "conversations_count": 0, "interviews_count": 0, "tutor_sessions_count": 0}

    def _calculate_confidence(self, conversations: list, interviews: list) -> float:
        scores = []
        for c in conversations[-20:]:
            if c.get("fluency_score"):
                scores.append(c["fluency_score"])
            if c.get("grammar_score"):
                scores.append(c["grammar_score"])
        for i in interviews[-10:]:
            if i.get("score"):
                scores.append(i["score"])
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 1)

    def _calculate_streak(self, date_strings: list) -> int:
        if not date_strings:
            return 0
        unique_dates = sorted(set(date_strings), reverse=True)
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if unique_dates[0] not in [today, yesterday]:
            return 0
        streak = 1
        for i in range(1, len(unique_dates)):
            expected = (date.fromisoformat(unique_dates[i-1]) - timedelta(days=1)).isoformat()
            if unique_dates[i] == expected:
                streak += 1
            else:
                break
        return streak

    def _get_weekly_activity(self, records: list) -> List[Dict]:
        today = date.today()
        activity = {}
        for i in range(7):
            day = (today - timedelta(days=i)).isoformat()
            activity[day] = 0
        for record in records:
            record_date = record.get("created_at", "")[:10]
            if record_date in activity:
                activity[record_date] += 1
        return [{"date": d, "count": c, "day": date.fromisoformat(d).strftime("%a")} for d, c in sorted(activity.items())]

    async def get_skill_breakdown(self, user_id: str) -> Dict[str, Any]:
        try:
            result = supabase.table("progress").select("*").eq("user_id", user_id).execute()
            progress_records = {r["skill"]: r for r in (result.data or [])}
            skill_data = {}
            for skill in self.SKILL_NAMES:
                if skill in progress_records:
                    record = progress_records[skill]
                    skill_data[skill] = {"score": record["score"], "trend": record.get("trend", 0), "history": record.get("history", [])}
                else:
                    skill_data[skill] = {"score": 0, "trend": 0, "history": []}
            radar_data = [{"skill": k.capitalize(), "score": v["score"], "fullMark": 100} for k, v in skill_data.items()]
            return {"skills": skill_data, "radar_chart_data": radar_data}
        except Exception as e:
            logger.error(f"Error getting skill breakdown: {e}")
            return {"skills": {}, "radar_chart_data": []}

    async def update_skill_scores(self, user_id: str, scores: Dict[str, float]):
        try:
            for skill, new_score in scores.items():
                existing = supabase.table("progress").select("*").eq("user_id", user_id).eq("skill", skill).execute()
                if existing.data:
                    record = existing.data[0]
                    history = record.get("history", [])
                    history.append({"score": new_score, "date": datetime.utcnow().isoformat()})
                    history = history[-30:]
                    recent = [h["score"] for h in history[-5:]]
                    older = [h["score"] for h in history[-10:-5]] if len(history) > 5 else recent
                    trend = (sum(recent) / len(recent)) - (sum(older) / len(older)) if older else 0
                    supabase.table("progress").update({"score": new_score, "trend": round(trend, 1), "history": history, "updated_at": datetime.utcnow().isoformat()}).eq("id", record["id"]).execute()
                else:
                    supabase.table("progress").insert({"user_id": user_id, "skill": skill, "score": new_score, "trend": 0, "history": [{"score": new_score, "date": datetime.utcnow().isoformat()}]}).execute()
        except Exception as e:
            logger.error(f"Error updating skill scores: {e}")

    async def get_confidence_timeline(self, user_id: str, days: int = 30) -> List[Dict]:
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            conv_result = supabase.table("conversations").select("created_at, fluency_score, grammar_score").eq("user_id", user_id).gte("created_at", cutoff).execute()
            int_result = supabase.table("interviews").select("created_at, score").eq("user_id", user_id).gte("created_at", cutoff).execute()
            daily_scores: Dict[str, list] = {}
            for record in (conv_result.data or []):
                day = record["created_at"][:10]
                if day not in daily_scores:
                    daily_scores[day] = []
                if record.get("fluency_score"):
                    daily_scores[day].append(record["fluency_score"])
                if record.get("grammar_score"):
                    daily_scores[day].append(record["grammar_score"])
            for record in (int_result.data or []):
                day = record["created_at"][:10]
                if day not in daily_scores:
                    daily_scores[day] = []
                if record.get("score"):
                    daily_scores[day].append(record["score"])
            timeline = []
            today = date.today()
            for i in range(days):
                day = (today - timedelta(days=days-1-i)).isoformat()
                scores = daily_scores.get(day, [])
                timeline.append({"date": day, "confidence": round(sum(scores) / len(scores), 1) if scores else None, "sessions": len(scores)})
            return timeline
        except Exception as e:
            logger.error(f"Error getting confidence timeline: {e}")
            return []


progress_service = ProgressService()