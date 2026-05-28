import random
import string
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from loguru import logger

from app.dependencies import get_current_user
from app.database import supabase
from app.websocket_manager import group_manager

router = APIRouter(prefix="/group", tags=["Group Sessions"])


class CreateGroupRequest(BaseModel):
    topic: str
    language: str = "en"
    max_participants: int = 10
    scheduled_at: Optional[str] = None
    description: Optional[str] = None


def generate_join_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/create", summary="Create a new group session")
async def create_group_session(
    request: CreateGroupRequest,
    current_user: dict = Depends(get_current_user)
):
    max_attempts = 10
    for _ in range(max_attempts):
        code = generate_join_code()
        existing = await redis_client.get(f"group_session:{code}")
        if not existing:
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique code, please try again.")
    session_data = {
        "code": code,
        "host_id": current_user["id"],
        "host_name": current_user.get("name", "Host"),
        "topic": request.topic,
        "language": request.language,
        "max_participants": request.max_participants,
        "participants": [current_user["id"]],
        "participant_names": [current_user.get("name", "Host")],
        "status": "waiting",
        "created_at": datetime.utcnow().isoformat(),
        "scheduled_at": request.scheduled_at,
        "description": request.description
    }
    await redis_client.setex(f"group_session:{code}", 86400, json.dumps(session_data))
    return {"success": True, "session": session_data, "join_code": code, "join_url": f"/group/{code}/join", "websocket_url": f"/ws/group/{code}"}


@router.post("/{code}/join", summary="Join a group session by code")
async def join_group_session(
    code: str,
    current_user: dict = Depends(get_current_user)
):
    session_raw = await redis_client.get(f"group_session:{code.upper()}")
    if not session_raw:
        raise HTTPException(status_code=404, detail="Session not found.")
    session = json.loads(session_raw)
    if session["status"] == "ended":
        raise HTTPException(status_code=400, detail="This session has ended.")
    if len(session["participants"]) >= session["max_participants"]:
        raise HTTPException(status_code=400, detail="Session is full.")
    if current_user["id"] not in session["participants"]:
        session["participants"].append(current_user["id"])
        session["participant_names"].append(current_user.get("name", "Learner"))
    await redis_client.setex(f"group_session:{code.upper()}", 86400, json.dumps(session))
    if group_manager.is_session_active(code):
        await group_manager.broadcast_to_session({"type": "participant_joined", "user_id": current_user["id"], "name": current_user.get("name", "Learner"), "participant_count": len(session["participants"])}, code)
    return {"success": True, "session": session, "participant_count": len(session["participants"]), "websocket_url": f"/ws/group/{code.upper()}"}


@router.post("/session/start", summary="Start a group session")
async def start_group_session(
    code: str,
    current_user: dict = Depends(get_current_user)
):
    session_raw = await redis_client.get(f"group_session:{code.upper()}")
    if not session_raw:
        raise HTTPException(status_code=404, detail="Session not found.")
    session = json.loads(session_raw)
    if session["host_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the session host can start the session.")
    if session["status"] == "active":
        raise HTTPException(status_code=400, detail="Session is already active.")
    session["status"] = "active"
    session["started_at"] = datetime.utcnow().isoformat()
    await redis_client.setex(f"group_session:{code.upper()}", 86400, json.dumps(session))
    await group_manager.broadcast_to_session({"type": "session_started", "message": "The session has started!", "topic": session["topic"], "participant_count": len(session["participants"])}, code.upper())
    return {"success": True, "session": session, "message": f"Session started with {len(session['participants'])} participants"}


@router.websocket("/ws/{code}")
async def group_session_ws(websocket: WebSocket, code: str):
    import json as json_lib
    user_id = None
    code = code.upper()
    try:
        init = await websocket.receive_json()
        if init.get("type") != "join":
            await websocket.send_json({"type": "error", "message": "Must send join message first"})
            await websocket.close()
            return
        token = init.get("token", "")
        from jose import jwt as jose_jwt
        from app.config import settings as app_settings
        try:
            payload = jose_jwt.decode(token, app_settings.JWT_SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
        except Exception:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return
        session_raw = await redis_client.get(f"group_session:{code}")
        if not session_raw:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            await websocket.close()
            return
        session = json_lib.loads(session_raw)
        if user_id not in session["participants"] and user_id != session["host_id"]:
            await websocket.send_json({"type": "error", "message": "Not a participant"})
            await websocket.close()
            return
        await group_manager.connect(websocket, code, user_id)
        user_result = supabase.table("users").select("name").eq("id", user_id).execute()
        user_name = (user_result.data[0].get("name") if user_result.data else None) or "Learner"
        await websocket.send_json({"type": "joined", "code": code, "topic": session["topic"]})
        await group_manager.broadcast_to_session({"type": "participant_joined", "user_id": user_id, "name": user_name}, code, exclude=websocket)
        while True:
            msg = await websocket.receive_json()
            if msg.get("type") == "message":
                await group_manager.broadcast_to_session({"type": "message", "from": user_name, "user_id": user_id, "text": msg.get("text", ""), "timestamp": datetime.utcnow().isoformat()}, code)
            elif msg.get("type") == "leave":
                break
    except WebSocketDisconnect:
        pass
    finally:
        if user_id:
            group_manager.disconnect(websocket, code)
            await group_manager.broadcast_to_session({"type": "participant_left", "user_id": user_id}, code)