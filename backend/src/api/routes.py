"""
All API endpoints for Give Me a DAY v1.

Endpoint spec follows api_data_flow.md §5.
"""

import threading
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.api.dependencies import get_audit_logger, get_store
from src.api.schemas import (
    ApproveRequest,
    ApproveResponse,
    CreateRunRequest,
    CreateRunResponse,
    PaperRunStatusResponse,
    PreflightRequest,
    PreflightSubmitRequest,
    PreflightSubmitResponse,
    ReApproveRequest,
    ReApproveResponse,
    RunStatusResponse,
    StopResponse,
)
from src.companion.approval_context_builder import build_approval_context
from src.companion.constraint_inferrer import apply_answers
from src.companion.contradiction_detector import detect_contradictions
from src.companion.models import ApprovalContext, CompanionGoalResponse
from src.companion.question_builder import build_questions
from src.companion.trigger_evaluator import evaluate_triggers, needs_clarification
from src.domain.models import AuditEvent, RunMeta, RunStatus
from src.pipeline.orchestrator import execute_pipeline

router = APIRouter()


# ---- Health check ----

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "give-me-a-day", "version": "1.0.0"}


# ---- Companion AI endpoints ----

@router.post("/runs/preflight", response_model=CompanionGoalResponse)
def preflight_goal(request: PreflightRequest):
    """
    Evaluate a goal before submission.
    Returns trigger evaluation, contradiction notices, and clarification questions.
    No run is created. Preflight is optional — clients may skip to POST /runs directly.
    """
    contradictions = detect_contradictions(
        raw_goal=request.goal,
        success_criteria=request.success_criteria,
        risk=request.risk,
        time_horizon=request.time_horizon,
        must_not_do=request.exclusions,
    )
    trigger_result = evaluate_triggers(
        goal=request.goal,
        success_criteria=request.success_criteria,
        risk=request.risk,
        time_horizon=request.time_horizon,
    )
    questions = build_questions(trigger_result)
    clarification_needed = needs_clarification(trigger_result, contradictions)

    # Inferences from known fields (no answers yet — surface what was already provided)
    inferences: list[dict] = []
    if request.risk:
        inferences.append({"field": "risk_preference", "from_text": request.risk,
                            "inferred_value": request.risk})
    if request.time_horizon:
        inferences.append({"field": "time_horizon_preference", "from_text": request.time_horizon,
                            "inferred_value": request.time_horizon})

    return CompanionGoalResponse(
        needs_clarification=clarification_needed,
        questions=questions,
        contradictions=contradictions,
        inferences=inferences,
    )


@router.post("/runs/preflight/submit", response_model=PreflightSubmitResponse)
def preflight_submit(request: PreflightSubmitRequest):
    """
    Ingest answers to clarification questions and return a refined CreateRunRequest.
    No run is created. Client reviews the inference summary, then calls POST /runs.
    """
    inference = apply_answers(
        answers=request.answers,
        existing_risk=request.original_request.risk,
        existing_time_horizon=request.original_request.time_horizon,
        existing_success_criteria=request.original_request.success_criteria,
    )

    # Build refined request
    refined = CreateRunRequest(
        goal=request.original_request.goal,
        success_criteria=inference.success_definition or request.original_request.success_criteria,
        risk=inference.risk_preference or request.original_request.risk,
        time_horizon=inference.time_horizon_preference or request.original_request.time_horizon,
        exclusions=request.original_request.exclusions,
    )

    return PreflightSubmitResponse(
        refined_request=refined,
        inference_summary=inference.inferences_made,
        open_uncertainties=inference.open_uncertainties,
        kpi_anchor=inference.kpi_anchor,
    )


@router.get("/runs/{run_id}/approval-context", response_model=ApprovalContext)
def get_approval_context(run_id: str, candidate_id: str, virtual_capital: float = 1_000_000):
    """
    Return Companion AI approval disclosure content for a specific candidate.
    Called when ApprovalPage loads — before the user clicks Approve.
    """
    store = get_store()
    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    # Load candidate cards
    try:
        candidate_cards = store.load_presentation(run_id, "candidate_cards.json")
        if not isinstance(candidate_cards, list):
            candidate_cards = [candidate_cards]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Candidate cards not available yet")

    # Validate the candidate_id exists
    card_ids = [c.get("candidate_id") for c in candidate_cards]
    if candidate_id not in card_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate '{candidate_id}' not found in this run",
        )

    # Load evidence plans for this run
    evidence_plans = store.load_all_candidate_objects(run_id, "evidence_plans")

    # Load user_intent for KPI anchor
    try:
        user_intent = store.load_run_object(run_id, "user_intent")
    except FileNotFoundError:
        user_intent = None

    return build_approval_context(
        run_id=run_id,
        candidate_id=candidate_id,
        candidate_cards=candidate_cards,
        evidence_plans=evidence_plans,
        user_intent=user_intent,
        virtual_capital=virtual_capital,
    )


# ---- Pipeline endpoints ----

@router.post("/runs", response_model=CreateRunResponse, status_code=202)
def create_run(request: CreateRunRequest):
    """Start a new pipeline run. Returns immediately with run_id."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    store = get_store()
    audit_logger = get_audit_logger()

    # Save initial run metadata
    meta = RunMeta(
        run_id=run_id,
        created_at=datetime.utcnow(),
        status=RunStatus.PENDING,
    )
    store.save_run_meta(run_id, meta)

    # Log pipeline start event
    audit_logger.append_event(AuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.utcnow(),
        run_id=run_id,
        event_type="pipeline.started",
        module="orchestrator",
        details={"raw_goal": request.goal},
    ))

    # Execute pipeline in background thread
    thread = threading.Thread(
        target=execute_pipeline,
        args=(run_id, request),
        daemon=True,
    )
    thread.start()

    return CreateRunResponse(
        run_id=run_id,
        status_url=f"/api/v1/runs/{run_id}/status",
    )


@router.get("/runs/{run_id}/status", response_model=RunStatusResponse)
def get_run_status(run_id: str):
    """Poll pipeline progress."""
    store = get_store()
    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    meta = store.load_run_meta(run_id)
    return RunStatusResponse(**meta)


@router.get("/runs/{run_id}/planning")
def get_planning_result(run_id: str):
    """Get planning pipeline results (Round 2: domain frame, spec, candidates, plans)."""
    store = get_store()
    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    meta = store.load_run_meta(run_id)
    if meta.get("status") not in ("completed", "executing"):
        raise HTTPException(
            status_code=409,
            detail=f"Run status is '{meta.get('status')}', planning not available",
        )

    result: dict = {"run_id": run_id}

    # Load each planning artifact if available
    for key in ["user_intent", "domain_frame", "research_spec"]:
        try:
            result[key] = store.load_run_object(run_id, key)
        except FileNotFoundError:
            pass

    # Load per-candidate objects
    result["candidates"] = store.load_all_candidate_objects(run_id, "candidates")
    result["evidence_plans"] = store.load_all_candidate_objects(run_id, "evidence_plans")
    result["validation_plans"] = store.load_all_candidate_objects(run_id, "validation_plans")

    return result


@router.get("/runs/{run_id}/result")
def get_run_result(run_id: str):
    """Get candidate presentation after pipeline completion."""
    store = get_store()
    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    meta = store.load_run_meta(run_id)
    if meta.get("status") != "completed":
        raise HTTPException(status_code=409, detail=f"Run status is '{meta.get('status')}', not 'completed'")

    try:
        cards = store.load_presentation(run_id, "candidate_cards.json")
        context = store.load_presentation(run_id, "presentation_context.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Results not yet available")

    return {
        "run_id": run_id,
        "candidate_cards": cards,
        "presentation_context": context,
        "approval_url": f"/api/v1/runs/{run_id}/approve",
    }


@router.get("/runs/{run_id}/export")
def get_run_export(run_id: str):
    """Download Markdown export of recommendation package."""
    store = get_store()
    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        content = store.load_markdown_export(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Export not available")

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=content, media_type="text/markdown")


# ---- Approval endpoint ----

@router.post("/runs/{run_id}/approve", response_model=ApproveResponse, status_code=201)
def approve_run(run_id: str, request: ApproveRequest):
    """Approve a candidate and start Paper Run."""
    store = get_store()
    audit_logger = get_audit_logger()

    if not store.run_exists(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    # Load recommendation (must exist before approval)
    try:
        rec_data = store.load_run_object(run_id, "recommendation")
    except FileNotFoundError:
        raise HTTPException(
            status_code=409,
            detail="Recommendation not yet available. Pipeline must complete first.",
        )

    from src.domain.models import Recommendation
    recommendation = Recommendation(**rec_data)

    # Validate confirmations
    from src.pipeline.approval_controller import (
        ApprovalError,
        create_approval,
        validate_confirmations,
    )

    try:
        confirmations = validate_confirmations(request.user_confirmations)
    except ApprovalError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create approval
    try:
        approval = create_approval(
            run_id=run_id,
            candidate_id=request.candidate_id,
            confirmations=confirmations,
            recommendation=recommendation,
            virtual_capital=request.virtual_capital,
        )
    except ApprovalError as e:
        raise HTTPException(status_code=400, detail=str(e))

    store.save_approval(run_id, approval)

    # Initialize Paper Run
    from src.pipeline.runtime_controller import initialize_paper_run

    paper_run_state = initialize_paper_run(approval)
    store.save_paper_run_state(paper_run_state.paper_run_id, paper_run_state)

    # Audit log
    audit_logger.append_event(AuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.utcnow(),
        run_id=run_id,
        event_type="approval.created",
        module="approval_controller",
        details={
            "approval_id": approval.approval_id,
            "candidate_id": approval.candidate_id,
            "paper_run_id": paper_run_state.paper_run_id,
        },
    ))

    return ApproveResponse(
        approval_id=approval.approval_id,
        paper_run_id=paper_run_state.paper_run_id,
        status_url=f"/api/v1/paper-runs/{paper_run_state.paper_run_id}",
    )


# ---- Paper Run endpoints ----

@router.get("/paper-runs/{pr_id}", response_model=PaperRunStatusResponse)
def get_paper_run_status(pr_id: str):
    """Get Paper Run status card."""
    store = get_store()
    if not store.paper_run_exists(pr_id):
        raise HTTPException(status_code=404, detail="Paper Run not found")

    state = store.load_paper_run_state(pr_id)
    snapshot = state.get("current_snapshot", {})
    safety = state.get("safety_status", {})
    schedule = state.get("schedule", {})

    return PaperRunStatusResponse(
        status=state.get("status", "unknown"),
        day_count=snapshot.get("day_count", 0),
        current_value=snapshot.get("virtual_capital_current", 0.0),
        total_return_pct=snapshot.get("total_return_pct", 0.0),
        safety_status="breached" if safety.get("any_breached") else "all_clear",
        next_report=schedule.get("next_monthly_report"),
        next_re_eval=schedule.get("next_quarterly_re_evaluation"),
    )


@router.post("/paper-runs/{pr_id}/stop", response_model=StopResponse)
def stop_paper_run(pr_id: str):
    """Manually stop a Paper Run."""
    store = get_store()
    if not store.paper_run_exists(pr_id):
        raise HTTPException(status_code=404, detail="Paper Run not found")

    # TODO: Round 6 — Update PaperRunState to halted, record in halt_history
    return StopResponse(status="halted")


@router.post("/paper-runs/{pr_id}/re-approve", response_model=ReApproveResponse, status_code=201)
def re_approve_paper_run(pr_id: str, request: ReApproveRequest):
    """Re-approve after halt or re-evaluation."""
    store = get_store()
    if not store.paper_run_exists(pr_id):
        raise HTTPException(status_code=404, detail="Paper Run not found")

    # TODO: Round 6 — Create new Approval, resume or start new PaperRun
    new_approval_id = f"reap_{uuid.uuid4().hex[:8]}"
    return ReApproveResponse(new_approval_id=new_approval_id, status="running")


@router.get("/paper-runs/{pr_id}/reports")
def list_monthly_reports(pr_id: str):
    """List all monthly reports for a Paper Run."""
    store = get_store()
    if not store.paper_run_exists(pr_id):
        raise HTTPException(status_code=404, detail="Paper Run not found")

    reports = store.load_monthly_reports(pr_id)
    return reports


@router.get("/paper-runs/{pr_id}/reports/{report_id}")
def get_monthly_report(pr_id: str, report_id: str):
    """Get a specific monthly report."""
    store = get_store()
    try:
        return store.load_monthly_report(pr_id, report_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")
