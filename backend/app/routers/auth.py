import random
import string
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt
from loguru import logger

from app.config import settings
from app.utils.validators import validate_phone_number
from app.database import supabase, get_cache
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class OTPSendRequest(BaseModel):
    phone: str


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str
    name: Optional[str] = None
    preferred_language: Optional[str] = "kn"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def create_jwt_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "iat": datetime.utcnow(), "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/otp/send")
async def send_otp(request: OTPSendRequest):
    phone = validate_phone_number(request.phone)
    rate_key = f"otp_rate:{phone}"
    cache = await get_cache()
    
    attempts = await cache.get(rate_key)
    if attempts and int(attempts) >= 3:
        raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait 10 minutes.")
    
    otp = generate_otp()
    await cache.setex(f"otp:{phone}", 300, otp)
    await cache.incr(rate_key)
    await cache.expire(rate_key, 600)
    
    logger.info(f"OTP for {phone}: {otp}")
    
    masked_phone = phone[:4] + "****" + phone[-3:]
    return {
        "success": True,
        "message": f"OTP sent to {masked_phone}",
        "expires_in": 300,
        "dev_otp": otp
    }


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(request: OTPVerifyRequest):
    phone = validate_phone_number(request.phone)
    cache = await get_cache()
    
    stored_otp = await cache.get(f"otp:{phone}")
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP expired or not found.")
    if stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    await cache.delete(f"otp:{phone}")

    existing = supabase.table("users").select("*").eq("phone", phone).execute()
    if existing.data:
        user = existing.data[0]
    else:
        new_user = {
            "phone": phone,
            "name": request.name,
            "preferred_language": request.preferred_language or "kn",
            "coins_balance": 100
        }
        result = supabase.table("users").insert(new_user).execute()
        user = result.data[0]
        logger.info(f"New user created: {user['id']}")

    token = create_jwt_token(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_DAYS * 86400,
        "user": {
            "id": user["id"],
            "phone": user["phone"],
            "name": user["name"],
            "preferred_language": user["preferred_language"],
            "coins_balance": user["coins_balance"],
            "is_tutor": user.get("is_tutor", False)
        }
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "phone": current_user["phone"],
            "name": current_user["name"],
            "preferred_language": current_user["preferred_language"],
            "district": current_user.get("district"),
            "coins_balance": current_user["coins_balance"],
            "is_tutor": current_user.get("is_tutor", False),
            "tutor_verified": current_user.get("tutor_verified", False),
            "created_at": current_user["created_at"],
            "last_active": current_user["last_active"]
        }
    }