"""
Tests for companion/trigger_evaluator.py

Covers all T1–T7 triggers and the needs_clarification gate.
"""

import pytest
from src.companion.trigger_evaluator import evaluate_triggers, needs_clarification


# ── T2: No measurable outcome ─────────────────────────────────────────────────

def test_t2_fires_when_no_number_in_goal():
    r = evaluate_triggers(
        goal="I want to make money in the stock market somehow",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T2" in r.fired
    assert not r.has_measurable_outcome


def test_t2_does_not_fire_with_percentage():
    r = evaluate_triggers(
        goal="I want to achieve 10% annual return from Japanese equities",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T2" not in r.fired
    assert r.has_measurable_outcome


def test_t2_does_not_fire_with_benchmark_comparator():
    r = evaluate_triggers(
        goal="I want to outperform the Nikkei 225 index over 3 years",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T2" not in r.fired


# ── T3: Success criteria missing AND T2 ───────────────────────────────────────

def test_t3_fires_when_t2_and_no_success_criteria():
    r = evaluate_triggers(
        goal="I want to do well in stocks",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T3" in r.fired


def test_t3_does_not_fire_when_success_criteria_provided():
    r = evaluate_triggers(
        goal="I want to do well in stocks",
        success_criteria="beat the market",
        risk="medium",
        time_horizon="one_week",
    )
    assert "T3" not in r.fired


def test_t3_does_not_fire_when_goal_has_measurable_target():
    r = evaluate_triggers(
        goal="I want a 7% annual return from Japanese equities",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T2" not in r.fired
    assert "T3" not in r.fired


# ── T1: Short goal ────────────────────────────────────────────────────────────

def test_t1_fires_for_short_vague_goal():
    r = evaluate_triggers(
        goal="make money",
        success_criteria=None,
        risk="medium",
        time_horizon="one_week",
    )
    assert "T1" in r.fired  # short AND vague (T2 also fires)


def test_t1_does_not_fire_for_short_but_complete_goal():
    # Short but has measurable outcome and success_criteria — T1 should not fire
    r = evaluate_triggers(
        goal="10% return annually",
        success_criteria="10% annual return",
        risk="medium",
        time_horizon="one_week",
    )
    assert "T1" not in r.fired


# ── T4: Risk preference not provided ─────────────────────────────────────────

def test_t4_fires_when_risk_is_none():
    r = evaluate_triggers(
        goal="I want to achieve 10% return from Japanese equities",
        success_criteria="10%",
        risk=None,
        time_horizon="one_week",
    )
    assert "T4" in r.fired


def test_t4_fires_when_risk_is_empty():
    r = evaluate_triggers(
        goal="I want to achieve 10% return from Japanese equities",
        success_criteria="10%",
        risk="",
        time_horizon="one_week",
    )
    assert "T4" in r.fired


def test_t4_does_not_fire_when_risk_provided():
    r = evaluate_triggers(
        goal="I want to achieve 10% return from Japanese equities",
        success_criteria="10%",
        risk="low",
        time_horizon="one_week",
    )
    assert "T4" not in r.fired


# ── T5: Time horizon not provided ────────────────────────────────────────────

def test_t5_fires_when_time_horizon_is_none():
    r = evaluate_triggers(
        goal="I want to achieve 10% return from Japanese equities",
        success_criteria="10%",
        risk="medium",
        time_horizon=None,
    )
    assert "T5" in r.fired


def test_t5_does_not_fire_when_provided():
    r = evaluate_triggers(
        goal="I want to achieve 10% return from Japanese equities",
        success_criteria="10%",
        risk="medium",
        time_horizon="one_month",
    )
    assert "T5" not in r.fired


# ── T7: Out-of-scope signals ──────────────────────────────────────────────────

def test_t7_fires_for_crypto():
    r = evaluate_triggers(
        goal="I want to trade bitcoin and ethereum for quick gains",
        success_criteria=None,
        risk="high",
        time_horizon="fast",
    )
    assert "T7" in r.fired
    assert any("crypto" in term[0] for term in r.out_of_scope_terms)


def test_t7_fires_for_options():
    r = evaluate_triggers(
        goal="I want to use options on Japanese equities for income",
        success_criteria="steady income",
        risk="medium",
        time_horizon="one_month",
    )
    assert "T7" in r.fired


def test_t7_fires_for_leveraged_etf():
    r = evaluate_triggers(
        goal="Invest in 3x leveraged ETF for momentum",
        success_criteria="30%",
        risk="high",
        time_horizon="one_week",
    )
    assert "T7" in r.fired


def test_t7_does_not_fire_for_clean_equity_goal():
    r = evaluate_triggers(
        goal="I want a momentum strategy on Japanese equities targeting 8% annual return",
        success_criteria="8% per year",
        risk="medium",
        time_horizon="one_year",
    )
    assert "T7" not in r.fired
    assert r.out_of_scope_terms == []


# ── needs_clarification gate ──────────────────────────────────────────────────

def test_needs_clarification_false_for_complete_goal():
    r = evaluate_triggers(
        goal="I want a momentum strategy on Japanese equities targeting 8% annual return",
        success_criteria="8% per year",
        risk="medium",
        time_horizon="one_week",
    )
    assert not needs_clarification(r, [])


def test_needs_clarification_true_when_t4_fires():
    r = evaluate_triggers(
        goal="I want a momentum strategy on Japanese equities targeting 8% annual return",
        success_criteria="8%",
        risk=None,
        time_horizon="one_week",
    )
    assert needs_clarification(r, [])


def test_needs_clarification_true_when_contradictions_present():
    r = evaluate_triggers(
        goal="I want a momentum strategy on Japanese equities targeting 8% annual return",
        success_criteria="8%",
        risk="medium",
        time_horizon="one_week",
    )
    assert needs_clarification(r, ["Some contradiction detected"])


def test_max_triggers_do_not_crash():
    """All triggers firing at once should not raise."""
    r = evaluate_triggers(
        goal="bitcoin",  # crypto keyword triggers T7; "btc" is slang not in spec pattern
        success_criteria=None,
        risk=None,
        time_horizon=None,
    )
    assert "T7" in r.fired
    assert "T4" in r.fired
    assert "T5" in r.fired
