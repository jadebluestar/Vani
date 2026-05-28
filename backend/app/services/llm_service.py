import json
import re
from groq import AsyncGroq
from app.config import settings
from loguru import logger
from typing import Optional, Dict, Any


class LLMService:
    """Service for interacting with Groq's Llama 3.3 70B model."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.max_tokens = 2048

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens or self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq LLM error: {e}")
            raise

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> Dict[str, Any]:
        raw = await self.generate(prompt=prompt, system_prompt=system_prompt or "You are a helpful AI assistant. Always respond with valid JSON only.", temperature=temperature)
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            raise ValueError(f"Could not parse AI response as JSON: {str(e)}")

    async def generate_speech_feedback(self, text: str, language_code: str) -> Dict[str, Any]:
        from app.utils.prompts import get_speech_feedback_prompt
        prompt = get_speech_feedback_prompt(text, language_code)
        return await self.generate_json(prompt, temperature=0.3)

    async def generate_conversation_response(self, user_message: str, language_code: str, history: list = None) -> str:
        from app.utils.prompts import get_conversation_response_prompt
        prompt = get_conversation_response_prompt(user_message, language_code, history)
        return await self.generate(prompt, temperature=0.8)

    async def evaluate_interview_answer(self, question: str, answer: str, category: str, difficulty: int, language_code: str) -> Dict[str, Any]:
        from app.utils.prompts import get_interview_feedback_prompt
        prompt = get_interview_feedback_prompt(question, answer, category, difficulty, language_code)
        return await self.generate_json(prompt, temperature=0.3)

    async def get_next_interview_question(self, category: str, difficulty: int, previous_questions: list, language_code: str) -> str:
        from app.utils.prompts import get_live_interview_question_prompt
        prompt = get_live_interview_question_prompt(category, difficulty, previous_questions, language_code)
        return await self.generate(prompt, temperature=0.9)

    async def get_recommendations(self, skill_scores: dict, language_code: str) -> list:
        from app.utils.prompts import get_progress_recommendations_prompt
        prompt = get_progress_recommendations_prompt(skill_scores, language_code)
        result = await self.generate_json(prompt, temperature=0.5)
        return result if isinstance(result, list) else result.get("recommendations", [])

    async def analyze_fluency(self, text: str, word_count: int, duration_seconds: float, language_code: str) -> Dict[str, Any]:
        from app.utils.prompts import get_fluency_analysis_prompt
        prompt = get_fluency_analysis_prompt(text, word_count, duration_seconds, language_code)
        return await self.generate_json(prompt, temperature=0.2)


llm_service = LLMService()