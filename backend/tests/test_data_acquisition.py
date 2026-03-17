import pandas as pd

from src.execution.data_acquisition import acquire_daily_ohlcv


def test_acquire_daily_ohlcv_returns_report_and_frame():
    df, report = acquire_daily_ohlcv("E01", ticker="SPY", lookback_days=365)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 50
    assert set(["open", "high", "low", "close", "volume"]).issubset(df.columns)
    assert report.evidence_item_id == "E01"
    assert report.row_count == len(df)
    assert report.usable_for_validation is True
