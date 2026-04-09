"""Analysis modules. Each takes a pandas DataFrame of messages and returns
structured Pydantic output."""
from __future__ import annotations

import pandas as pd

from app.core.models import ParsedChat


def chat_to_df(chat: ParsedChat) -> pd.DataFrame:
    _dump = (lambda m: m.model_dump()) if hasattr(chat.messages[0], "model_dump") else (lambda m: m.dict())
    rows = [_dump(m) for m in chat.messages] if chat.messages else []
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df
