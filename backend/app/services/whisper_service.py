import os
import tempfile
import boto3
from groq import AsyncGroq
from app.config import settings
from loguru import logger
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid


class WhisperService:
    """Service for transcribing audio using Groq's Whisper implementation."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "whisper-large-v3"
        self.r2_client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto"
        )
        self.bucket = settings.R2_BUCKET_NAME

    async def transcribe(
        self, 
        audio_bytes: bytes, 
        filename: str,
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        suffix = "." + filename.rsplit(".", 1)[-1] if "." in filename else ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as audio_file:
                kwargs = {"file": (filename, audio_file, "audio/webm"), "model": self.model, "response_format": "verbose_json", "temperature": 0}
                if language:
                    kwargs["language"] = language
                transcription = await self.client.audio.transcriptions.create(**kwargs)
            detected_lang = getattr(transcription, "language", language or "en")
            duration = getattr(transcription, "duration", 0.0)
            text = transcription.text.strip()
            return text, detected_lang, float(duration) if duration else 0.0
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise
        finally:
            os.unlink(tmp_path)

    async def upload_to_r2(self, audio_bytes: bytes, user_id: str, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "webm"
        date_str = datetime.utcnow().strftime("%Y/%m/%d")
        file_uuid = str(uuid.uuid4())
        object_key = f"audio/{user_id}/{date_str}/{file_uuid}.{ext}"
        try:
            self.r2_client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=audio_bytes,
                ContentType=f"audio/{ext}",
                Metadata={
                    "user_id": user_id,
                    "upload_date": datetime.utcnow().isoformat(),
                    "delete_after": (datetime.utcnow() + timedelta(days=settings.AUDIO_RETENTION_DAYS)).isoformat()
                }
            )
            return object_key
        except Exception as e:
            logger.error(f"R2 upload error: {e}")
            raise

    async def cleanup_expired_recordings(self):
        cutoff_date = datetime.utcnow() - timedelta(days=settings.AUDIO_RETENTION_DAYS)
        try:
            paginator = self.r2_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket, Prefix="audio/")
            deleted_count = 0
            for page in pages:
                for obj in page.get("Contents", []):
                    if obj["LastModified"].replace(tzinfo=None) < cutoff_date:
                        self.r2_client.delete_object(Bucket=self.bucket, Key=obj["Key"])
                        deleted_count += 1
            logger.info(f"Cleaned up {deleted_count} expired audio recordings")
        except Exception as e:
            logger.error(f"R2 cleanup error: {e}")


whisper_service = WhisperService()