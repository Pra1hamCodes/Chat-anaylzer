"""Pydantic schemas shared across parser, analysis, and API layers."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "message",
    "join",
    "leave",
    "add",
    "remove",
    "group_change",
    "pin",
    "delete",
    "encrypt_notice",
]


class ParsedMessage(BaseModel):
    datetime: datetime
    date: date
    hour: int
    minute: int
    day_of_week: int
    day_name: str
    user: str | None
    message: str
    message_type: Literal["user", "system"]
    event_type: EventType
    is_media: bool = False
    is_deleted: bool = False
    is_edited: bool = False
    word_count: int = 0
    char_count: int = 0
    emoji_list: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    has_mention: bool = False


class ChatMetadata(BaseModel):
    total_messages: int
    total_user_messages: int
    total_users: int
    total_system_events: int
    date_range: tuple[date, date]
    detected_format: str
    group_name: str | None = None
    parse_errors: int = 0
    parse_error_samples: list[str] = Field(default_factory=list)


class ParsedChat(BaseModel):
    messages: list[ParsedMessage]
    metadata: ChatMetadata


# ---- Analysis result schemas ------------------------------------------------


class UserStats(BaseModel):
    user: str
    messages: int
    words: int
    chars: int
    media: int
    links: int
    emojis: int
    unique_emojis: int
    top_emoji: str | None
    avg_msg_words: float
    avg_msg_chars: float
    first_message: datetime | None
    last_message: datetime | None
    active_days: int
    pct_of_total: float
    longest_message_chars: int


class OverviewStats(BaseModel):
    metadata: ChatMetadata
    total_messages: int
    total_user_messages: int
    total_words: int
    total_chars: int
    total_media: int
    total_links: int
    total_emojis: int
    unique_users: int
    active_days: int
    msgs_per_day: float
    most_active_date: date | None
    least_active_date: date | None
    top_users: list[UserStats]


class TemporalStats(BaseModel):
    hourly: dict[int, int]
    by_day_of_week: dict[str, int]
    heatmap: list[list[int]]  # 7 x 24
    daily: dict[str, int]
    weekly: dict[str, int]
    monthly: dict[str, int]
    cumulative: dict[str, int]
    busiest_hour: int
    busiest_day_name: str
    longest_gaps: list[dict]
    bursts: list[dict]
    response_time_median_minutes: dict[str, float]
    first_message_of_day_leaderboard: dict[str, int]
    night_owls: list[str]
    early_birds: list[str]


class NLPStats(BaseModel):
    sentiment_per_user: dict[str, float]
    daily_sentiment: dict[str, float]
    top_words_global: list[tuple[str, int]]
    top_words_per_user: dict[str, list[tuple[str, int]]]
    top_emojis_global: list[tuple[str, int]]
    top_emojis_per_user: dict[str, list[tuple[str, int]]]
    url_domains: list[tuple[str, int]]
    domain_categories: dict[str, int]
    languages: dict[str, int]
    topics: list[dict]


class NetworkStats(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    centrality: dict[str, dict[str, float]]
    communities: dict[str, int]
    threads: dict


class EngagementStats(BaseModel):
    scores: dict[str, dict[str, float]]
    tiers: dict[str, str]
    churn_risk: list[str]
    bounce_rate: float
    ghost_members: list[str]
    admin_performance: list[dict]


class RetentionStats(BaseModel):
    members: list[dict]
    survival_curve: dict[str, float]
    cohorts: dict[str, dict[str, float]]
    quick_churn: dict[str, int]
