"""FastAPI app factory."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import get_settings
from app.storage.repository import repo

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background cleanup task
    stop = asyncio.Event()

    async def cleaner():
        while not stop.is_set():
            try:
                await repo.cleanup_expired()
            except Exception:
                pass
            try:
                await asyncio.wait_for(stop.wait(), timeout=900)  # 15 min
            except asyncio.TimeoutError:
                pass

    task = asyncio.create_task(cleaner())
    try:
        yield
    finally:
        stop.set()
        task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )
        return response

    @app.get("/")
    async def root():
        return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
