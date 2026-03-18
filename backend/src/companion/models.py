"""
Companion AI v1 schema objects.

These models are companion-internal.
They do not extend or modify any existing domain model.
CompanionContext is attached to UserIntent and Approval as Optional[dict]
to avoid circular imports — pipeline logic never reads it.
"""

from typing import Optional

from pydantic import BaseModel, Field


class CompanionQuestion(BaseModel):
    id: str  # "Q-SUCCESS" | "Q-RISK" | "Q-TIME" | "Q-SCOPE" | "Q-REFINE"
    text: str
    type: str  # "free_text" | "redirect_notice"
    options: list[str] = Field(default_factory=list)
    optional: bool = False


class CompanionGoalResponse(BaseModel):
    needs_clarification: bool
    questions: list[CompanionQuestion]
    contradictions: list[str]  # Human-readable contradiction notices
    inferences: list[dict]     # [{field, from_text, inferred_value}]


class CompanionAnswers(BaseModel):
    answers: dict[str, str]  # question_id -> free-text or selected option


class StopConditionTranslation(BaseModel):
    id: str  # "SC-01" | "SC-02" | "SC-03" | "SC-04"
    plain_language: str
    virtual_capital_amount: Optional[float] = None  # SC-01 only


class RiskAnnotation(BaseModel):
    original_risk_text: str
    annotation: str


class ComprehensionCheck(BaseModel):
    question: str
    options: list[str]   # A through D
    correct_index: int   # 0-based


class ApprovalContext(BaseModel):
    run_id: str
    candidate_id: str
    authority_disclosure: str
    kpi_alignment: dict  # {aligned: bool, anchor: str, candidate_band: str, note: str}
    stop_condition_translations: list[StopConditionTranslation]
    risk_annotations: list[RiskAnnotation]
    data_access_disclosure: str
    paper_run_explanation: str
    comprehension_check: ComprehensionCheck


class CompanionContext(BaseModel):
    # Attached to UserIntent.companion_context and Approval.companion_context
    # Optional tracing only — pipeline logic never reads this.
    questions_asked: list[str] = Field(default_factory=list)
    inferences_made: list[dict] = Field(default_factory=list)
    contradictions_flagged: list[str] = Field(default_factory=list)
    comprehension_check_passed: bool = False
    comprehension_check_attempts: int = 0
    companion_active: bool = True
