import re
from fastapi import HTTPException, status


def validate_phone_number(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("91") and len(phone) == 12:
        pass
    elif len(phone) == 10:
        phone = "91" + phone
    else:
        raise HTTPException(status_code=400, detail="Invalid phone number.")
    if not re.match(r"^91[6-9]\d{9}$", phone):
        raise HTTPException(status_code=400, detail="Invalid Indian mobile number.")
    return "+" + phone


def validate_language_code(code: str) -> str:
    from app.utils.language_codes import is_supported_language
    if not is_supported_language(code):
        raise HTTPException(status_code=400, detail=f"Language '{code}' is not supported.")
    return code


def validate_audio_file_type(filename: str) -> str:
    allowed = {".webm", ".mp3", ".mp4", ".wav", ".ogg", ".m4a", ".opus"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format '{ext}'.")
    return ext


def validate_difficulty_level(level: int) -> int:
    if not 1 <= level <= 5:
        raise HTTPException(status_code=400, detail="Difficulty level must be between 1 and 5.")
    return level


def validate_rating(rating: float) -> float:
    if not 1.0 <= rating <= 5.0:
        raise HTTPException(status_code=400, detail="Rating must be between 1.0 and 5.0.")
    return rating


def sanitize_text_input(text: str, max_length: int = 5000) -> str:
    text = text.strip()
    if len(text) > max_length:
        raise HTTPException(status_code=400, detail=f"Text too long. Maximum {max_length} characters.")
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return text