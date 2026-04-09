"""File upload + input validation."""
from __future__ import annotations

import re
import uuid

from app.core.exceptions import InvalidUploadError
from app.core.parser import _TS_RE

ALLOWED_EXTENSIONS = {".txt"}
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def validate_session_id(sid: str) -> str:
    if not _UUID_RE.match(sid):
        raise InvalidUploadError("Invalid session id")
    return sid


def new_session_id() -> str:
    return str(uuid.uuid4())


def validate_upload_preview(first_bytes: bytes, filename: str, max_bytes: int) -> None:
    """Sanity-check an uploaded file BEFORE full processing."""
    if not filename.lower().endswith(".txt"):
        raise InvalidUploadError("Only .txt files are accepted")
    if len(first_bytes) > max_bytes:
        raise InvalidUploadError("File exceeds maximum allowed size")
    try:
        text = first_bytes.decode("utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover
        raise InvalidUploadError("File is not readable as text") from exc

    # Require at least one line that looks like a WhatsApp timestamped entry in
    # the first 20 lines; this catches most non-chat uploads.
    for line in text.splitlines()[:20]:
        if _TS_RE.match(line):
            return
    raise InvalidUploadError(
        "File does not appear to be a WhatsApp chat export (no recognizable timestamps found)."
    )
