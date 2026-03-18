"""
Tests for companion/contradiction_detector.py

Covers CON-01 through CON-06 detection and non-detection cases.
"""

import pytest
from src.companion.contradiction_detector import detect_contradictions


def _con_ids(notices: list[str]) -> set[str]:
    """Extract CON-XX IDs from notice texts."""
    return {n[:6] for n in notices if n.startswith("CON-")}


# ── CON-01: very_low risk AND return target > 8% ─────────────────────────────

def test_con01_fires_very_low_risk_high_return():
    notices = detect_contradictions(
        raw_goal="I want to achieve 15% annual return with low risk",
        success_criteria="15% per year",
        risk="very_low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-01" in ids


def test_con01_does_not_fire_for_low_return():
    notices = detect_contradictions(
        raw_goal="I want to achieve 5% return",
        success_criteria="5% per year",
        risk="very_low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-01" not in ids


def test_con01_does_not_fire_for_medium_risk():
    notices = detect_contradictions(
        raw_goal="I want 15% return",
        success_criteria="15% per year",
        risk="medium",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-01" not in ids


# ── CON-02: very_low risk, no exclusions, goal mentions returns ───────────────

def test_con02_fires_very_low_risk_no_exclusions_returns_mentioned():
    notices = detect_contradictions(
        raw_goal="I want good returns from equities",
        success_criteria=None,
        risk="very_low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-02" in ids


def test_con02_does_not_fire_when_exclusions_present():
    notices = detect_contradictions(
        raw_goal="I want good returns",
        success_criteria=None,
        risk="very_low",
        time_horizon="one_month",
        must_not_do=["no leveraged positions"],
    )
    ids = _con_ids(notices)
    assert "CON-02" not in ids


def test_con02_does_not_fire_for_medium_risk():
    notices = detect_contradictions(
        raw_goal="I want good returns",
        success_criteria=None,
        risk="medium",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-02" not in ids


# ── CON-03: fast horizon AND long-term signals in goal ────────────────────────

def test_con03_fires_fast_horizon_long_term_goal():
    notices = detect_contradictions(
        raw_goal="I want a stable long-term income strategy",
        success_criteria=None,
        risk="medium",
        time_horizon="fast",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-03" in ids


def test_con03_fires_fast_horizon_retirement_goal():
    notices = detect_contradictions(
        raw_goal="I want to build a retirement fund",
        success_criteria=None,
        risk="low",
        time_horizon="fast",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-03" in ids


def test_con03_does_not_fire_for_non_fast_horizon():
    notices = detect_contradictions(
        raw_goal="I want a stable long-term strategy",
        success_criteria=None,
        risk="medium",
        time_horizon="quality_over_speed",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-03" not in ids


# ── CON-04: fast horizon AND very_low risk ────────────────────────────────────

def test_con04_fires_fast_and_very_low():
    notices = detect_contradictions(
        raw_goal="I want quick returns with minimal risk",
        success_criteria="5%",
        risk="very_low",
        time_horizon="fast",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-04" in ids


def test_con04_does_not_fire_for_medium_risk():
    notices = detect_contradictions(
        raw_goal="I want quick returns",
        success_criteria="5%",
        risk="medium",
        time_horizon="fast",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-04" not in ids


# ── CON-05: must_not_do conflicts with raw_goal ───────────────────────────────

def test_con05_fires_when_exclusion_word_appears_in_goal():
    notices = detect_contradictions(
        raw_goal="I want to use leverage to amplify returns",
        success_criteria="20%",
        risk="high",
        time_horizon="one_month",
        must_not_do=["no leverage"],
    )
    ids = _con_ids(notices)
    assert "CON-05" in ids


def test_con05_does_not_fire_when_no_conflict():
    notices = detect_contradictions(
        raw_goal="I want momentum returns from Japanese equities",
        success_criteria="10%",
        risk="medium",
        time_horizon="one_month",
        must_not_do=["no leveraged positions"],
    )
    ids = _con_ids(notices)
    assert "CON-05" not in ids


# ── CON-06: return > 20% AND low/very_low risk ────────────────────────────────

def test_con06_fires_high_return_low_risk():
    notices = detect_contradictions(
        raw_goal="I want 30% annual return",
        success_criteria="30% per year",
        risk="low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-06" in ids


def test_con06_fires_high_return_very_low_risk():
    notices = detect_contradictions(
        raw_goal="I want 25% annual return",
        success_criteria="25% per year",
        risk="very_low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-06" in ids


def test_con06_does_not_fire_for_medium_risk():
    notices = detect_contradictions(
        raw_goal="I want 30% annual return",
        success_criteria="30% per year",
        risk="medium",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-06" not in ids


def test_con06_does_not_fire_for_moderate_target():
    notices = detect_contradictions(
        raw_goal="I want 12% annual return",
        success_criteria="12% per year",
        risk="low",
        time_horizon="one_month",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    assert "CON-06" not in ids


# ── No contradictions for clean goal ─────────────────────────────────────────

def test_no_contradictions_for_well_formed_goal():
    notices = detect_contradictions(
        raw_goal="I want a momentum strategy on Japanese equities targeting 10% annual return",
        success_criteria="10% per year",
        risk="medium",
        time_horizon="one_month",
        must_not_do=["no leveraged positions"],
    )
    assert notices == []


# ── Multiple contradictions can fire together ─────────────────────────────────

def test_multiple_contradictions_fire_together():
    notices = detect_contradictions(
        raw_goal="I want very stable retirement income",
        success_criteria="10% per year",
        risk="very_low",
        time_horizon="fast",
        must_not_do=[],
    )
    ids = _con_ids(notices)
    # CON-01: very_low + 10% > 8%
    # CON-02: very_low + no exclusions + returns mentioned (not in this goal text directly)
    # CON-03: fast + "stable" or "retirement"
    # CON-04: fast + very_low
    assert "CON-01" in ids
    assert "CON-03" in ids
    assert "CON-04" in ids
    assert len(notices) >= 3
