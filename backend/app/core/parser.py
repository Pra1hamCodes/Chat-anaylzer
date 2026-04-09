"""
WhatsApp Chat Parser - production grade.

Handles every observed WhatsApp export format:
- dd/mm/yy, dd/mm/yyyy, mm/dd/yy, mm/dd/yyyy (auto-detected)
- 12h (with regular space, NBSP \u00a0, or NARROW NBSP \u202f before AM/PM) AND 24h
- BOTH user messages AND system events (joins, leaves, group changes, deletes...)
- Multi-line messages (continuation lines appended to previous)
- Messages whose content contains colons
- Tilde-prefixed system actors ("~ Hetvi Doshi left")

Streams line-by-line for performance on 100k+ line files.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Iterable, Iterator

from app.core.models import ChatMetadata, ParsedChat, ParsedMessage

# ---------------------------------------------------------------------------
# Regex
# ---------------------------------------------------------------------------
# Date  : 1-2 digit / 1-2 digit / 2-or-4 digit year
# Time  : 1-2 digit hour : 2 digit minute, optional [\s\u00a0\u202f]?(am|pm) (any case)
# Body  : everything after " - "
#
# We use a single anchor regex with named groups, then post-process the date
# component once we know the layout (ddmm vs mmdd).
_TS_RE = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s"
    r"(?P<time>\d{1,2}:\d{2}(?:[\s\u00a0\u202f]?[APap][Mm])?)"
    r"\s-\s(?P<body>.*)$"
)

# Captures "<user>: <message>" but only when the colon comes BEFORE any other
# colon-followed-by-space. We restrict the username to characters that are
# plausible (no newlines, no leading dash). The greedy `.+?` stops at first ": ".
_USER_RE = re.compile(r"^(?P<user>[^:\n]{1,120}?):\s(?P<msg>.*)$", re.DOTALL)

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_MENTION_RE = re.compile(r"(?<!\w)@\w+")

# Try to detect emoji using a wide unicode range. Avoids extra dependency.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F6FF"  # symbols & pictographs, transport
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F1E6-\U0001F1FF"  # flags
    "]",
    flags=re.UNICODE,
)

# System-event keywords. Order matters for first-match wins.
_SYSTEM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("encrypt_notice", re.compile(r"Messages and calls are end-to-end encrypted", re.I)),
    ("group_change", re.compile(r"created this group", re.I)),
    ("group_change", re.compile(r"changed (the )?group (name|description|icon|settings)", re.I)),
    ("group_change", re.compile(r"changed this group's (icon|settings|description)", re.I)),
    ("group_change", re.compile(r"changed the subject", re.I)),
    ("join",         re.compile(r"joined using this group's invite link", re.I)),
    ("join",         re.compile(r"\bwas added\b", re.I)),
    ("add",          re.compile(r"\badded\b\s", re.I)),
    ("leave",        re.compile(r"\bleft\b\s*$", re.I)),
    ("remove",       re.compile(r"\bremoved\b", re.I)),
    ("pin",          re.compile(r"pinned a message", re.I)),
    ("delete",       re.compile(r"deleted this message|This message was deleted", re.I)),
]

_MEDIA_MARKERS = ("<Media omitted>", "<media omitted>", "image omitted", "video omitted",
                  "audio omitted", "sticker omitted", "GIF omitted", "document omitted")

_DELETED_MARKERS = ("This message was deleted", "You deleted this message")
_EDITED_MARKERS = ("<This message was edited>",)


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------
def _detect_format(sample_lines: Iterable[str]) -> tuple[str, bool]:
    """Return (date_layout, is_12h). date_layout in {"dmy", "mdy"}.

    Strategy: scan up to 200 timestamped lines, collect first/second number.
    If any first-component > 12 → dmy. Else if any second > 12 → mdy. Else dmy
    (matches WhatsApp's most common locale).
    """
    is_12h = False
    saw_dmy = False
    saw_mdy = False
    seen = 0
    for line in sample_lines:
        m = _TS_RE.match(line)
        if not m:
            continue
        seen += 1
        d = m.group("date")
        a, b, _ = d.split("/")
        ai, bi = int(a), int(b)
        if ai > 12:
            saw_dmy = True
        if bi > 12:
            saw_mdy = True
        if re.search(r"[APap][Mm]\s*$", m.group("time")):
            is_12h = True
        if seen >= 200:
            break
    if saw_dmy and not saw_mdy:
        return "dmy", is_12h
    if saw_mdy and not saw_dmy:
        return "mdy", is_12h
    return "dmy", is_12h  # default


def _parse_dt(date_s: str, time_s: str, layout: str) -> datetime:
    a, b, y = date_s.split("/")
    if layout == "dmy":
        day, month = int(a), int(b)
    else:
        month, day = int(a), int(b)
    year = int(y)
    if year < 100:
        year += 2000

    # Normalize whitespace before AM/PM
    t = time_s.replace("\u202f", " ").replace("\u00a0", " ").strip()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            tobj = datetime.strptime(t, fmt).time()
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"Unparseable time: {time_s!r}")
    return datetime(year, month, day, tobj.hour, tobj.minute)


# ---------------------------------------------------------------------------
# Body classification
# ---------------------------------------------------------------------------
def _classify_body(body: str) -> tuple[str | None, str, str]:
    """Return (user_or_None, message_text, event_type).

    Priority:
    1. If body matches `<plausible-user>: <text>` → user message
    2. Else → system event; classify event_type via keyword patterns
    """
    # Tilde-prefixed actors are still system messages: "~ Hetvi Doshi left"
    if body.startswith("~ "):
        return _classify_system(body)

    m = _USER_RE.match(body)
    if m:
        candidate_user = m.group("user").strip()
        msg = m.group("msg")
        # Heuristics: a "user" containing newlines, leading dash, or system
        # keywords is actually a system event masquerading. WhatsApp usernames
        # are short-ish; cap at 100 chars.
        if (
            "\n" not in candidate_user
            and not candidate_user.startswith("-")
            and len(candidate_user) <= 100
            and not _looks_like_system_actor(candidate_user, body)
        ):
            return candidate_user, msg, "message"

    return _classify_system(body)


def _looks_like_system_actor(user: str, body: str) -> bool:
    """A handful of system events use 'You' as the actor with a colon-less verb."""
    # If the body's "message" portion starts with "joined", "left", etc., it's a system event
    after = body[len(user) + 2 :] if body.startswith(user + ": ") else ""
    sys_words = ("joined using this group", "left", "was added", "removed",
                 "changed the group", "changed this group", "added")
    return any(after.startswith(w) for w in sys_words)


def _classify_system(body: str) -> tuple[None, str, str]:
    for event, pat in _SYSTEM_PATTERNS:
        if pat.search(body):
            return None, body, event
    return None, body, "message"  # unknown system → bucket as 'message'


# ---------------------------------------------------------------------------
# Message construction
# ---------------------------------------------------------------------------
def _build_message(dt: datetime, user: str | None, text: str, event: str) -> ParsedMessage:
    is_media = any(marker in text for marker in _MEDIA_MARKERS)
    is_deleted = any(marker in text for marker in _DELETED_MARKERS)
    is_edited = any(marker in text for marker in _EDITED_MARKERS)
    urls = _URL_RE.findall(text)
    emojis = _EMOJI_RE.findall(text)
    word_count = 0 if is_media else len(text.split())
    char_count = 0 if is_media else len(text)

    return ParsedMessage(
        datetime=dt,
        date=dt.date(),
        hour=dt.hour,
        minute=dt.minute,
        day_of_week=dt.weekday(),
        day_name=dt.strftime("%A"),
        user=user,
        message=text,
        message_type="user" if user is not None else "system",
        event_type=event,  # type: ignore[arg-type]
        is_media=is_media,
        is_deleted=is_deleted,
        is_edited=is_edited,
        word_count=word_count,
        char_count=char_count,
        emoji_list=emojis,
        urls=urls,
        has_mention=bool(_MENTION_RE.search(text)),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_chat(text: str) -> ParsedChat:
    """Parse the full content of a WhatsApp .txt export."""
    lines = text.splitlines()
    layout, is_12h = _detect_format(lines)

    messages: list[ParsedMessage] = []
    parse_errors = 0
    error_samples: list[str] = []
    group_name: str | None = None

    pending: tuple[datetime, str | None, str, str] | None = None  # (dt, user, text, event)

    def flush() -> None:
        nonlocal pending
        if pending is None:
            return
        dt, user, text, event = pending
        messages.append(_build_message(dt, user, text, event))
        pending = None

    for raw in lines:
        line = raw.rstrip("\r")
        if not line:
            # Blank line → continuation of previous (preserved as newline)
            if pending is not None:
                dt, user, text, event = pending
                pending = (dt, user, text + "\n", event)
            continue

        m = _TS_RE.match(line)
        if not m:
            # Continuation line for the prior message
            if pending is not None:
                dt, user, text, event = pending
                pending = (dt, user, text + "\n" + line, event)
            else:
                parse_errors += 1
                if len(error_samples) < 10:
                    error_samples.append(line)
            continue

        # New timestamped record → flush previous
        flush()
        try:
            dt = _parse_dt(m.group("date"), m.group("time"), layout)
        except ValueError:
            parse_errors += 1
            if len(error_samples) < 10:
                error_samples.append(line)
            continue

        body = m.group("body")
        user, text, event = _classify_body(body)
        pending = (dt, user, text, event)

        # Capture group name from rename events
        if event == "group_change" and "changed the group name" in body.lower():
            mm = re.search(r'to\s+"([^"]+)"', body)
            if mm:
                group_name = mm.group(1)

    flush()

    user_msg_count = sum(1 for m in messages if m.message_type == "user")
    sys_count = sum(1 for m in messages if m.message_type == "system")
    users = sorted({m.user for m in messages if m.user})
    if messages:
        date_range = (messages[0].date, messages[-1].date)
    else:
        today = date.today()
        date_range = (today, today)

    metadata = ChatMetadata(
        total_messages=len(messages),
        total_user_messages=user_msg_count,
        total_users=len(users),
        total_system_events=sys_count,
        date_range=date_range,
        detected_format=f"{layout} {'12h' if is_12h else '24h'}",
        group_name=group_name,
        parse_errors=parse_errors,
        parse_error_samples=error_samples,
    )
    return ParsedChat(messages=messages, metadata=metadata)


def parse_chat_file(path: str) -> ParsedChat:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return parse_chat(fh.read())


def stream_lines(path: str) -> Iterator[str]:
    """Memory-efficient line iterator (for very large files)."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            yield line.rstrip("\n")
