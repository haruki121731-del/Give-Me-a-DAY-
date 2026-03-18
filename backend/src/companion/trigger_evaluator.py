"""
Companion AI — Goal Intake trigger evaluator.

Evaluates T1–T7 triggers against a CreateRunRequest.
Returns a list of fired trigger IDs and metadata.

All logic is pattern-based. No LLM.
"""

import re
from dataclasses import dataclass, field

# Out-of-scope keyword patterns (T7) with their redirect text
_OUT_OF_SCOPE_PATTERNS: list[tuple[str, str, str]] = [
    # (regex_pattern, display_name, redirect_text)
    (r"\b(bitcoin|ethereum|crypto|cryptocurrency|web3|nft|defi)\b",
     "crypto assets",
     "Japanese or US equities"),
    (r"\b(forex|foreign exchange|currency pair|fx trading|usd/jpy|eur/usd|gbp/usd)\b",
     "FX trading",
     "macro equity strategy"),
    (r"\b(2x|3x|leveraged etf|leveraged fund|margin trading|margin account)\b",
     "leveraged products",
     "equity strategy without leverage"),
    (r"\b(options|call options?|put options?|futures|derivatives|warrants)\b",
     "options/derivatives",
     "equity strategy"),
    (r"\b(property investment|real estate direct|direct real estate|physical property)\b",
     "direct real estate",
     "equity REIT exposure"),
    (r"\b(penny stocks?|micro.?cap stocks?|illiquid stocks?)\b",
     "penny/micro-cap stocks",
     "small-cap strategy"),
]

# Patterns that suggest a measurable outcome is present (T2 check)
_MEASURABLE_OUTCOME_PATTERN = re.compile(
    r"(\d+\s*%|\d+\s*percent|beat\s+the\s+market|outperform|index|benchmark|"
    r"double|triple|return|yield|profit|gain|loss|drawdown)",
    re.IGNORECASE,
)

# Long-term signals for CON-03 / T5 context
LONG_TERM_SIGNALS = ["stable", "long-term", "long term", "retirement", "income", "pension"]


@dataclass
class TriggerResult:
    fired: list[str] = field(default_factory=list)          # fired trigger IDs
    out_of_scope_terms: list[tuple[str, str]] = field(default_factory=list)  # (term, redirect)
    has_measurable_outcome: bool = False


def evaluate_triggers(
    goal: str,
    success_criteria: str | None,
    risk: str | None,
    time_horizon: str | None,
) -> TriggerResult:
    """
    Evaluate T1–T7 against intake fields.

    Returns TriggerResult with fired trigger IDs and metadata.
    Priority order for question limiting: T6 > T7 > T3 > T4 > T5 > T1/T2.
    """
    result = TriggerResult()
    goal_lower = goal.lower().strip()

    # T2: No measurable outcome
    has_measurable = bool(_MEASURABLE_OUTCOME_PATTERN.search(goal))
    result.has_measurable_outcome = has_measurable
    if not has_measurable:
        result.fired.append("T2")

    # T3: Success criteria missing AND T2 fired
    if (not success_criteria or not success_criteria.strip()) and "T2" in result.fired:
        result.fired.append("T3")

    # T1: Goal too short — only trigger if T2 or T3 also fired (incomplete short goal)
    if len(goal.strip()) < 40 and ("T2" in result.fired or "T3" in result.fired):
        result.fired.append("T1")

    # T4: Risk preference not provided
    if risk is None or risk.strip() == "":
        result.fired.append("T4")

    # T5: Time horizon not provided
    if time_horizon is None or time_horizon.strip() == "":
        result.fired.append("T5")

    # T7: Out-of-scope signal in goal text
    for pattern, display_name, redirect in _OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, goal_lower):
            result.out_of_scope_terms.append((display_name, redirect))

    if result.out_of_scope_terms:
        result.fired.append("T7")

    # T6 is evaluated by contradiction_detector — placeholder here
    # The contradiction_detector adds "T6" to fired list separately when called

    return result


def needs_clarification(trigger_result: TriggerResult, contradiction_notices: list[str]) -> bool:
    """
    Returns True if any trigger fired or contradictions were found.
    T6 (contradiction) is surfaced as a notice regardless.
    """
    if contradiction_notices:
        return True
    # T7 shows a redirect notice — counts as needing clarification
    question_triggers = {"T1", "T2", "T3", "T4", "T5", "T7"}
    return bool(set(trigger_result.fired) & question_triggers)
