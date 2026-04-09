"""Survival / retention analysis based on join and leave system events."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import pandas as pd

from app.core.models import ParsedChat, RetentionStats

from . import chat_to_df

_JOIN_RE = re.compile(r"^(?:~\s)?(.+?)\sjoined using this group")
_LEAVE_RE = re.compile(r"^(?:~\s)?(.+?)\sleft$")


def compute(chat: ParsedChat) -> RetentionStats:
    df = chat_to_df(chat)
    if df.empty:
        return RetentionStats(members=[], survival_curve={}, cohorts={}, quick_churn={})

    sys = df[df["message_type"] == "system"].copy()
    users = df[df["message_type"] == "user"].copy()
    end_dt = df["datetime"].max()

    joins: dict[str, pd.Timestamp] = {}
    leaves: dict[str, pd.Timestamp] = {}
    for _, r in sys.iterrows():
        text = str(r["message"]).strip()
        m = _JOIN_RE.match(text)
        if m:
            joins.setdefault(m.group(1).strip(), r["datetime"])
            continue
        m = _LEAVE_RE.match(text)
        if m:
            leaves[m.group(1).strip()] = r["datetime"]

    last_msg = users.groupby("user")["datetime"].max().to_dict()

    members = []
    for user, join_dt in joins.items():
        last_active = last_msg.get(user)
        leave_dt = leaves.get(user)
        end = leave_dt or last_active or end_dt
        tenure = max(0, (end - join_dt).days)
        status = "churned" if leave_dt else "active"
        members.append({
            "user": str(user),
            "join": join_dt.isoformat(),
            "last_active": last_active.isoformat() if last_active is not None else None,
            "leave": leave_dt.isoformat() if leave_dt is not None else None,
            "tenure_days": int(tenure),
            "status": status,
        })

    # Survival at 1,3,7,14,30 days after join
    buckets = [1, 3, 7, 14, 30]
    survival: dict[str, float] = {}
    total_joins = len(joins) or 1
    for b in buckets:
        surviving = 0
        for user, jdt in joins.items():
            lv = leaves.get(user)
            cutoff = jdt + pd.Timedelta(days=b)
            if lv is None or lv > cutoff:
                surviving += 1
        survival[f"day_{b}"] = round(surviving / total_joins * 100, 2)

    # Cohorts: by join-week
    cohort_buckets: dict[str, list[pd.Timestamp]] = defaultdict(list)
    for user, jdt in joins.items():
        cohort_buckets[str(jdt.to_period("W"))].append(jdt)
    cohorts: dict[str, dict[str, float]] = {}
    for cohort, dts in cohort_buckets.items():
        cohort_members = [u for u, jd in joins.items() if str(jd.to_period("W")) == cohort]
        sub_survival: dict[str, float] = {}
        for b in buckets:
            surviving = 0
            for u in cohort_members:
                jd = joins[u]
                lv = leaves.get(u)
                cutoff = jd + pd.Timedelta(days=b)
                if lv is None or lv > cutoff:
                    surviving += 1
            sub_survival[f"day_{b}"] = round(surviving / max(1, len(cohort_members)) * 100, 2)
        cohorts[cohort] = sub_survival

    quick = Counter()
    for u, jd in joins.items():
        lv = leaves.get(u)
        if lv is None:
            continue
        secs = (lv - jd).total_seconds()
        if secs < 3600:
            quick["1h"] += 1
        elif secs < 86400:
            quick["1d"] += 1
        elif secs < 86400 * 3:
            quick["3d"] += 1
    return RetentionStats(
        members=members,
        survival_curve=survival,
        cohorts=cohorts,
        quick_churn=dict(quick),
    )
