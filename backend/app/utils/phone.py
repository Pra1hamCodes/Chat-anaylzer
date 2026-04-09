"""Phone-number normalization + contact name mapping."""
from __future__ import annotations

import re

_PHONE_RE = re.compile(r"^\+?\d[\d\s\-().]{6,}$")


def normalize(user: str) -> str:
    """Collapse a phone-number-looking user to `+<digits>`.

    Non-phone names are returned unchanged.
    """
    if not user:
        return user
    stripped = user.strip()
    if _PHONE_RE.match(stripped):
        digits = re.sub(r"\D", "", stripped)
        if stripped.startswith("+"):
            return "+" + digits
        return digits
    return stripped


def is_phone(user: str) -> bool:
    return bool(user and _PHONE_RE.match(user.strip()))
