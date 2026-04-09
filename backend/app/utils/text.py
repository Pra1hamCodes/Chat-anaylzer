"""Text cleaning / stopword handling."""
from __future__ import annotations

import re
from collections import Counter

# Minimal multi-lingual stopword list. Supplemented (optionally) with NLTK.
STOPWORDS: set[str] = {
    # English
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
    "with","from","as","is","are","was","were","be","been","being","have","has","had","do",
    "does","did","this","that","these","those","it","its","i","you","he","she","we","they",
    "me","him","her","us","them","my","your","his","their","our","so","not","no","yes","ok",
    "okay","ya","hi","hello","haan","haa","hmm","hm","hey","bro","bhai","sir","ma'am","mam",
    # common chat noise
    "media","omitted","null","deleted","message","<media","<this","edited","u","r","bt","pls",
    "plz","thanks","thank","tq","ty","welcome",
}

_WORD_RE = re.compile(r"[A-Za-z\u0900-\u097F\u0980-\u09FF][A-Za-z'\u0900-\u097F\u0980-\u09FF]{1,}")


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


def clean_tokens(text: str) -> list[str]:
    return [w for w in tokenize(text) if w not in STOPWORDS and len(w) > 2]


def top_words(texts, n: int = 50) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for t in texts:
        c.update(clean_tokens(t))
    return c.most_common(n)
