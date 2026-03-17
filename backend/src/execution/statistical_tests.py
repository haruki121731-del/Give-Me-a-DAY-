"""Round 3 statistical tests: t-test, Sharpe significance, and 70/30 split."""

from __future__ import annotations

import numpy as np
from scipy import stats


def run_statistical_tests(net_returns: list[float]) -> dict:
    arr = np.asarray(net_returns, dtype=float)
    if arr.size == 0:
        return {
            "t_test_p_value": None,
            "sharpe": 0.0,
            "sharpe_p_value": None,
            "in_sample_mean": 0.0,
            "out_of_sample_mean": 0.0,
        }

    t_res = stats.ttest_1samp(arr, popmean=0.0, alternative="greater")
    sharpe = _sharpe(arr)
    sharpe_p = _sharpe_p_value(arr)

    split_idx = max(1, int(0.7 * len(arr)))
    ins = arr[:split_idx]
    oos = arr[split_idx:] if split_idx < len(arr) else np.array([0.0])

    return {
        "t_test_p_value": float(t_res.pvalue) if np.isfinite(t_res.pvalue) else 1.0,
        "sharpe": float(sharpe),
        "sharpe_p_value": float(sharpe_p) if sharpe_p is not None else None,
        "in_sample_mean": float(ins.mean()),
        "out_of_sample_mean": float(oos.mean()),
    }


def _sharpe(arr: np.ndarray) -> float:
    std_r = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    if std_r < 1e-12:
        return 0.0
    return float((arr.mean() / std_r) * np.sqrt(252))


def _sharpe_p_value(arr: np.ndarray) -> float | None:
    if arr.size < 3:
        return None
    std_r = float(arr.std(ddof=1))
    if std_r < 1e-12:
        return 1.0
    t_stat = (arr.mean() / (std_r / np.sqrt(arr.size)))
    p = 1.0 - stats.t.cdf(t_stat, df=arr.size - 1)
    return float(p)
