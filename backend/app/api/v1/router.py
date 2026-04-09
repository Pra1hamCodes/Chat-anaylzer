"""Main v1 router."""
from fastapi import APIRouter

from app.api.v1 import analysis, export, health, upload

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(export.router, tags=["export"])
