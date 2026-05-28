import time
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.dependencies import get_current_user
from app.services.llm_service import llm_service
from app.services.feedback_service import feedback_service
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
async def transcribe_audio(
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
        r2_key = None
        if store_recording:
            try:
                r2_key = await whisper_service.upload_to_r2(
                    audio_bytes=audio_bytes,
                    user_id=current_user["id"],
                    filename=audio.filename
                )
            except Exception as e:
                logger.warning(f"R2 upload failed (non-critical): {e}")
        response_time = round(time.time() - start_time, 2)
        return {
            "success": True,
            "text": text,
            "detected_language": detected_language,
            "duration_seconds": duration,
            "word_count": len(text.split()),
            "storage_key": r2_key,
            "response_time_seconds": response_time
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/feedback", summary="Get AI speech feedback from text")
async def get_speech_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    start_time = time.time()
    if len(request.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text too short for meaningful feedback.")
    language = validate_language_code(request.language)
    try:
        ai_feedback = await llm_service.generate_speech_feedback(request.text, language)
        enriched = feedback_service.enrich_feedback(
            ai_feedback=ai_feedback,
            text=request.text,
            language_code=language,
            duration_seconds=request.duration_seconds
        )
        response_time = round(time.time() - start_time, 2)
        return {"success": True, "feedback": enriched, "response_time_seconds": response_time}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")


@router.post("/analyze-fluency", summary="Real-time fluency analysis")
async def analyze_fluency(
    request: FluencyRequest,
    current_user: dict = Depends(get_current_user)
):
    language = validate_language_code(request.language)
    word_count = len(request.text.split())
    rate_metrics = feedback_service.calculate_speaking_rate(request.text, request.duration_seconds)
    filler_metrics = feedback_service.count_filler_words(request.text, language)
    try:
        ai_analysis = await llm_service.analyze_fluency(
            text=request.text,
            word_count=word_count,
            duration_seconds=request.duration_seconds,
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