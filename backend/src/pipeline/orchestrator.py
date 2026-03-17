"""
Pipeline orchestrator — sequences all pipeline modules.

Round 1: Goal Intake only.
Round 2: Goal Intake → DomainFramer → ResearchSpecCompiler
         → CandidateGenerator → EvidencePlanner → ValidationPlanner
Round 3: Execution layer integrated (data/backtest/stats/comparison).
Round 4+: Audit, Recommendation, Reporting (TODO).
"""

import logging
import uuid
from datetime import datetime

from src.api.dependencies import get_audit_logger, get_store
from src.api.schemas import CreateRunRequest
from src.domain.models import AuditEvent, RunMeta, RunStatus, StatisticalSignificance
from src.pipeline.goal_intake import process_goal_intake

logger = logging.getLogger(__name__)


def execute_pipeline(run_id: str, request: CreateRunRequest) -> str:
    """
    Execute the full pipeline synchronously.
    Called in a background thread from the API endpoint.

    Returns run_id on success.
    """
    store = get_store()
    audit_logger = get_audit_logger()

    try:
        # Update status: executing
        _update_status(store, run_id, RunStatus.EXECUTING, "goal_intake", 0)

        # ---- Step 1: Goal Intake ----
        user_intent = process_goal_intake(run_id, request)
        store.save_run_object(run_id, "user_intent", user_intent)
        _log_step(audit_logger, run_id, "goal_intake")
        _update_status(store, run_id, RunStatus.EXECUTING, "domain_framing", 1)

        # ---- Step 2: Domain Framing ----
        from src.pipeline.domain_framer import frame
        domain_frame = frame(user_intent)
        store.save_run_object(run_id, "domain_frame", domain_frame)
        _log_step(audit_logger, run_id, "domain_framing")
        _update_status(store, run_id, RunStatus.EXECUTING, "research_spec", 2)

        # ---- Step 3: Research Spec Compilation ----
        from src.pipeline.research_spec_compiler import compile
        research_spec = compile(user_intent, domain_frame)
        store.save_run_object(run_id, "research_spec", research_spec)
        _log_step(audit_logger, run_id, "research_spec")
        _update_status(store, run_id, RunStatus.EXECUTING, "candidate_generation", 3)

        # ---- Step 4: Candidate Generation ----
        from src.pipeline.candidate_generator import generate
        candidates = generate(research_spec, domain_frame)
        for candidate in candidates:
            store.save_candidate_object(
                run_id, "candidates", candidate.candidate_id, candidate
            )
        _log_step(audit_logger, run_id, "candidate_generation",
                  {"candidate_count": len(candidates)})
        _update_status(store, run_id, RunStatus.EXECUTING, "evidence_planning", 4)

        # ---- Step 5: Evidence Planning ----
        from src.pipeline.evidence_planner import plan as plan_evidence
        evidence_plans = []
        for candidate in candidates:
            ep = plan_evidence(research_spec, candidate)
            store.save_candidate_object(
                run_id, "evidence_plans", candidate.candidate_id, ep
            )
            evidence_plans.append(ep)
        _log_step(audit_logger, run_id, "evidence_planning",
                  {"plans_count": len(evidence_plans)})
        _update_status(store, run_id, RunStatus.EXECUTING, "validation_planning", 5, steps_total=10)

        # ---- Step 6: Validation Planning ----
        from src.pipeline.validation_planner import plan as plan_validation
        validation_plans = []
        for candidate, ep in zip(candidates, evidence_plans):
            vp = plan_validation(research_spec, candidate, ep)
            store.save_candidate_object(
                run_id, "validation_plans", candidate.candidate_id, vp
            )
            validation_plans.append(vp)
        _log_step(audit_logger, run_id, "validation_planning",
                  {"plans_count": len(validation_plans)})


        # ---- Step 7: Data Acquisition ----
        from src.execution.data_acquisition import acquire_daily_ohlcv
        acquired_data: dict[str, object] = {}
        for candidate in candidates:
            df, dq = acquire_daily_ohlcv(
                evidence_item_id=f"{candidate.candidate_id}_price_daily",
                ticker="SPY",
            )
            store.save_candidate_object(run_id, "data_quality_reports", candidate.candidate_id, dq)
            acquired_data[candidate.candidate_id] = df
        _log_step(audit_logger, run_id, "data_acquisition",
                  {"reports_count": len(acquired_data)})
        _update_status(store, run_id, RunStatus.EXECUTING, "backtest_execution", 6, steps_total=10)

        # ---- Step 8: Backtest + Statistical Tests ----
        from src.execution.backtest_engine import run_daily_backtest
        from src.execution.statistical_tests import run_statistical_tests

        candidate_metrics: dict[str, dict[str, float]] = {}
        for candidate in candidates:
            tr = run_daily_backtest(candidate.candidate_id, acquired_data[candidate.candidate_id])

            stats = run_statistical_tests(tr.return_timeseries.net_returns if tr.return_timeseries else [])
            for metric in tr.metrics_results:
                if metric.metric_name == "sharpe":
                    metric.statistical_significance = StatisticalSignificance(
                        test_used="sharpe_t_test",
                        p_value=stats.get("sharpe_p_value"),
                    )

            store.save_candidate_object(run_id, "test_results", candidate.candidate_id, tr)
            metrics = {m.metric_name: m.actual_value for m in tr.metrics_results}
            metrics["t_test_p_value"] = stats.get("t_test_p_value") or 1.0
            metrics["in_sample_mean"] = stats.get("in_sample_mean", 0.0)
            metrics["out_of_sample_mean"] = stats.get("out_of_sample_mean", 0.0)
            candidate_metrics[candidate.candidate_id] = metrics

        _log_step(audit_logger, run_id, "backtest_execution",
                  {"test_results_count": len(candidate_metrics)})
        _update_status(store, run_id, RunStatus.EXECUTING, "candidate_comparison", 7, steps_total=10)

        # ---- Step 9: Cross-candidate Comparison ----
        from src.execution.comparison_engine import build_comparison_result

        comparison_result = build_comparison_result(run_id, candidate_metrics)
        store.save_run_object(run_id, "comparison_result", comparison_result)
        _log_step(audit_logger, run_id, "candidate_comparison")

        # ---- Step 10: Execution Package Complete (Round 3 boundary) ----
        _update_status(store, run_id, RunStatus.COMPLETED, "execution_completed", 10, steps_total=10)

        logger.info(
            f"Pipeline completed for run {run_id} "
            f"(Round 3: Execution — {len(candidates)} candidates, "
            f"{len(candidate_metrics)} executed results)"
        )
        return run_id

    except Exception as e:
        logger.exception(f"Pipeline failed for run {run_id}: {e}")

        audit_logger.append_event(AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            run_id=run_id,
            event_type="pipeline.step_failed",
            module="orchestrator",
            details={"error_type": type(e).__name__, "error_message": str(e)},
        ))

        _update_status(store, run_id, RunStatus.FAILED, error=str(e))
        raise


def _log_step(
    audit_logger, run_id: str, step_name: str, extra: dict | None = None
) -> None:
    """Log a pipeline step completion event."""
    details = {"step_name": step_name}
    if extra:
        details.update(extra)
    audit_logger.append_event(AuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.utcnow(),
        run_id=run_id,
        event_type="pipeline.step_completed",
        module=step_name,
        details=details,
    ))


def _update_status(
    store,
    run_id: str,
    status: RunStatus,
    current_step: str = "",
    steps_completed: int = 0,
    error: str | None = None,
    steps_total: int = 7,
) -> None:
    meta = RunMeta(
        run_id=run_id,
        created_at=datetime.utcnow(),
        status=status,
        current_step=current_step,
        steps_completed=steps_completed,
        error=error,
        steps_total=steps_total,
    )
    store.save_run_meta(run_id, meta)
