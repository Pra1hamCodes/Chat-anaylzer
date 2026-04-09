"""Analysis read-only endpoints (pydantic v1/v2 compatible)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.core.exceptions import InvalidUploadError
from app.core.security import validate_session_id
from app.storage.repository import repo

router = APIRouter()


def _dump(obj):
    """Cross-version pydantic serialization to JSON-friendly dict."""
    return jsonable_encoder(obj)


async def _require(sid: str):
    try:
        validate_session_id(sid)
    except InvalidUploadError:
        raise HTTPException(status_code=400, detail="Invalid session id")
    rec = await repo.get(sid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if rec.status == "error":
        raise HTTPException(status_code=500, detail=rec.error or "Analysis failed")
    if rec.status != "done":
        raise HTTPException(status_code=202, detail=f"Analysis {rec.status}")
    return rec


@router.get("/analysis/{sid}/status")
async def status(sid: str) -> dict:
    try:
        validate_session_id(sid)
    except InvalidUploadError:
        raise HTTPException(status_code=400, detail="Invalid session id")
    rec = await repo.get(sid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": sid, "status": rec.status, "error": rec.error}


@router.get("/analysis/{sid}/overview")
async def overview(sid: str):
    rec = await _require(sid)
    return _dump(rec.overview)


@router.get("/analysis/{sid}/users")
async def users(sid: str, limit: int = 100, offset: int = 0):
    rec = await _require(sid)
    users = rec.overview.top_users
    return {
        "total": len(users),
        "items": _dump(users[offset: offset + limit]),
    }


@router.get("/analysis/{sid}/user/{username}")
async def single_user(sid: str, username: str):
    rec = await _require(sid)
    for u in rec.overview.top_users:
        if u.user == username:
            return _dump(u)
    raise HTTPException(status_code=404, detail="User not found in session")


@router.get("/analysis/{sid}/temporal")
async def temporal(sid: str):
    rec = await _require(sid)
    return _dump(rec.temporal)


@router.get("/analysis/{sid}/nlp")
async def nlp(sid: str):
    rec = await _require(sid)
    return _dump(rec.nlp)


@router.get("/analysis/{sid}/network")
async def network(sid: str):
    rec = await _require(sid)
    return _dump(rec.network)


@router.get("/analysis/{sid}/engagement")
async def engagement(sid: str):
    rec = await _require(sid)
    return _dump(rec.engagement)


@router.get("/analysis/{sid}/retention")
async def retention(sid: str):
    rec = await _require(sid)
    return _dump(rec.retention)


@router.get("/analysis/{sid}/heatmap")
async def heatmap(sid: str):
    rec = await _require(sid)
    return {"heatmap": rec.temporal.heatmap}


@router.get("/analysis/{sid}/wordcloud")
async def wordcloud(sid: str):
    rec = await _require(sid)
    return {"words": rec.nlp.top_words_global}
