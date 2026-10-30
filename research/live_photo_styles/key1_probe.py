"""HYPOTHESIS TOOL: probe the layout of a short Live-Photo-video key '1' vector.

The iOS 27.2 IMG_3940 notes report a per-frame key '1' of 1152 bytes = 576
little-endian float16 values. No such file is in this repo's sample set, so the
layout is unknown. This tool does not decode anything; it scores candidate
factorizations of N with a structure test that needs no paired HEIC:

* In HEIC Key 1 (12x9 grid x 8 planes x 3 outputs x 10 basis terms) a neutral
  transform puts ~1.0 on each output's own linear term and ~0 elsewhere. If the
  video vector is a reduced version of that, values near 1.0 should repeat with a
  stride equal to the size of one "cell" (or one output row).
* For each candidate (cells, outputs, terms) we reshape and measure how much of
  the variance is explained by the per-(output, term) mean across cells. A
  correct split gives high explained variance because cells are similar.

Usage: python3 key1_probe.py KEY1.bin   (raw payload, f16 LE)
"""
from __future__ import annotations

import json
import sys

import numpy as np


def factorizations(n: int):
    out = []
    for outputs in (1, 3):
        for terms in (1, 2, 3, 4, 6, 9, 10, 12):
            if n % (outputs * terms):
                continue
            cells = n // (outputs * terms)
            out.append((cells, outputs, terms))
    return out


def probe(vec: np.ndarray, near_one: float = 0.15) -> dict:
    v = np.asarray(vec, dtype=np.float64).ravel()
    n = v.size
    ones = np.flatnonzero(np.abs(v - 1.0) < near_one)
    strides = np.diff(ones)
    stride_hist = {int(k): int(c) for k, c in zip(*np.unique(strides, return_counts=True))} if strides.size else {}
    x = v - v.mean()
    ac = np.array([np.dot(x[:-k], x[k:]) / max(np.dot(x, x), 1e-12) for k in range(1, min(n // 2, 300))])
    top_lags = (np.argsort(ac)[::-1][:5] + 1).tolist()
    scores = []
    for cells, outputs, terms in factorizations(n):
        a = v.reshape(cells, outputs * terms)
        resid = a - a.mean(axis=0, keepdims=True)
        tot = ((v - v.mean()) ** 2).sum()
        ev = 1.0 - (resid ** 2).sum() / tot if tot > 0 else 0.0
        scores.append({"cells": cells, "outputs": outputs, "terms": terms, "explained_by_cell_mean": round(float(ev), 4)})
    scores.sort(key=lambda s: -s["explained_by_cell_mean"])
    return {"n": n, "min": float(v.min()), "max": float(v.max()), "n_near_one": int(ones.size),
            "near_one_stride_hist": stride_hist, "autocorr_top_lags": top_lags, "factorization_scores": scores[:10]}


if __name__ == "__main__":
    raw = open(sys.argv[1], "rb").read()
    print(json.dumps(probe(np.frombuffer(raw, "<f2")), indent=2))
