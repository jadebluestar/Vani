from app.services.llm_service import LLMService, _is_retryable, _CircuitBreaker
import httpx


def test_llm_service_defaults_to_mock_mode_without_a_valid_key():
    service = LLMService()
    assert service._mock_mode is True


async def test_generate_returns_a_string_in_mock_mode():
    service = LLMService()
    reply = await service.generate("hello")
    assert isinstance(reply, str)
    assert len(reply) > 0


async def test_generate_speech_feedback_shape_in_mock_mode():
    service = LLMService()
    feedback = await service.generate_speech_feedback("I am learning English", "en")
    for key in ("fluency_score", "pronunciation_score", "grammar_score", "strengths", "improvements"):
        assert key in feedback


async def test_evaluate_interview_answer_shape_in_mock_mode():
    service = LLMService()
    evaluation = await service.evaluate_interview_answer(
        question="Tell me about yourself.",
        answer="I am a software engineer.",
        category="behavioral",
        difficulty=1,
        language_code="en",
    )
    assert "score" in evaluation
    assert "strengths" in evaluation


def test_is_retryable_treats_timeouts_as_transient():
    assert _is_retryable(httpx.TimeoutException("timed out")) is True


def test_is_retryable_treats_5xx_as_transient():
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(503, request=request)
    exc = httpx.HTTPStatusError("server error", request=request, response=response)
    assert _is_retryable(exc) is True


def test_is_retryable_treats_4xx_as_non_transient():
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(400, request=request)
    exc = httpx.HTTPStatusError("bad request", request=request, response=response)
    assert _is_retryable(exc) is False


def test_circuit_breaker_opens_after_threshold():
    breaker = _CircuitBreaker(failure_threshold=3, recovery_seconds=30.0)
    assert breaker.allow_request() is True
    for _ in range(3):
        breaker.record_failure()
    assert breaker.allow_request() is False


def test_circuit_breaker_resets_on_success():
    breaker = _CircuitBreaker(failure_threshold=2, recovery_seconds=30.0)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.allow_request() is False
    breaker.record_success()
    assert breaker.allow_request() is True
