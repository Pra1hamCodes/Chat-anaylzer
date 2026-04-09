"""Composite engagement score, member tiering, churn risk, admin metrics."""
from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from app.core.models import EngagementStats, ParsedChat

from . import chat_to_df


def _norm(s: pd.Series) -> pd.Series:
    if s.empty:
        return s
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(50.0, index=s.index)
    return ((s - lo) / (hi - lo) * 100.0).round(2)


def compute(chat: ParsedChat) -> EngagementStats:
    df = chat_to_df(chat)
    users = df[df["message_type"] == "user"].copy()
    if users.empty:
        return EngagementStats(scores={}, tiers={}, churn_risk=[],
                               bounce_rate=0.0, ghost_members=[], admin_performance=[])

    total_days = max(1, (users["date"].max() - users["date"].min()).days + 1)

    agg = users.groupby("user").agg(
        messages=("message", "size"),
        active_days=("date", "nunique"),
        avg_words=("word_count", "mean"),
        links=("urls", lambda s: sum(len(x) for x in s)),
        media=("is_media", "sum"),
    )

    # Response score: times this user replied to another user within 3 min
    users.sort_values("datetime", inplace=True)
    users["prev_user"] = users["user"].shift(1)
    users["gap"] = users["datetime"].diff().dt.total_seconds() / 60.0
    replies = users[(users["prev_user"].notna()) & (users["prev_user"] != users["user"]) & (users["gap"] <= 3)]
    resp = replies["user"].value_counts()
    agg["responses"] = agg.index.map(resp).fillna(0)

    # Per-message sentiment (rough, cheap)
    try:
        from textblob import TextBlob  # type: ignore
        def pol(t: str) -> float:
            try:
                return float(TextBlob(t).sentiment.polarity)
            except Exception:
                return 0.0
        users["pol"] = users["message"].astype(str).apply(pol)
        sent = users.groupby("user")["pol"].mean()
    except Exception:
        sent = pd.Series(0.0, index=agg.index)
    agg["sentiment"] = agg.index.map(sent).fillna(0)

    scores = pd.DataFrame(index=agg.index)
    scores["message_frequency_score"] = _norm(agg["messages"])
    scores["consistency_score"] = (agg["active_days"] / total_days * 100).round(2)
    scores["response_score"] = _norm(agg["responses"])
    scores["content_score"] = _norm(agg["avg_words"].fillna(0) + agg["links"] * 3)
    scores["sentiment_score"] = ((agg["sentiment"].clip(-1, 1) + 1) * 50).round(2)

    scores["overall"] = (
        scores["message_frequency_score"] * 0.35
        + scores["consistency_score"] * 0.25
        + scores["response_score"] * 0.15
        + scores["content_score"] * 0.15
        + scores["sentiment_score"] * 0.10
    ).round(2)

    ranked = scores.sort_values("overall", ascending=False)
    n = len(ranked)
    tiers: dict[str, str] = {}
    for i, u in enumerate(ranked.index):
        pct = i / max(1, n - 1)
        if pct <= 0.10: tiers[str(u)] = "Power User"
        elif pct <= 0.40: tiers[str(u)] = "Active"
        elif pct <= 0.70: tiers[str(u)] = "Casual"
        elif pct <= 0.95: tiers[str(u)] = "Lurker"
        else: tiers[str(u)] = "Ghost"

    # Churn risk: last message > 7 days before chat end, OR >60% drop in last quarter
    end = users["datetime"].max()
    cutoff = end - timedelta(days=7)
    last_msg = users.groupby("user")["datetime"].max()
    churn = set(last_msg[last_msg < cutoff].index.astype(str))

    quarter_start = users["datetime"].min() + (end - users["datetime"].min()) * 0.75
    before = users[users["datetime"] < quarter_start]["user"].value_counts()
    after = users[users["datetime"] >= quarter_start]["user"].value_counts()
    for u in before.index:
        b = before.get(u, 0)
        a = after.get(u, 0)
        if b > 5 and a < b * 0.4:
            churn.add(str(u))

    # Bounce rate + ghost members from system events
    sysdf = df[df["message_type"] == "system"].copy()
    joins: dict[str, list] = {}
    leaves: dict[str, list] = {}
    import re as _re
    for _, r in sysdf.iterrows():
        text = str(r["message"])
        if "joined using this group" in text:
            # extract leading actor: e.g. "+91 99... joined using..."
            m = _re.match(r"^(?:~\s)?(.+?)\sjoined", text)
            if m:
                joins.setdefault(m.group(1).strip(), []).append(r["datetime"])
        elif _re.search(r"\bleft\b\s*$", text):
            m = _re.match(r"^(?:~\s)?(.+?)\sleft$", text.strip())
            if m:
                leaves.setdefault(m.group(1).strip(), []).append(r["datetime"])

    quick_bounces = 0
    total_joins = 0
    for actor, dts in joins.items():
        for dt in dts:
            total_joins += 1
            lv = [l for l in leaves.get(actor, []) if l >= dt]
            if lv and (lv[0] - dt).total_seconds() < 86400:
                quick_bounces += 1
    bounce_rate = (quick_bounces / total_joins * 100) if total_joins else 0.0

    senders = set(users["user"].astype(str).unique())
    ghosts = [actor for actor in joins if actor not in senders and not leaves.get(actor)]

    # Admin performance: top 3 users by message count
    admins = agg.nlargest(3, "messages").index.tolist()
    admin_perf = []
    for admin in admins:
        admin_msgs = users[users["user"] == admin]
        for _, m in admin_msgs.iterrows():
            window_end = m["datetime"] + timedelta(minutes=30)
            replies_n = users[(users["datetime"] > m["datetime"])
                              & (users["datetime"] <= window_end)
                              & (users["user"] != admin)].shape[0]
            admin_perf.append({
                "admin": str(admin),
                "datetime": m["datetime"].isoformat(),
                "message_preview": str(m["message"])[:120],
                "replies_30m": int(replies_n),
            })
    # Keep top 50 best-performing admin messages for response payload
    admin_perf.sort(key=lambda x: x["replies_30m"], reverse=True)
    admin_perf = admin_perf[:50]

    scores_dict = {str(u): {k: float(v) for k, v in row.items()}
                   for u, row in scores.iterrows()}
    return EngagementStats(
        scores=scores_dict,
        tiers=tiers,
        churn_risk=sorted(churn),
        bounce_rate=round(float(bounce_rate), 2),
        ghost_members=ghosts,
        admin_performance=admin_perf,
    )
