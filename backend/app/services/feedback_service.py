import re
from typing import Dict, Any, List
from loguru import logger


class FeedbackService:
    """Enriches and processes speech/interview feedback from the LLM."""

    FILLER_WORDS = {
        "en": ["um", "uh", "like", "you know", "basically", "actually", "literally", "sort of", "kind of"],
        "hi": ["matlab", "woh", "aur", "toh", "haan", "accha", "bas"],
        "kn": ["andre", "enu", "hage", "heli"],
        "ta": ["enna", "pakku", "sari"],
        "te": ["ante", "emi", "ayye"],
        "ml": ["ennu", "avar", "oke"],
        "bn": ["mane", "hyan", "aar"],
        "mr": ["mhanje", "haa", "aani"],
    }

    def count_filler_words(self, text: str, language_code: str) -> Dict[str, Any]:
        text_lower = text.lower()
        fillers = self.FILLER_WORDS.get(language_code, []) + self.FILLER_WORDS.get("en", [])
        found = []
        count = 0
        for filler in fillers:
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = re.findall(pattern, text_lower)
            if matches:
                found.extend(matches)
                count += len(matches)
        return {"count": count, "words_found": list(set(found))}

    def calculate_speaking_rate(self, text: str, duration_seconds: float) -> Dict[str, Any]:
        if duration_seconds <= 0:
            return {"wpm": 0, "assessment": "unknown", "ideal_range": "120-150"}
        word_count = len(text.split())
        wpm = (word_count / duration_seconds) * 60
        if wpm < 80:
            assessment = "too_slow"
            tip = "Try to speak a bit faster for a more natural flow"
        elif wpm < 120:
            assessment = "slightly_slow"
            tip = "Good pace, you can speed up slightly"
        elif wpm <= 160:
            assessment = "ideal"
            tip = "Excellent speaking rate!"
        elif wpm <= 200:
            assessment = "slightly_fast"
            tip = "Slow down a little for better clarity"
        else:
            assessment = "too_fast"
            tip = "Slow down significantly for better comprehension"
        return {"wpm": round(wpm, 1), "word_count": word_count, "duration_seconds": duration_seconds, "assessment": assessment, "tip": tip, "ideal_range": "120-160 WPM"}

    def calculate_overall_score(self, fluency: float, pronunciation: float, grammar: float) -> float:
        return round(fluency * 0.40 + pronunciation * 0.30 + grammar * 0.30, 1)

    def get_confidence_level(self, score: float) -> Dict[str, str]:
        if score >= 85:
            return {"level": "Advanced", "description": "Excellent communication skills"}
        elif score >= 70:
            return {"level": "Proficient", "description": "Good communication skills, keep practicing"}
        elif score >= 55:
            return {"level": "Intermediate", "description": "Improving steadily, great progress"}
        elif score >= 40:
            return {"level": "Beginner", "description": "Building foundation, you're on the right track"}
        else:
            return {"level": "Starter", "description": "Just starting out, every practice counts"}

    def enrich_feedback(self, ai_feedback: dict, text: str, language_code: str, duration_seconds: float = 0) -> dict:
        if "filler_words" not in ai_feedback or not ai_feedback["filler_words"]:
            ai_feedback["filler_words"] = self.count_filler_words(text, language_code)
        if duration_seconds > 0:
            ai_feedback["speaking_rate"] = self.calculate_speaking_rate(text, duration_seconds)
        if "overall_score" not in ai_feedback:
            ai_feedback["overall_score"] = self.calculate_overall_score(
                ai_feedback.get("fluency_score", 0),
                ai_feedback.get("pronunciation_score", 0),
                ai_feedback.get("grammar_score", 0)
            )
        ai_feedback["confidence_level"] = self.get_confidence_level(ai_feedback["overall_score"])
        return ai_feedback


feedback_service = FeedbackService()