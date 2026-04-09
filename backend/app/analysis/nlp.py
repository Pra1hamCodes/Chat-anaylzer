"""NLP analysis: sentiment, topics, word freq, emoji, URL, language."""
from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urlparse

import pandas as pd

from app.core.models import NLPStats, ParsedChat
from app.utils.text import clean_tokens, top_words

from . import chat_to_df

# Optional imports kept lazy so the module still imports on minimal installs
try:
    from textblob import TextBlob  # type: ignore
    _HAS_TEXTBLOB = True
except Exception:  # pragma: no cover
    _HAS_TEXTBLOB = False

try:
    from langdetect import detect, DetectorFactory  # type: ignore
    DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
except Exception:  # pragma: no cover
    _HAS_LANGDETECT = False

try:
    from sklearn.feature_extraction.text import CountVectorizer  # type: ignore
    from sklearn.decomposition import LatentDirichletAllocation  # type: ignore
    _HAS_SKLEARN = True
except Exception:  # pragma: no cover
    _HAS_SKLEARN = False


_SOCIAL = {"linkedin.com", "twitter.com", "x.com", "instagram.com", "facebook.com"}
_VIDEO = {"youtube.com", "youtu.be", "vimeo.com"}
_CODE = {"github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com"}
_NEWS = {"nytimes.com", "bbc.com", "cnn.com", "thehindu.com", "ndtv.com"}
_EDU = {"coursera.org", "udemy.com", "geeksforgeeks.org", "w3schools.com", "medium.com"}


def _categorize(domain: str) -> str:
    d = domain.lower()
    for group, label in [(_SOCIAL, "social"), (_VIDEO, "video"),
                         (_CODE, "code"), (_NEWS, "news"), (_EDU, "education")]:
        if any(d == x or d.endswith("." + x) for x in group):
            return label
    return "other"


def _sentiment(text: str) -> float:
    if not text.strip():
        return 0.0
    if _HAS_TEXTBLOB:
        try:
            return float(TextBlob(text).sentiment.polarity)  # type: ignore
        except Exception:
            return 0.0
    # Fallback: tiny lexicon
    pos = {"good", "great", "nice", "love", "happy", "thanks", "awesome", "cool"}
    neg = {"bad", "hate", "angry", "sad", "worst", "terrible", "awful"}
    toks = text.lower().split()
    score = sum(1 for t in toks if t in pos) - sum(1 for t in toks if t in neg)
    return score / max(len(toks), 1)


def _safe_detect(text: str) -> str:
    if not _HAS_LANGDETECT or len(text) < 10:
        return "unknown"
    try:
        return detect(text)  # type: ignore
    except Exception:
        return "unknown"


def compute(chat: ParsedChat) -> NLPStats:
    df = chat_to_df(chat)
    users = df[(df["message_type"] == "user") & (~df["is_media"])].copy()
    if users.empty:
        return NLPStats(
            sentiment_per_user={}, daily_sentiment={}, top_words_global=[],
            top_words_per_user={}, top_emojis_global=[], top_emojis_per_user={},
            url_domains=[], domain_categories={}, languages={}, topics=[],
        )

    users["sentiment"] = users["message"].apply(_sentiment)
    sent_per_user = users.groupby("user")["sentiment"].mean().round(3).to_dict()
    daily_sent = (
        users.groupby(users["datetime"].dt.date)["sentiment"].mean().round(3).to_dict()
    )
    daily_sent = {str(k): float(v) for k, v in daily_sent.items()}

    top_words_global = top_words(users["message"].tolist(), 50)
    per_user_words: dict[str, list[tuple[str, int]]] = {}
    for u, g in users.groupby("user"):
        per_user_words[str(u)] = top_words(g["message"].tolist(), 20)

    emoji_counter: Counter[str] = Counter()
    per_user_emojis: dict[str, list[tuple[str, int]]] = {}
    for u, g in users.groupby("user"):
        c: Counter[str] = Counter()
        for lst in g["emoji_list"]:
            c.update(lst)
        per_user_emojis[str(u)] = c.most_common(5)
        emoji_counter.update(c)

    url_counter: Counter[str] = Counter()
    for lst in users["urls"]:
        for u in lst:
            try:
                host = urlparse(u if "://" in u else "http://" + u).hostname or ""
                if host:
                    url_counter[host.lower().lstrip("www.")] += 1
            except Exception:
                continue
    cat_counter: Counter[str] = Counter()
    for host, n in url_counter.items():
        cat_counter[_categorize(host)] += n

    # Language distribution (sample up to 500 longest messages for speed)
    langs: Counter[str] = Counter()
    sample = users.assign(_l=users["message"].str.len()).nlargest(500, "_l")["message"]
    for text in sample:
        langs[_safe_detect(str(text))] += 1

    # Topic modeling (LDA)
    topics: list[dict] = []
    if _HAS_SKLEARN and len(users) >= 30:
        try:
            vec = CountVectorizer(max_features=500, stop_words="english",
                                  token_pattern=r"(?u)\b[A-Za-z]{3,}\b")
            X = vec.fit_transform(users["message"].astype(str).tolist())
            if X.shape[1] > 5:
                n_topics = min(6, max(2, X.shape[1] // 50))
                lda = LatentDirichletAllocation(n_components=n_topics, random_state=42,
                                                max_iter=15)
                lda.fit(X)
                vocab = vec.get_feature_names_out()
                for i, comp in enumerate(lda.components_):
                    top_idx = comp.argsort()[-10:][::-1]
                    topics.append({
                        "id": i,
                        "keywords": [str(vocab[j]) for j in top_idx],
                    })
        except Exception:
            topics = []

    return NLPStats(
        sentiment_per_user={str(k): float(v) for k, v in sent_per_user.items()},
        daily_sentiment=daily_sent,
        top_words_global=top_words_global,
        top_words_per_user=per_user_words,
        top_emojis_global=emoji_counter.most_common(20),
        top_emojis_per_user=per_user_emojis,
        url_domains=url_counter.most_common(30),
        domain_categories=dict(cat_counter),
        languages=dict(langs),
        topics=topics,
    )
