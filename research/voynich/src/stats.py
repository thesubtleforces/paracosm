"""Small, dependency-light text statistics used by the analyses."""
from __future__ import annotations

import math
import random
from collections import Counter
from typing import Iterable, Sequence

import numpy as np


def entropy(counts: Iterable[int]) -> float:
    """Shannon entropy in bits of a count vector (plug-in estimate)."""
    c = np.asarray([x for x in counts if x > 0], dtype=float)
    if c.size == 0:
        return 0.0
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def char_entropies(tokens: Sequence[str], sep: str = " ") -> tuple[float, float]:
    """(h1, h2): unigram entropy and conditional entropy H(c_n | c_{n-1}) of the glyph stream,
    with the word separator counted as a symbol. Both in bits per glyph."""
    stream = sep.join(tokens)
    h1 = entropy(Counter(stream).values())
    big = Counter(zip(stream, stream[1:]))
    h_joint = entropy(big.values())
    # H(X_n | X_{n-1}) = H(X_{n-1}, X_n) - H(X_{n-1})
    h_prev = entropy(Counter(stream[:-1]).values())
    return h1, h_joint - h_prev


def within1(a: str, b: str) -> bool:
    """True if Levenshtein distance(a, b) <= 1."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = 0
        for x, y in zip(a, b):
            if x != y:
                diff += 1
                if diff > 1:
                    return False
        return True
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def near1(a: str, b: str) -> bool:
    """Exactly one edit apart (similar but not identical)."""
    return a != b and within1(a, b)


def adjacent_mi(tokens: Sequence[str]) -> float:
    """Plug-in mutual information (bits) between consecutive word tokens."""
    uni = Counter(tokens)
    big = Counter(zip(tokens, tokens[1:]))
    n = len(tokens) - 1
    h_x = entropy(Counter(tokens[:-1]).values())
    h_y = entropy(Counter(tokens[1:]).values())
    h_xy = entropy(big.values())
    del uni, n
    return h_x + h_y - h_xy


def shuffled(tokens: Sequence[str], rng: random.Random) -> list[str]:
    t = list(tokens)
    rng.shuffle(t)
    return t


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def window_metrics(tokens: Sequence[str], rng: random.Random, n_shuffles: int = 5) -> dict:
    """Metrics for one window of word tokens. Shuffle baselines keep the word inventory and
    destroy only the order, so 'excess' values isolate sequential structure."""
    n = len(tokens)
    counts = Counter(tokens)
    freq = np.array(sorted(counts.values(), reverse=True), float)
    h1, h2 = char_entropies(tokens)
    lens = [len(w) for w in tokens]

    rep_exact = sum(a == b for a, b in zip(tokens, tokens[1:])) / (n - 1)
    rep_near = sum(near1(a, b) for a, b in zip(tokens, tokens[1:])) / (n - 1)
    mi = adjacent_mi(tokens)
    ac = pearson(lens[:-1], lens[1:])

    s_exact, s_near, s_mi, s_ac = [], [], [], []
    for _ in range(n_shuffles):
        s = shuffled(tokens, rng)
        s_exact.append(sum(a == b for a, b in zip(s, s[1:])) / (n - 1))
        s_near.append(sum(near1(a, b) for a, b in zip(s, s[1:])) / (n - 1))
        s_mi.append(adjacent_mi(s))
        sl = [len(w) for w in s]
        s_ac.append(pearson(sl[:-1], sl[1:]))

    return {
        "n_tokens": n,
        "mean_word_len": float(np.mean(lens)),
        "sd_word_len": float(np.std(lens)),
        "h1_char": h1,
        "h2_char": h2,
        "alphabet": len(set("".join(tokens))),
        "ttr": len(counts) / n,
        "hapax_share_of_types": float((freq == 1).sum() / len(freq)),
        "top10_share": float(freq[:10].sum() / n),
        "word_entropy": entropy(counts.values()),
        "repeat_exact": rep_exact,
        "repeat_exact_shuffled": float(np.mean(s_exact)),
        "repeat_near": rep_near,
        "repeat_near_shuffled": float(np.mean(s_near)),
        "adjacent_mi_excess": mi - float(np.mean(s_mi)),
        "len_autocorr": ac,
        "len_autocorr_shuffled": float(np.nanmean(s_ac)),
    }


def windows(tokens: Sequence[str], size: int, max_windows: int = 3) -> list[Sequence[str]]:
    k = min(max_windows, len(tokens) // size)
    return [tokens[i * size:(i + 1) * size] for i in range(k)]


def mean_dict(dicts: list[dict]) -> dict:
    out = {}
    for key in dicts[0]:
        vals = [d[key] for d in dicts]
        out[key] = float(np.nanmean(vals))
    out["n_windows"] = len(dicts)
    return out


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 0, q=(2.5, 97.5)) -> tuple[float, float]:
    v = np.asarray(values, float)
    if v.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, v.size, size=(n_boot, v.size))].mean(axis=1)
    return (float(np.percentile(means, q[0])), float(np.percentile(means, q[1])))


def log2(x: float) -> float:
    return math.log2(x)


def neighbor_map(types: Iterable[str]) -> dict[str, set[str]]:
    """For every word type, the set of *other* types exactly one edit away.

    Candidates are found by bucketing on single-deletion variants (two strings within one edit
    always share one), then verified with `within1`."""
    types = list(set(types))
    buckets: dict[str, list[str]] = {}
    for w in types:
        variants = {w} | {w[:i] + w[i + 1:] for i in range(len(w))}
        for v in variants:
            buckets.setdefault(v, []).append(w)
    near: dict[str, set[str]] = {w: set() for w in types}
    for group in buckets.values():
        if len(group) < 2:
            continue
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                if a != b and b not in near[a] and within1(a, b):
                    near[a].add(b)
                    near[b].add(a)
    return near


def jsd(p_counts: dict, q_counts: dict) -> float:
    """Jensen-Shannon divergence (bits) between two count dictionaries."""
    keys = sorted(set(p_counts) | set(q_counts))
    p = np.array([p_counts.get(k, 0) for k in keys], float)
    q = np.array([q_counts.get(k, 0) for k in keys], float)
    if p.sum() == 0 or q.sum() == 0:
        return float("nan")
    p, q = p / p.sum(), q / q.sum()
    m = (p + q) / 2

    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)
