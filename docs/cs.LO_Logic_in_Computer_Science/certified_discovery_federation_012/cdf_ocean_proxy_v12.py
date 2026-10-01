#!/usr/bin/env python3
"""Executable specification for the CDF v12 blind hidden-target proxy.

Requires NumPy 2.3.5 for the exact reference stream used in the paper.
"""
from __future__ import annotations

import math
import numpy as np

B = 10**8
ALPHA = 100
WORKERS = np.array([8, 16, 32, 64, 128], dtype=np.int64)
SEED = 20261001
REPLICATIONS = 200_000


def one_replication(rng: np.random.Generator):
    b = int(rng.integers(1, B + 1))
    u = float(rng.uniform(3.0, 6.0))
    W = int(math.floor(10.0**u))
    M = int(rng.choice(WORKERS))

    hit_lo = max(1, b - W)
    hit_hi = min(B, b + W)
    hit_len = hit_hi - hit_lo + 1
    p = hit_len / B

    # Equivalent to drawing iid uniform probes until the first hit.
    Q = int(rng.geometric(p))
    # Conditional distribution of the successful probe given a hit.
    probe = int(rng.integers(hit_lo, hit_hi + 1))

    local_lo = max(1, probe - W)
    local_hi = min(B, probe + W)
    assert local_lo <= b <= local_hi
    local_tests = b - local_lo + 1  # ascending local search

    charged_hybrid = ALPHA * Q + local_tests
    wall_hybrid = ALPHA * Q + math.ceil(local_tests / M)
    charged_brute = b
    wall_brute = math.ceil(b / M)

    return {
        "b": b,
        "W": W,
        "M": M,
        "Q": Q,
        "probe": probe,
        "local_tests": local_tests,
        "charged_hybrid": charged_hybrid,
        "wall_hybrid": wall_hybrid,
        "charged_brute": charged_brute,
        "wall_brute": wall_brute,
    }


def mean_ci95(x: np.ndarray):
    x = np.asarray(x, dtype=np.float64)
    mean = float(x.mean())
    se = float(x.std(ddof=1) / math.sqrt(len(x)))
    return mean, mean - 1.96 * se, mean + 1.96 * se


def prop_ci95(x: np.ndarray):
    x = np.asarray(x, dtype=np.float64)
    p = float(x.mean())
    se = math.sqrt(p * (1.0 - p) / len(x))
    return p, p - 1.96 * se, p + 1.96 * se


def main():
    rng = np.random.Generator(np.random.PCG64(SEED))
    rows = [one_replication(rng) for _ in range(REPLICATIONS)]

    first = rows[0]
    print("FIRST", first)

    keys = [
        "charged_brute",
        "charged_hybrid",
        "wall_brute",
        "wall_hybrid",
    ]
    arrays = {k: np.array([r[k] for r in rows], dtype=np.float64) for k in keys}
    m = np.array([r["M"] for r in rows], dtype=np.int64)

    for k in keys:
        print(k, mean_ci95(arrays[k]))

    work_win = arrays["charged_hybrid"] < arrays["charged_brute"]
    wall_win = arrays["wall_hybrid"] < arrays["wall_brute"]
    print("work_win", prop_ci95(work_win))
    print("wall_win", prop_ci95(wall_win))
    print("mean_ratio_work", arrays["charged_brute"].mean() / arrays["charged_hybrid"].mean())
    print("mean_ratio_wall", arrays["wall_brute"].mean() / arrays["wall_hybrid"].mean())

    for M in WORKERS:
        mask = m == M
        p = float(wall_win[mask].mean())
        ratio = float(arrays["wall_brute"][mask].mean() / arrays["wall_hybrid"][mask].mean())
        print("M", int(M), "n", int(mask.sum()), "wall_win", p, "mean_ratio", ratio)


if __name__ == "__main__":
    main()
