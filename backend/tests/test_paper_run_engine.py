from datetime import datetime

from src.domain.models import Approval, CurrentSnapshot, PaperRunState, UserConfirmations
from src.execution.paper_run_engine import update_daily_mark_to_market


def test_paper_run_halts_on_drawdown_breach():
    approval = Approval(
        approval_id="ap_001",
        run_id="run_001",
        candidate_id="C01",
        approved_at=datetime.utcnow(),
        user_confirmations=UserConfirmations(
            risks_reviewed=True,
            stop_conditions_reviewed=True,
            paper_run_understood=True,
        ),
    )
    state = PaperRunState(
        paper_run_id="pr_001",
        approval_id=approval.approval_id,
        candidate_id="C01",
        started_at=datetime.utcnow(),
        current_snapshot=CurrentSnapshot(
            virtual_capital_initial=100.0,
            virtual_capital_current=100.0,
        ),
    )

    state = update_daily_mark_to_market(state, daily_return=-0.25, benchmark_return=0.0)
    assert state.status.value == "halted"
    assert state.safety_status.any_breached is True
    assert len(state.halt_history) == 1
    assert state.halt_history[0].condition_id == "SC-01"
