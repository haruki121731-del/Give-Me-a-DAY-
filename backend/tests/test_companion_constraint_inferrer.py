"""
Tests for companion/constraint_inferrer.py

Covers all inference pathways: risk_preference, time_horizon_preference,
success_definition extraction, and the apply_answers integration.
"""

import pytest
from src.companion.constraint_inferrer import (
    apply_answers,
    infer_risk_preference,
    infer_success_definition,
    infer_time_horizon,
)


# ── infer_risk_preference ─────────────────────────────────────────────────────

class TestInferRiskPreference:

    def test_very_low_from_preserve_keyword(self):
        risk, confident = infer_risk_preference("I want to preserve my capital above all")
        assert risk == "very_low"
        assert confident

    def test_very_low_from_lose_nothing(self):
        risk, confident = infer_risk_preference("I don't want to lose anything")
        assert risk == "very_low"
        assert confident

    def test_very_low_from_small_threshold(self):
        risk, confident = infer_risk_preference("Stop if I've lost 5%")
        assert risk == "very_low"
        assert confident

    def test_low_from_conservative_keyword(self):
        risk, confident = infer_risk_preference("I'm fairly conservative with money")
        assert risk == "low"
        assert confident

    def test_low_from_threshold_12pct(self):
        risk, confident = infer_risk_preference("I can handle up to 12% loss")
        assert risk == "low"
        assert confident

    def test_medium_from_moderate_keyword(self):
        risk, confident = infer_risk_preference("I'm comfortable with moderate market swings")
        assert risk == "medium"
        assert confident

    def test_medium_from_threshold_25pct(self):
        risk, confident = infer_risk_preference("I can handle losing 25% if the upside is there")
        assert risk == "medium"
        assert confident

    def test_high_from_aggressive_keyword(self):
        risk, confident = infer_risk_preference("I'm aggressive and willing to lose a lot for gains")
        assert risk == "high"
        assert confident

    def test_high_from_threshold_40pct(self):
        risk, confident = infer_risk_preference("Stop at 40% loss maximum")
        assert risk == "high"
        assert confident

    def test_default_medium_no_signal(self):
        risk, confident = infer_risk_preference("I don't know really")
        assert risk == "medium"
        assert not confident

    def test_threshold_extraction_takes_priority(self):
        """An explicit percentage overrides surrounding qualitative language."""
        risk, confident = infer_risk_preference("I'm aggressive but stop at 3%")
        assert risk == "very_low"  # 3% < 8%
        assert confident


# ── infer_time_horizon ────────────────────────────────────────────────────────

class TestInferTimeHorizon:

    def test_fast_from_days(self):
        horizon, confident = infer_time_horizon("I want results in a few days")
        assert horizon == "fast"
        assert confident

    def test_fast_from_this_week(self):
        horizon, confident = infer_time_horizon("I'm thinking about this week")
        assert horizon == "fast"
        assert confident

    def test_one_week_from_few_weeks(self):
        horizon, confident = infer_time_horizon("Maybe 1-2 months or a few weeks")
        assert horizon == "one_week"
        assert confident

    def test_one_month_from_month(self):
        horizon, confident = infer_time_horizon("I'm thinking about a 30 days timeframe")
        assert horizon == "one_month"
        assert confident

    def test_one_month_from_6_months(self):
        horizon, confident = infer_time_horizon("I'm thinking about 6 months to 2 years")
        assert horizon == "one_month"
        assert confident

    def test_quality_over_speed_from_long_term(self):
        horizon, confident = infer_time_horizon("This is long-term, probably 5 years or more")
        assert horizon == "quality_over_speed"
        assert confident

    def test_quality_over_speed_from_retirement(self):
        horizon, confident = infer_time_horizon("I'm building a retirement fund")
        assert horizon == "quality_over_speed"
        assert confident

    def test_default_one_week_no_signal(self):
        horizon, confident = infer_time_horizon("I'm not sure about the timeframe")
        assert horizon == "one_week"
        assert not confident


# ── infer_success_definition ──────────────────────────────────────────────────

class TestInferSuccessDefinition:

    def test_numeric_answer_returned_verbatim(self):
        definition, is_numeric = infer_success_definition("I want 8% per year from stocks")
        assert is_numeric
        assert "8" in definition

    def test_numeric_answer_capped_at_200_chars(self):
        long_answer = "a" * 250 + " 10%"
        definition, is_numeric = infer_success_definition(long_answer)
        assert len(definition) <= 200

    def test_qualitative_beat_market_maps(self):
        definition, is_numeric = infer_success_definition("I want to beat the market")
        assert not is_numeric
        assert definition == "beat_market_index"

    def test_qualitative_preserve_maps(self):
        definition, is_numeric = infer_success_definition("Preserve my savings")
        assert not is_numeric
        assert definition == "capital_preservation"

    def test_qualitative_retirement_maps(self):
        definition, is_numeric = infer_success_definition("Build a retirement fund")
        assert not is_numeric
        assert definition == "long_term_growth"

    def test_empty_answer_returns_not_specified(self):
        definition, is_numeric = infer_success_definition("")
        assert definition == "not_specified"
        assert not is_numeric


# ── apply_answers integration ─────────────────────────────────────────────────

class TestApplyAnswers:

    def test_applies_risk_answer(self):
        result = apply_answers({"Q-RISK": "I can handle up to 15% loss"})
        assert result.risk_preference == "low"
        assert any(i["field"] == "risk_preference" for i in result.inferences_made)

    def test_applies_time_answer(self):
        result = apply_answers({"Q-TIME": "I'm thinking long-term, 5+ years"})
        assert result.time_horizon_preference == "quality_over_speed"

    def test_applies_success_answer(self):
        result = apply_answers({"Q-SUCCESS": "I want 10% annual return"})
        assert result.success_definition is not None
        assert result.kpi_anchor is not None

    def test_falls_back_to_existing_risk_when_no_answer(self):
        result = apply_answers({}, existing_risk="low")
        assert result.risk_preference == "low"

    def test_falls_back_to_existing_time_when_no_answer(self):
        result = apply_answers({}, existing_time_horizon="one_month")
        assert result.time_horizon_preference == "one_month"

    def test_open_uncertainty_added_for_unconfident_risk(self):
        result = apply_answers({"Q-RISK": "I really don't know"})
        assert any("risk_preference" in u for u in result.open_uncertainties)

    def test_open_uncertainty_added_for_unconfident_time(self):
        result = apply_answers({"Q-TIME": "who knows"})
        assert any("time_horizon" in u for u in result.open_uncertainties)

    def test_open_uncertainty_added_for_qualitative_success(self):
        result = apply_answers({"Q-SUCCESS": "beat the market"})
        assert any("success_definition" in u for u in result.open_uncertainties)

    def test_all_three_answers_combined(self):
        result = apply_answers({
            "Q-RISK": "stop at 20% loss",
            "Q-TIME": "about 1 year from now",  # "1 year" matches one_month (spec: 6mo-2yr)
            "Q-SUCCESS": "12% per year",
        })
        assert result.risk_preference == "medium"  # 20% → medium (18-35%)
        assert result.time_horizon_preference == "one_month"  # "1 year" → one_month
        assert result.success_definition is not None
        assert result.kpi_anchor is not None
        assert len(result.inferences_made) == 3
