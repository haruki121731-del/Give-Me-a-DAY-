"""
Companion AI — Constraint inferrer.

Pattern-based inference of risk_preference, time_horizon_preference,
and success_definition from free-text answers.

No LLM. No session state.
"""

import re
from dataclasses import dataclass, field

# Maps success criteria answers to archetype labels (qualitative fallback)
_SUCCESS_ARCHETYPES = {
    "beat the market": "beat_market_index",
    "outperform": "beat_market_index",
    "index": "beat_market_index",
    "benchmark": "beat_market_index",
    "preserve": "capital_preservation",
    "protect": "capital_preservation",
    "don't lose": "capital_preservation",
    "no loss": "capital_preservation",
    "stable": "stable_income",
    "income": "stable_income",
    "dividend": "stable_income",
    "steady": "stable_income",
    "grow": "moderate_growth",
    "growth": "moderate_growth",
    "retirement": "long_term_growth",
    "long term": "long_term_growth",
    "double": "aggressive_growth",
    "triple": "aggressive_growth",
}

# Loss threshold extraction
_LOSS_PCT_PATTERN = re.compile(
    r"(?:lose|loss|losing|drop|down|fall|drawdown).*?(\d+(?:\.\d+)?)\s*%|"
    r"(\d+(?:\.\d+)?)\s*%.*?(?:lose|loss|losing|stop)",
    re.IGNORECASE,
)

# Plain number percentage (e.g. "lose up to 15%")
_PCT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%")


@dataclass
class InferenceResult:
    risk_preference: str | None = None
    time_horizon_preference: str | None = None
    success_definition: str | None = None
    kpi_anchor: str | None = None       # retained for KPI alignment at approval
    open_uncertainties: list[str] = field(default_factory=list)
    inferences_made: list[dict] = field(default_factory=list)


def infer_risk_preference(answer: str) -> tuple[str, bool]:
    """
    Infer risk_preference from Q-RISK answer text.
    Returns (inferred_value, is_confident).
    First match wins; order matches spec §5.3.
    """
    text = answer.lower().strip()

    # Extract explicit loss threshold percentage first
    pct_match = _PCT_PATTERN.search(text)
    threshold = float(pct_match.group(1)) if pct_match else None

    # Threshold-based inference (takes priority over keyword signals)
    if threshold is not None:
        if threshold < 8:
            return "very_low", True
        elif threshold < 18:
            return "low", True
        elif threshold < 35:
            return "medium", True
        else:
            return "high", True

    # Keyword signals
    if any(kw in text for kw in ["preserve", "don't lose", "protect", "safe", "lose nothing",
                                  "lose anything", "no loss", "very cautious", "first sign of trouble"]):
        return "very_low", True
    if any(kw in text for kw in ["small loss", "conservative", "not much risk",
                                  "cautious", "careful"]):
        return "low", True
    if any(kw in text for kw in ["some ups and downs", "moderate", "can handle",
                                  "market swings", "some risk"]):
        return "medium", True
    if any(kw in text for kw in ["aggressive", "high risk", "willing to lose a lot",
                                  "big risk", "high return"]):
        return "high", True

    return "medium", False  # default, not confident


def infer_time_horizon(answer: str) -> tuple[str, bool]:
    """
    Infer time_horizon_preference from Q-TIME answer text.
    Returns (inferred_value, is_confident).
    First match wins; order matches spec §5.3.
    """
    text = answer.lower().strip()

    # Check "30 days" / "month" before bare "days" to avoid misclassifying "30 days" as "fast"
    if any(kw in text for kw in ["1-2 months", "few weeks", "couple months"]):
        return "one_week", True  # spec: "few weeks, 1-2 months" → one_week
    if any(kw in text for kw in ["month", "30 days", "short term", "one month"]):
        return "one_month", True
    if any(kw in text for kw in ["days", "this week", "next week", "quick", "asap",
                                  "immediately"]):
        return "fast", True
    if any(kw in text for kw in ["6 months", "medium term", "half year", "1 year", "2 year",
                                  "one year", "two year"]):
        return "one_month", True  # spec: "6 months to 2 years" → one_month (closest)
    if any(kw in text for kw in ["years", "long term", "long-term", "3+", "5 years",
                                  "decade", "retirement", "10 years", "many years"]):
        return "quality_over_speed", True

    return "one_week", False  # default


def infer_success_definition(answer: str) -> tuple[str, bool]:
    """
    Extract or map success_definition from Q-SUCCESS answer.
    Returns (definition_text, is_numeric).
    """
    text = answer.strip()

    # If answer contains a numerical target, use verbatim (first 200 chars)
    if _PCT_PATTERN.search(text) or re.search(r"\d+", text):
        return text[:200], True

    # Qualitative mapping
    text_lower = text.lower()
    for kw, archetype in _SUCCESS_ARCHETYPES.items():
        if kw in text_lower:
            return archetype, False

    return text[:200] if text else "not_specified", False


def apply_answers(
    answers: dict[str, str],
    existing_risk: str | None = None,
    existing_time_horizon: str | None = None,
    existing_success_criteria: str | None = None,
) -> InferenceResult:
    """
    Apply all inference rules to a dict of question answers.
    Returns InferenceResult with inferred fields and traceability.
    """
    result = InferenceResult()

    # Risk preference
    if "Q-RISK" in answers:
        inferred, confident = infer_risk_preference(answers["Q-RISK"])
        result.risk_preference = inferred
        if confident:
            result.inferences_made.append({
                "field": "risk_preference",
                "from_text": answers["Q-RISK"][:100],
                "inferred_value": inferred,
            })
        else:
            result.risk_preference = existing_risk or "medium"
            result.open_uncertainties.append(
                f"risk_preference inferred as default 'medium' from answer: '{answers['Q-RISK'][:60]}'"
            )
    elif existing_risk:
        result.risk_preference = existing_risk

    # Time horizon
    if "Q-TIME" in answers:
        inferred, confident = infer_time_horizon(answers["Q-TIME"])
        result.time_horizon_preference = inferred
        if confident:
            result.inferences_made.append({
                "field": "time_horizon_preference",
                "from_text": answers["Q-TIME"][:100],
                "inferred_value": inferred,
            })
        else:
            result.time_horizon_preference = existing_time_horizon or "one_week"
            result.open_uncertainties.append(
                f"time_horizon_preference inferred as default 'one_week' from answer: "
                f"'{answers['Q-TIME'][:60]}'"
            )
    elif existing_time_horizon:
        result.time_horizon_preference = existing_time_horizon

    # Success definition
    if "Q-SUCCESS" in answers:
        definition, is_numeric = infer_success_definition(answers["Q-SUCCESS"])
        result.success_definition = definition
        result.kpi_anchor = definition
        if not is_numeric:
            result.open_uncertainties.append(
                f"success_definition inferred from qualitative answer: "
                f"'{answers['Q-SUCCESS'][:60]}' → '{definition}'"
            )
        result.inferences_made.append({
            "field": "success_definition",
            "from_text": answers["Q-SUCCESS"][:100],
            "inferred_value": definition,
        })
    elif existing_success_criteria:
        result.success_definition = existing_success_criteria
        result.kpi_anchor = existing_success_criteria

    return result
