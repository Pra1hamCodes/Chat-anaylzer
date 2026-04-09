"""Temporal analysis: hourly, weekly, heatmap, bursts, response time."""
from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from app.core.models import ParsedChat, TemporalStats

from . import chat_to_df

_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def compute(chat: ParsedChat) -> TemporalStats:
    df = chat_to_df(chat)
    users = df[df["message_type"] == "user"].copy()
    if users.empty:
        return TemporalStats(
            hourly={h: 0 for h in range(24)},
            by_day_of_week={d: 0 for d in _DAY_NAMES},
            heatmap=[[0] * 24 for _ in range(7)],
            daily={}, weekly={}, monthly={}, cumulative={},
            busiest_hour=0, busiest_day_name="Monday",
            longest_gaps=[], bursts=[], response_time_median_minutes={},
            first_message_of_day_leaderboard={}, night_owls=[], early_birds=[],
        )
    users = users.sort_values("datetime").reset_index(drop=True)

    hourly = users.groupby("hour").size().reindex(range(24), fill_value=0).to_dict()
    hourly = {int(k): int(v) for k, v in hourly.items()}

    by_dow = users.groupby("day_name").size().to_dict()
    by_dow = {d: int(by_dow.get(d, 0)) for d in _DAY_NAMES}

    heatmap = np.zeros((7, 24), dtype=int)
    for _, row in users.iterrows():
        heatmap[row["day_of_week"], row["hour"]] += 1

    daily = users.groupby(users["datetime"].dt.date).size()
    weekly = users.groupby(users["datetime"].dt.to_period("W").astype(str)).size()
    monthly = users.groupby(users["datetime"].dt.to_period("M").astype(str)).size()
    cumulative = daily.cumsum()

    busiest_hour = int(max(hourly, key=hourly.get))
    busiest_day = max(by_dow, key=by_dow.get)

    # Longest gaps
    gaps = users["datetime"].diff().dropna()
    gap_rows = []
    if not gaps.empty:
        top = gaps.nlargest(10)
        for idx, g in top.items():
            gap_rows.append({
                "start": users.loc[idx - 1, "datetime"].isoformat(),
                "end": users.loc[idx, "datetime"].isoformat(),
                "hours": round(g.total_seconds() / 3600, 2),
            })

    # Burst detection (daily)
    bursts = []
    if len(daily) > 3:
        mu, sd = daily.mean(), daily.std() or 1
        thresh = mu + 3 * sd
        for d, v in daily.items():
            if v > thresh:
                bursts.append({"date": str(d), "messages": int(v),
                               "zscore": round((v - mu) / sd, 2)})

    # Response time (median) per user: time since previous user's message
    users["prev_dt"] = users["datetime"].shift(1)
    users["prev_user"] = users["user"].shift(1)
    users["delta_min"] = (users["datetime"] - users["prev_dt"]).dt.total_seconds() / 60.0
    others = users[(users["prev_user"].notna()) & (users["prev_user"] != users["user"])]
    rt_median = (
        others.groupby("user")["delta_min"].median().round(2).to_dict() if not others.empty else {}
    )

    # First message of day
    first = users.loc[users.groupby("date")["datetime"].idxmin()]
    first_leader = first["user"].value_counts().to_dict()

    # Night owls (21-04) / early birds (04-08)
    night = users[(users["hour"] >= 21) | (users["hour"] < 4)]
    early = users[(users["hour"] >= 4) & (users["hour"] < 8)]
    night_owls = night["user"].value_counts().head(5).index.tolist()
    early_birds = early["user"].value_counts().head(5).index.tolist()

    return TemporalStats(
        hourly=hourly,
        by_day_of_week=by_dow,
        heatmap=heatmap.tolist(),
        daily={str(k): int(v) for k, v in daily.items()},
        weekly={str(k): int(v) for k, v in weekly.items()},
        monthly={str(k): int(v) for k, v in monthly.items()},
        cumulative={str(k): int(v) for k, v in cumulative.items()},
        busiest_hour=busiest_hour,
        busiest_day_name=busiest_day,
        longest_gaps=gap_rows,
        bursts=bursts,
        response_time_median_minutes={str(k): float(v) for k, v in rt_median.items()},
        first_message_of_day_leaderboard={str(k): int(v) for k, v in first_leader.items()},
        night_owls=[str(u) for u in night_owls],
        early_birds=[str(u) for u in early_birds],
    )
