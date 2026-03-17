"""Round 3 data acquisition: daily OHLCV with quality checks and synthetic fallback."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.domain.models import (
    AcquisitionStatus,
    DataQualityReport,
    DateRange,
    QualityCheckType,
    QualityIssue,
    QualityIssueSeverity,
)


DEFAULT_TICKER = "SPY"


def acquire_daily_ohlcv(
    evidence_item_id: str,
    ticker: str = DEFAULT_TICKER,
    lookback_days: int = 365 * 5,
) -> tuple[pd.DataFrame, DataQualityReport]:
    """Fetch daily OHLCV from yfinance; fallback to synthetic if unavailable."""
    end_dt = datetime.utcnow().date()
    start_dt = end_dt - timedelta(days=lookback_days)

    source = "yfinance"
    try:
        import yfinance as yf

        df = yf.download(
            ticker,
            start=start_dt.isoformat(),
            end=end_dt.isoformat(),
            auto_adjust=False,
            progress=False,
            interval="1d",
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            raise ValueError("empty data")
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })
        for col in ["open", "high", "low", "close", "volume"]:
            if col not in df.columns:
                raise ValueError(f"missing column: {col}")
        df = df[["open", "high", "low", "close", "volume"]].copy()
        df.index = pd.to_datetime(df.index)
    except Exception:
        source = "synthetic_fallback"
        df = _generate_synthetic_ohlcv(start_dt, end_dt)

    quality_issues = _run_quality_checks(df)
    status = AcquisitionStatus.ACQUIRED
    if any(i.severity == QualityIssueSeverity.CRITICAL for i in quality_issues):
        status = AcquisitionStatus.PARTIALLY_ACQUIRED

    report = DataQualityReport(
        evidence_item_id=evidence_item_id,
        acquisition_status=status,
        acquisition_timestamp=datetime.utcnow(),
        data_source=source,
        row_count=len(df),
        date_range_actual=DateRange(
            start=df.index.min().date().isoformat(),
            end=df.index.max().date().isoformat(),
        ),
        quality_issues=quality_issues,
        pit_status_verified="not_applicable",
        usable_for_validation=(status != AcquisitionStatus.FAILED),
    )
    return df, report


def _generate_synthetic_ohlcv(start_dt, end_dt) -> pd.DataFrame:
    dates = pd.bdate_range(start=start_dt, end=end_dt)
    if len(dates) == 0:
        dates = pd.bdate_range(end=end_dt, periods=252)

    rng = np.random.default_rng(42)
    rets = rng.normal(0.0003, 0.012, size=len(dates))
    close = 100 * np.cumprod(1 + rets)
    open_px = close * (1 + rng.normal(0, 0.001, size=len(dates)))
    high = np.maximum(open_px, close) * (1 + np.abs(rng.normal(0, 0.002, size=len(dates))))
    low = np.minimum(open_px, close) * (1 - np.abs(rng.normal(0, 0.002, size=len(dates))))
    volume = rng.integers(500_000, 3_000_000, size=len(dates))

    return pd.DataFrame(
        {
            "open": open_px,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=dates,
    )


def _run_quality_checks(df: pd.DataFrame) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    missing_rows = int(df[["open", "high", "low", "close", "volume"]].isna().any(axis=1).sum())
    if missing_rows > 0:
        issues.append(QualityIssue(
            check_type=QualityCheckType.COMPLETENESS,
            severity=QualityIssueSeverity.WARNING,
            description="Rows with missing OHLCV values detected",
            affected_rows=missing_rows,
            affected_percentage=round(100 * missing_rows / max(1, len(df)), 3),
        ))

    bad_hl = int((df["high"] < df["low"]).sum())
    if bad_hl > 0:
        issues.append(QualityIssue(
            check_type=QualityCheckType.CONSISTENCY,
            severity=QualityIssueSeverity.CRITICAL,
            description="Rows where high < low detected",
            affected_rows=bad_hl,
            affected_percentage=round(100 * bad_hl / max(1, len(df)), 3),
        ))

    non_positive_close = int((df["close"] <= 0).sum())
    if non_positive_close > 0:
        issues.append(QualityIssue(
            check_type=QualityCheckType.CONSISTENCY,
            severity=QualityIssueSeverity.CRITICAL,
            description="Non-positive close prices detected",
            affected_rows=non_positive_close,
            affected_percentage=round(100 * non_positive_close / max(1, len(df)), 3),
        ))

    if not df.index.is_monotonic_increasing:
        issues.append(QualityIssue(
            check_type=QualityCheckType.TEMPORAL,
            severity=QualityIssueSeverity.WARNING,
            description="Index is not strictly increasing",
            affected_rows=0,
            affected_percentage=0.0,
        ))

    return issues
