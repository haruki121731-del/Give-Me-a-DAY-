from src.execution.backtest_engine import run_daily_backtest
from src.execution.data_acquisition import acquire_daily_ohlcv


def test_backtest_produces_test_result():
    df, _ = acquire_daily_ohlcv("E02", lookback_days=365)
    tr = run_daily_backtest("C01", df)

    assert tr.candidate_id == "C01"
    assert tr.execution_status.value == "completed"
    assert tr.return_timeseries is not None
    assert len(tr.return_timeseries.net_returns) == len(df)
    assert len(tr.metrics_results) >= 3
