"""Round 3 paper run engine: daily mark-to-market and stop-condition checks."""

from __future__ import annotations

from datetime import datetime

from src.domain.models import CurrentSnapshot, HaltEvent, NearestCondition, PaperRunState, PaperRunStatus


def update_daily_mark_to_market(
    state: PaperRunState,
    daily_return: float,
    benchmark_return: float,
    sigma_estimate: float = 0.02,
    data_quality_fail_streak: int = 0,
) -> PaperRunState:
    """Advance Paper Run by one day and evaluate stop conditions."""
    snap = state.current_snapshot
    if snap.virtual_capital_initial <= 0:
        snap.virtual_capital_initial = max(1.0, snap.virtual_capital_current)

    snap.day_count += 1
    snap.virtual_capital_current = float(snap.virtual_capital_current * (1.0 + daily_return))
    snap.total_return_pct = float((snap.virtual_capital_current / snap.virtual_capital_initial - 1.0) * 100.0)

    peak = max(snap.virtual_capital_initial, snap.virtual_capital_current)
    dd = (snap.virtual_capital_current / peak - 1.0) * 100.0
    snap.current_drawdown_pct = float(min(0.0, dd))

    breached, condition_id = _evaluate_stop_conditions(
        drawdown_pct=snap.current_drawdown_pct,
        excess_return=daily_return - benchmark_return,
        sigma_estimate=sigma_estimate,
        data_quality_fail_streak=data_quality_fail_streak,
    )

    state.safety_status.any_breached = breached
    state.safety_status.nearest_condition = NearestCondition(
        id="SC-01",
        current_value=snap.current_drawdown_pct,
        threshold=-20.0,
        distance_pct=abs((-20.0) - snap.current_drawdown_pct),
    )

    if breached:
        state.status = PaperRunStatus.HALTED
        state.halt_history.append(HaltEvent(
            halted_at=datetime.utcnow().isoformat(),
            condition_id=condition_id,
            resumed_at=None,
            re_approval_id=None,
        ))

    state.current_snapshot = CurrentSnapshot(**snap.model_dump())
    return state


def _evaluate_stop_conditions(
    drawdown_pct: float,
    excess_return: float,
    sigma_estimate: float,
    data_quality_fail_streak: int,
) -> tuple[bool, str]:
    if drawdown_pct <= -20.0:
        return True, "SC-01"

    if sigma_estimate > 0 and abs(excess_return) > (3.0 * sigma_estimate):
        return True, "SC-03"

    if data_quality_fail_streak >= 3:
        return True, "SC-04"

    return False, ""
