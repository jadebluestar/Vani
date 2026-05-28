from fastapi import WebSocket
from typing import Dict, List, Optional
import json
import asyncio
from loguru import logger
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for live interviews and group sessions."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_users: Dict[WebSocket, str] = {}
        self.session_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        self.connection_users[websocket] = user_id
        logger.info(f"User {user_id} connected to session {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        if websocket in self.connection_users:
            user_id = self.connection_users.pop(websocket)
            logger.info(f"User {user_id} disconnected from session {session_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_session(self, message: dict, session_id: str, exclude: Optional[WebSocket] = None):
        if session_id not in self.active_connections:
            return
        dead_connections = []
        for connection in self.active_connections[session_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead, session_id)

    def get_session_participants(self, session_id: str) -> List[str]:
        if session_id not in self.active_connections:
            return []
        return [self.connection_users.get(ws, "unknown") for ws in self.active_connections[session_id]]

    def is_session_active(self, session_id: str) -> bool:
        return session_id in self.active_connections and len(self.active_connections[session_id]) > 0

    def set_session_metadata(self, session_id: str, metadata: dict):
        self.session_metadata[session_id] = metadata

    def get_session_metadata(self, session_id: str) -> Optional[dict]:
        return self.session_metadata.get(session_id)

    def update_session_metadata(self, session_id: str, updates: dict):
        if session_id in self.session_metadata:
            self.session_metadata[session_id].update(updates)
        else:
            self.session_metadata[session_id] = updates


interview_manager = ConnectionManager()
group_manager = ConnectionManager()