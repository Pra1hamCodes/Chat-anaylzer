"""Group-level and per-user basic statistics."""
from __future__ import annotations

from collections import Counter

import pandas as pd

from app.core.models import ChatMetadata, OverviewStats, ParsedChat, UserStats

from . import chat_to_df


def compute(chat: ParsedChat) -> OverviewStats:
    df = chat_to_df(chat)
    users_df = df[df["message_type"] == "user"].copy()

    total_user_messages = len(users_df)
    total_messages = len(df)

    # Group aggregates
    total_words = int(users_df["word_count"].sum()) if not users_df.empty else 0
    total_chars = int(users_df["char_count"].sum()) if not users_df.empty else 0
    total_media = int(users_df["is_media"].sum()) if not users_df.empty else 0
    total_links = int(users_df["urls"].apply(len).sum()) if not users_df.empty else 0
    total_emojis = int(users_df["emoji_list"].apply(len).sum()) if not users_df.empty else 0

    if not users_df.empty:
        per_day = users_df.groupby("date").size()
        most_active = per_day.idxmax()
        least_active = per_day.idxmin()
        active_days = int(per_day.size)
        msgs_per_day = float(per_day.mean())
    else:
        most_active = least_active = None
        active_days = 0
        msgs_per_day = 0.0

    top_users = _per_user_stats(users_df, total_user_messages)
    return OverviewStats(
        metadata=chat.metadata,
        total_messages=total_messages,
        total_user_messages=total_user_messages,
        total_words=total_words,
        total_chars=total_chars,
        total_media=total_media,
        total_links=total_links,
        total_emojis=total_emojis,
        unique_users=users_df["user"].nunique() if not users_df.empty else 0,
        active_days=active_days,
        msgs_per_day=msgs_per_day,
        most_active_date=most_active,
        least_active_date=least_active,
        top_users=top_users,
    )


def _per_user_stats(users_df: pd.DataFrame, total: int) -> list[UserStats]:
    if users_df.empty:
        return []
    out: list[UserStats] = []
    for user, g in users_df.groupby("user"):
        emoji_counter: Counter[str] = Counter()
        for lst in g["emoji_list"]:
            emoji_counter.update(lst)
        msgs = len(g)
        out.append(
            UserStats(
                user=str(user),
                messages=msgs,
                words=int(g["word_count"].sum()),
                chars=int(g["char_count"].sum()),
                media=int(g["is_media"].sum()),
                links=int(g["urls"].apply(len).sum()),
                emojis=int(sum(emoji_counter.values())),
                unique_emojis=len(emoji_counter),
                top_emoji=(emoji_counter.most_common(1)[0][0] if emoji_counter else None),
                avg_msg_words=float(g["word_count"].mean()),
                avg_msg_chars=float(g["char_count"].mean()),
                first_message=g["datetime"].min().to_pydatetime(),
                last_message=g["datetime"].max().to_pydatetime(),
                active_days=int(g["date"].nunique()),
                pct_of_total=(msgs / total * 100.0) if total else 0.0,
                longest_message_chars=int(g["char_count"].max()),
            )
        )
    out.sort(key=lambda u: u.messages, reverse=True)
    return out
