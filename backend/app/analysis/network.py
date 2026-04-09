"""Reply/mention network analysis."""
from __future__ import annotations

from collections import Counter, defaultdict

import pandas as pd

from app.core.models import NetworkStats, ParsedChat

from . import chat_to_df

try:
    import networkx as nx  # type: ignore
    _HAS_NX = True
except Exception:  # pragma: no cover
    _HAS_NX = False

REPLY_WINDOW_MIN = 3
THREAD_GAP_MIN = 10


def compute(chat: ParsedChat) -> NetworkStats:
    df = chat_to_df(chat)
    users = df[df["message_type"] == "user"].copy()
    if users.empty or not _HAS_NX:
        return NetworkStats(nodes=[], edges=[], centrality={}, communities={},
                            threads={"total_threads": 0, "avg_length": 0,
                                     "thread_starters": {}, "top_participants": {}})
    users = users.sort_values("datetime").reset_index(drop=True)

    edges: dict[tuple[str, str], int] = Counter()
    users["prev_user"] = users["user"].shift(1)
    users["prev_dt"] = users["datetime"].shift(1)
    users["gap_min"] = (users["datetime"] - users["prev_dt"]).dt.total_seconds() / 60.0
    mask = (users["prev_user"].notna()) & (users["prev_user"] != users["user"]) \
        & (users["gap_min"] <= REPLY_WINDOW_MIN)
    for _, r in users[mask].iterrows():
        edges[(str(r["user"]), str(r["prev_user"]))] += 1

    G = nx.DiGraph()
    msg_counts = users["user"].value_counts().to_dict()
    for u, c in msg_counts.items():
        G.add_node(str(u), size=int(c))
    for (src, dst), w in edges.items():
        G.add_edge(src, dst, weight=w)

    try:
        pagerank = nx.pagerank(G, weight="weight")
    except Exception:
        pagerank = {n: 0.0 for n in G.nodes}
    try:
        betweenness = nx.betweenness_centrality(G, weight="weight")
    except Exception:
        betweenness = {n: 0.0 for n in G.nodes}
    try:
        clustering = nx.clustering(G.to_undirected())
    except Exception:
        clustering = {n: 0.0 for n in G.nodes}

    centrality = {
        n: {
            "pagerank": round(float(pagerank.get(n, 0)), 5),
            "betweenness": round(float(betweenness.get(n, 0)), 5),
            "in_degree": int(G.in_degree(n, weight="weight") or 0),
            "out_degree": int(G.out_degree(n, weight="weight") or 0),
            "clustering": round(float(clustering.get(n, 0)), 5),
        }
        for n in G.nodes
    }

    # Community detection (greedy modularity on undirected projection)
    communities: dict[str, int] = {}
    try:
        from networkx.algorithms.community import greedy_modularity_communities  # type: ignore
        comms = list(greedy_modularity_communities(G.to_undirected()))
        for idx, c in enumerate(comms):
            for m in c:
                communities[str(m)] = idx
    except Exception:
        communities = {n: 0 for n in G.nodes}

    nodes = [
        {"id": n, "size": int(msg_counts.get(n, 0)), "community": communities.get(n, 0),
         "pagerank": centrality[n]["pagerank"]}
        for n in G.nodes
    ]
    edge_list = [{"source": s, "target": t, "weight": int(w)} for (s, t), w in edges.items()]

    # Threads
    users["new_thread"] = (users["gap_min"] > THREAD_GAP_MIN) | users["gap_min"].isna()
    users["thread_id"] = users["new_thread"].cumsum()
    threads_df = users.groupby("thread_id")
    thread_lens = threads_df.size()
    starters = users[users["new_thread"]]["user"].value_counts().head(10).to_dict()
    participants: Counter[str] = Counter()
    for _, g in threads_df:
        participants.update(set(g["user"].tolist()))

    return NetworkStats(
        nodes=nodes,
        edges=edge_list,
        centrality=centrality,
        communities=communities,
        threads={
            "total_threads": int(thread_lens.size),
            "avg_length": float(thread_lens.mean() if thread_lens.size else 0),
            "thread_starters": {str(k): int(v) for k, v in starters.items()},
            "top_participants": dict(participants.most_common(10)),
        },
    )
