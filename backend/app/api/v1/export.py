"""Export endpoints: PDF, CSV, HTML."""
from __future__ import annotations

import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse

from app.api.v1.analysis import _require
from app.export import csv_export, html_report, pdf_report

router = APIRouter()


@router.get("/export/{sid}/pdf")
async def export_pdf(sid: str):
    rec = await _require(sid)
    data = pdf_report.render(rec)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="analysis_{sid}.pdf"'},
    )


@router.get("/export/{sid}/csv")
async def export_csv(sid: str):
    rec = await _require(sid)
    data = csv_export.render_zip(rec)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="analysis_{sid}.zip"'},
    )


@router.get("/export/{sid}/html")
async def export_html(sid: str):
    rec = await _require(sid)
    html = html_report.render(rec)
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="analysis_{sid}.html"'},
    )
