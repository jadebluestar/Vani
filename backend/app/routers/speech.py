import time
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.config import settings
from app.dependencies import get_current_user
from app.rate_limiter import limiter
from app.services.llm_service import llm_service
from app.services.feedback_service import feedback_service
from app.services.whisper_service import whisper_service
from app.utils.language_codes import SUPPORTED_LANGUAGES
from app.utils.validators import validate_audio_file_type, validate_language_code

router = APIRouter(prefix="/speech", tags=["Speech"])


class FeedbackRequest(BaseModel):
    text: str
    language: str = "en"
    duration_seconds: Optional[float] = 0


class FluencyRequest(BaseModel):
    text: str
    language: str = "en"
    duration_seconds: float = 10.0


@router.post("/transcribe", summary="Transcribe audio to text via Groq Whisper")
@limiter.limit(f"{settings.RATE_LIMIT_FREE}/minute")
async def transcribe_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    store_recording: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    start_time = time.time()
    validate_audio_file_type(audio.filename)
    audio_bytes = await audio.read()
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file too large. Maximum 25MB allowed.")
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small or empty.")
    try:
        text, detected_language, duration = await whisper_service.transcribe(
            audio_bytes=audio_bytes,
            filename=audio.filename,
            language=language
        )
        if store_recording:
            # Archival upload isn't needed for the response — push it to the
            # background so the user isn't waiting on an R2 round-trip.
            background_tasks.add_task(
                whisper_service.upload_to_r2,
                audio_bytes,
                current_user["id"],
                audio.filename
            )
        response_time = round(time.time() - start_time, 2)
        return {
            "success": True,
            "text": text,
            "detected_language": detected_language,
            "duration_seconds": duration,
            "word_count": len(text.split()),
            "response_time_seconds": response_time
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/feedback", summary="Get AI speech feedback from text")
@limiter.limit(f"{settings.RATE_LIMIT_FREE}/minute")
async def get_speech_feedback(
    request: Request,
    body: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    start_time = time.time()
    if len(body.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text too short for meaningful feedback.")
    language = validate_language_code(body.language)
    try:
        ai_feedback = await llm_service.generate_speech_feedback(body.text, language)
        enriched = feedback_service.enrich_feedback(
            ai_feedback=ai_feedback,
            text=body.text,
            language_code=language,
            duration_seconds=body.duration_seconds
        )
        response_time = round(time.time() - start_time, 2)
        return {"success": True, "feedback": enriched, "response_time_seconds": response_time}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")


@router.post("/analyze-fluency", summary="Real-time fluency analysis")
@limiter.limit(f"{settings.RATE_LIMIT_FREE}/minute")
async def analyze_fluency(
    request: Request,
    body: FluencyRequest,
    current_user: dict = Depends(get_current_user)
):
    language = validate_language_code(body.language)
    word_count = len(body.text.split())
    rate_metrics = feedback_service.calculate_speaking_rate(body.text, body.duration_seconds)
    filler_metrics = feedback_service.count_filler_words(body.text, language)
    try:
        ai_analysis = await llm_service.analyze_fluency(
            text=body.text,
            word_count=word_count,
            duration_seconds=body.duration_seconds,
            language_code=language
        )
    except Exception as e:
        logger.warning(f"AI fluency analysis failed, using computed only: {e}")
        ai_analysis = {}
    return {
        "success": True,
        "fluency_analysis": {
            **rate_metrics,
            **filler_metrics,
            **ai_analysis,
            "word_count": word_count,
            "language": language
        }
    }


@router.get("/supported-languages", summary="Get list of supported languages")
async def get_supported_languages():
    return {"success": True, "languages": SUPPORTED_LANGUAGES, "count": len(SUPPORTED_LANGUAGES)}