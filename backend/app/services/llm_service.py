import json
import re
import random
import time
from typing import Optional, Dict, Any
from loguru import logger
import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception

try:
    import groq
    from groq import AsyncGroq
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False

from app.config import settings

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
_OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"

# Errors worth retrying: timeouts, connection drops, 429s, and 5xx — all
# transient. Auth/validation errors (4xx other than 429) are not retried
# since a retry can't fix a bad API key or a malformed request.
_RETRYABLE_TRANSPORT_ERRORS = tuple(
    exc for exc in (
        httpx.TimeoutException,
        httpx.ConnectError,
        getattr(groq, "APIConnectionError", None) if _GROQ_AVAILABLE else None,
        getattr(groq, "APITimeoutError", None) if _GROQ_AVAILABLE else None,
        getattr(groq, "RateLimitError", None) if _GROQ_AVAILABLE else None,
        getattr(groq, "InternalServerError", None) if _GROQ_AVAILABLE else None,
    )
    if exc is not None
)


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, _RETRYABLE_TRANSPORT_ERRORS):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False


class _CircuitBreaker:
    """
    Trips after consecutive upstream failures. While open, calls skip the
    network entirely and fall straight through to the mock response instead
    of paying (retry attempts x timeout) latency on every request during an
    LLM provider outage. Half-opens after `recovery_seconds` to probe recovery.
    """

    def __init__(self, failure_threshold: int = 5, recovery_seconds: float = 30.0):
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._consecutive_failures = 0
        self._opened_at: Optional[float] = None

    def allow_request(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self._recovery_seconds:
            return True
        return False

    def record_success(self):
        if self._consecutive_failures or self._opened_at:
            logger.info("LLM circuit breaker reset after successful call")
        self._consecutive_failures = 0
        self._opened_at = None

    def record_failure(self):
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._failure_threshold and self._opened_at is None:
            self._opened_at = time.monotonic()
            logger.warning(
                f"LLM circuit breaker OPEN after {self._consecutive_failures} consecutive failures "
                f"— falling back to mock responses for {self._recovery_seconds}s"
            )


# ─── Mock responses used when Groq is unavailable ────────────────────────────

_MOCK_FEEDBACK = {
    "fluency_score": 72.0,
    "pronunciation_score": 68.0,
    "grammar_score": 70.0,
    "overall_score": 70.0,
    "filler_words": {"count": 0, "words_found": []},
    "strengths": ["Clear sentence structure", "Good vocabulary range"],
    "improvements": ["Work on speaking pace", "Reduce hesitations"],
    "tips": "Keep practicing! Try reading aloud daily to improve fluency.",
    "confidence_level": {"level": "Intermediate", "description": "Improving steadily, great progress"},
}

_MOCK_EVALUATION = {
    "score": 70,
    "content_score": 68,
    "communication_score": 72,
    "strengths": ["Shows self-awareness", "Structured answer"],
    "improvements": ["Add specific examples", "Be more concise"],
    "overall_feedback": "Good attempt. Focus on giving concrete examples from your experience.",
    "star_method_used": False,
    "confidence_level": "Intermediate",
}

_MOCK_QUESTIONS = [
    "Tell me about a time you faced a challenge and how you overcame it.",
    "Describe a situation where you had to work under pressure.",
    "What is your greatest professional achievement so far?",
    "How do you handle disagreements with colleagues?",
    "Where do you see yourself growing in the next two years?",
]

_MOCK_CONVERSATION_REPLIES = [
    "That's a great point! Can you tell me more about your experience with that?",
    "I understand. How did that make you feel, and what did you learn from it?",
    "Excellent! Let's practice expressing that idea more formally in English.",
    "Good effort! Try rephrasing that using more professional vocabulary.",
    "Well said! Now let's work on making your delivery even more confident.",
]

_MOCK_FLUENCY = {
    "fluency_score": 70.0,
    "pace": "moderate",
    "clarity": "good",
    "vocabulary_range": "intermediate",
    "suggestions": ["Maintain a steady pace", "Pause naturally between ideas"],
}

_MOCK_RECOMMENDATIONS = [
    {"priority": "high", "skill": "speaking", "recommendation": "Practice 5 minutes of daily conversation", "time_required": "5 min", "exercise_type": "speaking"},
    {"priority": "high", "skill": "fluency", "recommendation": "Read a paragraph aloud and record yourself", "time_required": "10 min", "exercise_type": "speaking"},
    {"priority": "medium", "skill": "vocabulary", "recommendation": "Learn 5 new professional English words each day", "time_required": "5 min", "exercise_type": "vocabulary"},
]


class LLMService:
    """LLM service supporting OpenRouter (sk-or-) or Groq (gsk_), with mock fallback."""

    def __init__(self):
        self._client = None
        self._mock_mode = True
        self._backend = None  # "openrouter" | "groq" | None
        self.model = "llama-3.3-70b-versatile"
        self.max_tokens = 2048
        self._breaker = _CircuitBreaker(failure_threshold=5, recovery_seconds=30.0)
        key = settings.GROQ_API_KEY or ""

        if key.startswith("sk-or-"):
            self._backend = "openrouter"
            self._mock_mode = False
            logger.info("LLM service using OpenRouter")
        elif key.startswith("gsk_") and _GROQ_AVAILABLE:
            try:
                self._client = AsyncGroq(api_key=key)
                self._backend = "groq"
                self._mock_mode = False
                logger.info("LLM service using Groq")
            except Exception as e:
                logger.warning(f"Groq init failed: {e} — using mock responses")
        else:
            logger.warning("No valid LLM API key found — using mock responses")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        if self._mock_mode:
            return random.choice(_MOCK_CONVERSATION_REPLIES)

        if not self._breaker.allow_request():
            logger.warning("LLM circuit breaker open — skipping call, returning mock response")
            return random.choice(_MOCK_CONVERSATION_REPLIES)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        call = self._generate_openrouter if self._backend == "openrouter" else self._generate_groq
        try:
            result = await self._call_with_retry(call, messages, temperature, max_tokens)
            self._breaker.record_success()
            return result
        except Exception as e:
            self._breaker.record_failure()
            logger.error(f"LLM error ({self._backend}) after retries: {e} — returning mock response")
            return random.choice(_MOCK_CONVERSATION_REPLIES)

    @staticmethod
    async def _call_with_retry(func, *args):
        """Retries transient upstream errors (timeouts, 429, 5xx) with exponential backoff."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        ):
            with attempt:
                return await func(*args)

    async def _generate_groq(self, messages: list, temperature: float, max_tokens=None) -> str:
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        return response.choices[0].message.content.strip()

    async def _generate_openrouter(self, messages: list, temperature: float, max_tokens=None) -> str:
        key = settings.GROQ_API_KEY
        payload = {
            "model": _OPENROUTER_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{_OPENROUTER_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vani.app",
                    "X-Title": "Vani",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        if self._mock_mode:
            return _MOCK_FEEDBACK.copy()
        raw = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt or "You are a helpful AI assistant. Always respond with valid JSON only.",
            temperature=temperature,
        )
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            logger.warning("Could not parse LLM response as JSON, using mock feedback")
            return _MOCK_FEEDBACK.copy()

    async def generate_speech_feedback(self, text: str, language_code: str) -> Dict[str, Any]:
        if self._mock_mode:
            return _MOCK_FEEDBACK.copy()
        from app.utils.prompts import get_speech_feedback_prompt
        prompt = get_speech_feedback_prompt(text, language_code)
        try:
            return await self.generate_json(prompt, temperature=0.3)
        except Exception:
            return _MOCK_FEEDBACK.copy()

    async def generate_conversation_response(
        self, user_message: str, language_code: str, history: list = None
    ) -> str:
        if self._mock_mode:
            return random.choice(_MOCK_CONVERSATION_REPLIES)
        from app.utils.prompts import get_conversation_response_prompt
        prompt = get_conversation_response_prompt(user_message, language_code, history)
        try:
            return await self.generate(prompt, temperature=0.8)
        except Exception:
            return random.choice(_MOCK_CONVERSATION_REPLIES)

    async def evaluate_interview_answer(
        self, question: str, answer: str, category: str, difficulty: int, language_code: str
    ) -> Dict[str, Any]:
        if self._mock_mode:
            return _MOCK_EVALUATION.copy()
        from app.utils.prompts import get_interview_feedback_prompt
        prompt = get_interview_feedback_prompt(question, answer, category, difficulty, language_code)
        try:
            return await self.generate_json(prompt, temperature=0.3)
        except Exception:
            return _MOCK_EVALUATION.copy()

    async def get_next_interview_question(
        self, category: str, difficulty: int, previous_questions: list, language_code: str
    ) -> str:
        if self._mock_mode:
            return random.choice(_MOCK_QUESTIONS)
        from app.utils.prompts import get_live_interview_question_prompt
        prompt = get_live_interview_question_prompt(category, difficulty, previous_questions, language_code)
        try:
            return await self.generate(prompt, temperature=0.9)
        except Exception:
            return random.choice(_MOCK_QUESTIONS)

    async def get_recommendations(self, skill_scores: dict, language_code: str) -> list:
        if self._mock_mode:
            return _MOCK_RECOMMENDATIONS.copy()
        from app.utils.prompts import get_progress_recommendations_prompt
        prompt = get_progress_recommendations_prompt(skill_scores, language_code)
        try:
            result = await self.generate_json(prompt, temperature=0.5)
            return result if isinstance(result, list) else result.get("recommendations", _MOCK_RECOMMENDATIONS)
        except Exception:
            return _MOCK_RECOMMENDATIONS.copy()

    async def analyze_fluency(
        self, text: str, word_count: int, duration_seconds: float, language_code: str
    ) -> Dict[str, Any]:
        if self._mock_mode:
            return _MOCK_FLUENCY.copy()
        from app.utils.prompts import get_fluency_analysis_prompt
        prompt = get_fluency_analysis_prompt(text, word_count, duration_seconds, language_code)
        try:
            return await self.generate_json(prompt, temperature=0.2)
        except Exception:
            return _MOCK_FLUENCY.copy()


llm_service = LLMService()
