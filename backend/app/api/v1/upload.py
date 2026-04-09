"""Upload endpoint: accepts a .txt WhatsApp export, kicks off parsing +
analysis as a background task, returns a session id."""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.analysis import basic_stats, engagement, network, nlp, retention, temporal
from app.config import get_settings
from app.core.exceptions import InvalidUploadError, ParseError
from app.core.parser import parse_chat
from app.core.security import new_session_id, validate_upload_preview
from app.storage.repository import repo

router = APIRouter()
_SETTINGS = get_settings()


@router.post("/upload")
async def upload(background: BackgroundTasks, file: UploadFile = File(...)) -> dict:
    max_bytes = _SETTINGS.max_upload_size_mb * 1024 * 1024

    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File exceeds max upload size")

    try:
        validate_upload_preview(content[: 64 * 1024], file.filename or "upload.txt", max_bytes)
    except InvalidUploadError as e:
        raise HTTPException(status_code=400, detail=str(e))

    sid = new_session_id()
    dest: Path = _SETTINGS.upload_dir / f"{sid}.txt"
    dest.write_bytes(content)

    await repo.create(sid)
    await repo.update(sid, status="processing")

    background.add_task(_run_pipeline, sid, dest)
    return {"session_id": sid, "status": "processing"}


async def _run_pipeline(sid: str, path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        chat = await asyncio.to_thread(parse_chat, text)
        if chat.metadata.total_messages == 0:
            raise ParseError("Parser produced no messages")

        ov = await asyncio.to_thread(basic_stats.compute, chat)
        temp = await asyncio.to_thread(temporal.compute, chat)
        nl = await asyncio.to_thread(nlp.compute, chat)
        net = await asyncio.to_thread(network.compute, chat)
        eng = await asyncio.to_thread(engagement.compute, chat)
        ret = await asyncio.to_thread(retention.compute, chat)

        await repo.update(
            sid,
            status="done",
            overview=ov,
            temporal=temp,
            nlp=nl,
            network=net,
            engagement=eng,
            retention=ret,
            raw_chat=chat,
        )
    except Exception as exc:  # pragma: no cover
        await repo.update(sid, status="error", error=str(exc))
    finally:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
