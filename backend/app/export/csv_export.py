"""CSV export bundled into a ZIP archive."""
from __future__ import annotations

import csv
import io
import zipfile

from app.storage.repository import SessionRecord


def render_zip(rec: SessionRecord) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("messages.csv", _messages_csv(rec))
        zf.writestr("user_stats.csv", _user_stats_csv(rec))
        zf.writestr("temporal_daily.csv", _daily_csv(rec))
    return buf.getvalue()


def _messages_csv(rec: SessionRecord) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["datetime", "user", "message_type", "event_type", "is_media",
                "word_count", "char_count", "urls", "emojis", "message"])
    for m in rec.raw_chat.messages:
        w.writerow([
            m.datetime.isoformat(), m.user or "", m.message_type, m.event_type,
            int(m.is_media), m.word_count, m.char_count,
            "|".join(m.urls), "".join(m.emoji_list),
            m.message.replace("\n", "\\n"),
        ])
    return out.getvalue()


def _user_stats_csv(rec: SessionRecord) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["user", "messages", "words", "chars", "media", "links", "emojis",
                "unique_emojis", "top_emoji", "avg_msg_words", "active_days", "pct_of_total"])
    for u in rec.overview.top_users:
        w.writerow([u.user, u.messages, u.words, u.chars, u.media, u.links, u.emojis,
                    u.unique_emojis, u.top_emoji or "", round(u.avg_msg_words, 2),
                    u.active_days, round(u.pct_of_total, 2)])
    return out.getvalue()


def _daily_csv(rec: SessionRecord) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["date", "messages"])
    for d, n in rec.temporal.daily.items():
        w.writerow([d, n])
    return out.getvalue()
