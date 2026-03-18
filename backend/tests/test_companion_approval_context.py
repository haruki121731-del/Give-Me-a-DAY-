"""
Tests for companion/approval_context_builder.py

Covers authority disclosure, KPI alignment, stop condition translations,
risk annotations, data access disclosure, paper run explanation,
and comprehension check generation.
"""

import pytest
from src.companion.approval_context_builder import (
    _annotate_risk,
    _build_authority_disclosure,
    _build_comprehension_check,
    _build_data_access_disclosure,
    _build_kpi_alignment,
    _build_paper_run_explanation,
    _build_stop_translations,
    build_approval_context,
)
from src.companion.models import ApprovalContext


# ── Authority disclosure ──────────────────────────────────────────────────────

def test_authority_disclosure_contains_candidate_name():
    text = _build_authority_disclosure("Momentum Alpha", 1_000_000)
    assert "Momentum Alpha" in text


def test_authority_disclosure_contains_formatted_capital():
    text = _build_authority_disclosure("Test Strategy", 1_000_000)
    assert "1,000,000" in text


def test_authority_disclosure_contains_all_five_items():
    text = _build_authority_disclosure("Test Strategy", 1_000_000)
    assert "1." in text
    assert "2." in text
    assert "3." in text
    assert "4." in text
    assert "5." in text


def test_authority_disclosure_no_real_money_language():
    text = _build_authority_disclosure("Test Strategy", 1_000_000)
    assert "No real money" in text


# ── Stop condition translations ───────────────────────────────────────────────

def test_stop_translations_returns_4_conditions():
    translations = _build_stop_translations(1_000_000)
    assert len(translations) == 4
    ids = [t.id for t in translations]
    assert ids == ["SC-01", "SC-02", "SC-03", "SC-04"]


def test_sc01_includes_capital_amount():
    translations = _build_stop_translations(1_000_000)
    sc01 = next(t for t in translations if t.id == "SC-01")
    assert sc01.virtual_capital_amount == 1_000_000
    assert "800,000" in sc01.plain_language  # 80% of 1,000,000


def test_sc01_threshold_scales_with_capital():
    translations = _build_stop_translations(500_000)
    sc01 = next(t for t in translations if t.id == "SC-01")
    assert "400,000" in sc01.plain_language  # 80% of 500,000


def test_sc02_mentions_consecutive_months():
    translations = _build_stop_translations(1_000_000)
    sc02 = next(t for t in translations if t.id == "SC-02")
    assert "3" in sc02.plain_language
    assert sc02.virtual_capital_amount is None


def test_sc03_mentions_sigma():
    translations = _build_stop_translations(1_000_000)
    sc03 = next(t for t in translations if t.id == "SC-03")
    assert "3 standard deviations" in sc03.plain_language


def test_sc04_mentions_data_quality():
    translations = _build_stop_translations(1_000_000)
    sc04 = next(t for t in translations if t.id == "SC-04")
    assert "data" in sc04.plain_language.lower()


# ── Risk annotations ──────────────────────────────────────────────────────────

def test_crowding_risk_annotated():
    annotation = _annotate_risk("factor crowding risk")
    assert "same signals" in annotation.annotation or "crowding" in annotation.annotation.lower()


def test_regime_risk_annotated():
    annotation = _annotate_risk("regime change sensitivity")
    assert "market" in annotation.annotation.lower()


def test_overfitting_risk_annotated():
    annotation = _annotate_risk("risk of overfitting to historical data")
    assert "historical data" in annotation.annotation


def test_unknown_risk_gets_fallback():
    annotation = _annotate_risk("some unusual exotic risk factor")
    assert annotation.original_risk_text == "some unusual exotic risk factor"
    assert "No additional" in annotation.annotation


def test_risk_annotation_preserves_original_text():
    annotation = _annotate_risk("liquidity risk in small cap stocks")
    assert annotation.original_risk_text == "liquidity risk in small cap stocks"


# ── KPI alignment ─────────────────────────────────────────────────────────────

def test_kpi_aligned_when_target_within_band():
    result = _build_kpi_alignment("10% per year", 8.0, 15.0)
    assert result["aligned"] is True
    assert "10" in result["anchor"]


def test_kpi_misaligned_when_target_well_above_band():
    result = _build_kpi_alignment("50% per year", 5.0, 10.0)
    assert result["aligned"] is False
    assert "below" in result["note"].lower() or "above" in result["note"].lower()


def test_kpi_overdelivery_noted_when_target_well_below():
    result = _build_kpi_alignment("2% per year", 10.0, 20.0)
    assert result["aligned"] is True
    assert "above" in result["note"].lower() or "more than" in result["note"].lower()


def test_kpi_no_anchor_returns_aligned():
    result = _build_kpi_alignment(None, 8.0, 15.0)
    assert result["aligned"] is True
    assert "No specific" in result["anchor"]


def test_kpi_qualitative_anchor():
    result = _build_kpi_alignment("beat the market", 8.0, 15.0)
    assert result["aligned"] is True
    assert "beat the market" in result["anchor"]


# ── Data access disclosure ────────────────────────────────────────────────────

def test_data_access_price_items_counted():
    evidence = [
        {"category": "price", "description": "JPY equity prices"},
        {"category": "price", "description": "US equity prices"},
    ]
    text = _build_data_access_disclosure(evidence)
    assert "2 securities" in text
    assert "Yahoo Finance" in text


def test_data_access_includes_fred_for_macro():
    evidence = [
        {"category": "price", "description": "equity"},
        {"category": "macro", "description": "fed rate"},
    ]
    text = _build_data_access_disclosure(evidence)
    assert "FRED" in text


def test_data_access_includes_cot_for_flow():
    evidence = [{"category": "flow", "description": "COT data"}]
    text = _build_data_access_disclosure(evidence)
    assert "CFTC" in text


def test_data_access_public_and_free_statement():
    evidence = [{"category": "price", "description": "equities"}]
    text = _build_data_access_disclosure(evidence)
    assert "public and free" in text


def test_data_access_empty_evidence_fallback():
    text = _build_data_access_disclosure([])
    assert "public sources" in text.lower()


# ── Paper run explanation ─────────────────────────────────────────────────────

def test_paper_run_explanation_no_real_money():
    text = _build_paper_run_explanation(1_000_000)
    assert "no real money" in text.lower()


def test_paper_run_explanation_contains_capital():
    text = _build_paper_run_explanation(1_000_000)
    assert "1,000,000" in text


def test_paper_run_explanation_v1_only():
    text = _build_paper_run_explanation(1_000_000)
    assert "v1" in text.lower() or "Paper Run" in text


# ── Comprehension check ───────────────────────────────────────────────────────

def test_comprehension_check_has_4_options():
    check = _build_comprehension_check(1_000_000)
    assert len(check.options) == 4


def test_comprehension_check_correct_index_is_1():
    check = _build_comprehension_check(1_000_000)
    assert check.correct_index == 1  # B is correct


def test_comprehension_check_question_contains_capital():
    check = _build_comprehension_check(1_000_000)
    assert "1,000,000" in check.question


def test_comprehension_check_correct_answer_mentions_stop():
    check = _build_comprehension_check(1_000_000)
    correct = check.options[check.correct_index]
    assert "stop" in correct.lower() or "Stop" in correct


# ── build_approval_context integration ───────────────────────────────────────

_SAMPLE_CARDS = [
    {
        "candidate_id": "cand_001",
        "display_name": "Momentum Alpha",
        "expected_return_band": {"low_pct": 8.0, "high_pct": 14.0, "basis": "backtest", "disclaimer": ""},
        "estimated_max_loss": {"low_pct": 10.0, "high_pct": 20.0, "basis": "backtest"},
        "key_risks": ["factor crowding", "regime change"],
    },
    {
        "candidate_id": "cand_002",
        "display_name": "Conservative Quality",
        "expected_return_band": {"low_pct": 4.0, "high_pct": 8.0, "basis": "backtest", "disclaimer": ""},
        "estimated_max_loss": {"low_pct": 5.0, "high_pct": 12.0, "basis": "backtest"},
        "key_risks": ["data quality"],
    },
]

_SAMPLE_EVIDENCE_PLANS = [
    {
        "candidate_id": "cand_001",
        "evidence_items": [
            {"category": "price", "description": "JPY equity prices"},
            {"category": "macro", "description": "FRED macro data"},
        ],
    },
]

_SAMPLE_USER_INTENT = {
    "success_definition": "10% per year",
    "user_goal_summary": "Momentum strategy with 10% target",
}


def test_build_approval_context_returns_correct_type():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert isinstance(ctx, ApprovalContext)


def test_build_approval_context_correct_candidate_id():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert ctx.candidate_id == "cand_001"


def test_build_approval_context_authority_disclosure_has_name():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert "Momentum Alpha" in ctx.authority_disclosure


def test_build_approval_context_4_stop_conditions():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert len(ctx.stop_condition_translations) == 4


def test_build_approval_context_risk_annotations_for_known_risks():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert len(ctx.risk_annotations) == 2
    originals = [ra.original_risk_text for ra in ctx.risk_annotations]
    assert "factor crowding" in originals
    assert "regime change" in originals


def test_build_approval_context_data_access_includes_fred():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert "FRED" in ctx.data_access_disclosure


def test_build_approval_context_kpi_alignment_uses_user_intent():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    assert ctx.kpi_alignment["aligned"] is True
    assert "10" in ctx.kpi_alignment["anchor"]


def test_build_approval_context_no_evidence_plan_fallback():
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_001",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=[],  # no evidence plan for this candidate
        user_intent=_SAMPLE_USER_INTENT,
    )
    # Should not raise — falls back to generic disclosure
    assert ctx.data_access_disclosure is not None


def test_build_approval_context_unknown_candidate_id_graceful():
    """Unknown candidate_id should return context with fallback display name."""
    ctx = build_approval_context(
        run_id="run_test",
        candidate_id="cand_unknown",
        candidate_cards=_SAMPLE_CARDS,
        evidence_plans=_SAMPLE_EVIDENCE_PLANS,
        user_intent=_SAMPLE_USER_INTENT,
    )
    # Should not raise — returns context using candidate_id as name fallback
    assert ctx.candidate_id == "cand_unknown"
    assert "cand_unknown" in ctx.authority_disclosure
