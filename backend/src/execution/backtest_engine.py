"""Round 3 vectorized daily backtest engine (momentum/factor-oriented)."""

from __future__ import annotations

import uuid

import numpy as np
import pandas as pd

from src.domain.models import (
    ExecutionStatus,
    MetricResult,
    ReturnTimeseries,
    StatisticalSignificance,
    TestResult,
    TestResultOutcome,
)


def run_daily_backtest(candidate_id: str, prices: pd.DataFrame, test_id: str = "offline_backtest") -> TestResult:
    """Run a simple long/flat monthly-rebalanced momentum backtest."""
    df = prices.copy()
    df = df.sort_index()
    ret = df["close"].pct_change().fillna(0.0)
    signal = (df["close"].pct_change(20) > 0).astype(float)

    # monthly rebalance: signal frozen within month
    month_bucket = pd.Series(df.index.to_period("M"), index=df.index)
    rebalance_signal = signal.groupby(month_bucket).transform("first").shift(1).fillna(0.0)

    gross = rebalance_signal * ret
    turnover = rebalance_signal.diff().abs().fillna(0.0)
    cost = 0.001 * turnover
    net = gross - cost

    cumulative = (1 + net).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1.0

    sharpe = _annualized_sharpe(net)
    total_return = float(cumulative.iloc[-1] - 1.0)
    max_dd = float(drawdown.min())

    metrics = [
        MetricResult(
            metric_name="total_return",
            actual_value=total_return,
            pass_threshold="> 0.00",
            fail_threshold="<= 0.00",
            result=TestResultOutcome.PASS if total_return > 0 else TestResultOutcome.FAIL,
        ),
        MetricResult(
            metric_name="sharpe",
            actual_value=float(sharpe),
            pass_threshold="> 0.50",
            fail_threshold="<= 0.00",
            result=TestResultOutcome.PASS if sharpe > 0.5 else TestResultOutcome.MIXED,
            statistical_significance=StatisticalSignificance(test_used="sharpe_estimate"),
        ),
        MetricResult(
            metric_name="max_drawdown",
            actual_value=max_dd,
            pass_threshold="> -0.20",
            fail_threshold="<= -0.30",
            result=TestResultOutcome.PASS if max_dd > -0.2 else TestResultOutcome.FAIL,
        ),
    ]

    failures = [m for m in metrics if m.result == TestResultOutcome.FAIL]
    overall = TestResultOutcome.PASS if not failures else TestResultOutcome.FAIL

    return TestResult(
        test_result_id=f"tr_{uuid.uuid4().hex[:8]}",
        test_id=test_id,
        candidate_id=candidate_id,
        execution_status=ExecutionStatus.COMPLETED,
        metrics_results=metrics,
        overall_result=overall,
        return_timeseries=ReturnTimeseries(
            dates=[d.date().isoformat() for d in df.index],
            gross_returns=[float(x) for x in gross.values],
            net_returns=[float(x) for x in net.values],
            benchmark_returns=[float(x) for x in ret.values],
        ),
        data_quality_flags=[],
        pit_compliance="none",
    )


def _annualized_sharpe(net_returns: pd.Series) -> float:
    mu = float(net_returns.mean())
    std_r = float(net_returns.std(ddof=1))
    if std_r < 1e-12:
        return 0.0
    return (mu / std_r) * np.sqrt(252)
