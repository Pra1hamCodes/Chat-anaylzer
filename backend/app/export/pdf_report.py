"""Multi-page PDF report via ReportLab."""
from __future__ import annotations

import io
from datetime import datetime

from app.storage.repository import SessionRecord

try:
    from reportlab.lib import colors  # type: ignore
    from reportlab.lib.pagesizes import A4  # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
    from reportlab.lib.units import cm  # type: ignore
    from reportlab.platypus import (  # type: ignore
        PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    )
    _HAS_REPORTLAB = True
except Exception:  # pragma: no cover
    _HAS_REPORTLAB = False


def render(rec: SessionRecord) -> bytes:
    if not _HAS_REPORTLAB:
        return _render_text_fallback(rec)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontSize=26, textColor=colors.HexColor("#00d4aa"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#7c3aed"))

    ov = rec.overview
    meta = ov.metadata
    story = []

    story.append(Paragraph("WhatsApp Chat Analysis Report", title))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Group: <b>{meta.group_name or 'Unknown Group'}</b>", styles["Normal"]))
    story.append(Paragraph(f"Date range: {meta.date_range[0]} to {meta.date_range[1]}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph("Executive Summary", h2))
    kpis = [
        ["Total Messages", f"{ov.total_messages}"],
        ["User Messages", f"{ov.total_user_messages}"],
        ["System Events", f"{meta.total_system_events}"],
        ["Unique Users", f"{ov.unique_users}"],
        ["Active Days", f"{ov.active_days}"],
        ["Msgs / Day", f"{ov.msgs_per_day:.1f}"],
        ["Total Media", f"{ov.total_media}"],
        ["Total Links", f"{ov.total_links}"],
    ]
    t = Table(kpis, colWidths=[6 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f4f4f8")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Top Users", h2))
    rows = [["#", "User", "Messages", "Words", "Media", "Links", "% of total"]]
    for i, u in enumerate(ov.top_users[:20], 1):
        rows.append([str(i), u.user[:25], str(u.messages), str(u.words),
                     str(u.media), str(u.links), f"{u.pct_of_total:.1f}%"])
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("Temporal Patterns", h2))
    tp = rec.temporal
    story.append(Paragraph(f"Busiest hour: {tp.busiest_hour}:00", styles["Normal"]))
    story.append(Paragraph(f"Busiest day: {tp.busiest_day_name}", styles["Normal"]))
    story.append(Paragraph(f"Total bursts detected: {len(tp.bursts)}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Engagement", h2))
    eng = rec.engagement
    story.append(Paragraph(f"Bounce rate (joined+left within 24h): {eng.bounce_rate}%", styles["Normal"]))
    story.append(Paragraph(f"Churn risk members: {len(eng.churn_risk)}", styles["Normal"]))
    story.append(Paragraph(f"Ghost members: {len(eng.ghost_members)}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    tiers = eng.tiers
    tier_counts: dict[str, int] = {}
    for t_ in tiers.values():
        tier_counts[t_] = tier_counts.get(t_, 0) + 1
    rows = [["Tier", "Members"]] + [[k, str(v)] for k, v in tier_counts.items()]
    table = Table(rows, colWidths=[6 * cm, 3 * cm])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey)]))
    story.append(table)
    story.append(PageBreak())

    story.append(Paragraph("Sentiment & NLP", h2))
    nl = rec.nlp
    story.append(Paragraph(f"Topics extracted: {len(nl.topics)}", styles["Normal"]))
    if nl.topics:
        for tp_ in nl.topics[:5]:
            kws = ", ".join(tp_["keywords"][:8])
            story.append(Paragraph(f"<b>Topic {tp_['id']}</b>: {kws}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Top Words", styles["Heading3"]))
    words = [[w, str(n)] for w, n in nl.top_words_global[:20]]
    if words:
        story.append(Table([["Word", "Count"]] + words,
                           style=TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey)])))

    story.append(PageBreak())
    story.append(Paragraph("Retention", h2))
    rt = rec.retention
    for k, v in rt.survival_curve.items():
        story.append(Paragraph(f"{k}: {v}% still active", styles["Normal"]))

    doc.build(story)
    return buf.getvalue()


def _render_text_fallback(rec: SessionRecord) -> bytes:
    lines = [
        "WhatsApp Chat Analysis Report",
        "",
        f"Group: {rec.overview.metadata.group_name or 'Unknown'}",
        f"Total messages: {rec.overview.total_messages}",
        f"Unique users: {rec.overview.unique_users}",
    ]
    return ("\n".join(lines)).encode("utf-8")
