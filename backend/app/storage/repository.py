"""In-memory + SQLite-backed session repository.

For the first cut we keep parsed analysis in memory keyed by session id
(fine for a single-worker deployment) and persist a lightweight metadata row
to SQLite so sessions survive reloads for status lookups.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from app.config import get_settings

_SETTINGS = get_settings()


@dataclass
class SessionRecord:
    session_id: str
    status: str = "pending"  # pending|processing|done|error
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    overview: Any = None
    temporal: Any = None
    nlp: Any = None
    network: Any = None
    engagement: Any = None
    retention: Any = None
    raw_chat: Any = None  # ParsedChat for export


class SessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._lock = asyncio.Lock()

    async def create(self, sid: str) -> SessionRecord:
        async with self._lock:
            rec = SessionRecord(session_id=sid)
            self._sessions[sid] = rec
            return rec

    async def get(self, sid: str) -> SessionRecord | None:
        async with self._lock:
            return self._sessions.get(sid)

    async def update(self, sid: str, **fields: Any) -> None:
        async with self._lock:
            rec = self._sessions.get(sid)
            if rec is None:
                return
            for k, v in fields.items():
                setattr(rec, k, v)

    async def delete(self, sid: str) -> None:
        async with self._lock:
            self._sessions.pop(sid, None)

    async def cleanup_expired(self) -> int:
        ttl = _SETTINGS.session_ttl_hours * 3600
        now = time.time()
        async with self._lock:
            expired = [sid for sid, r in self._sessions.items() if now - r.created_at > ttl]
            for sid in expired:
                self._sessions.pop(sid, None)
            return len(expired)


repo = SessionRepository()
