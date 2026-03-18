"""
Companion AI — Contradiction detector.

Implements CON-01 through CON-06 per spec §6.
Returns human-readable notices. Non-blocking — user may proceed.
"""

import re

# Patterns indicating a long-term goal
_LONG_TERM_SIGNALS = re.compile(
    r"\b(stable|long.?term|retirement|income|pension|dividend|steady)\b",
    re.IGNORECASE,
)

# Extract an annual return percentage from free text
_RETURN_PCT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:per\s*year|annually|annual|p\.?a\.?|a year)?",
    re.IGNORECASE,
)


def _extract_return_pct(text: str) -> float | None:
    """Extract the first numeric return percentage from text. Returns None if not found."""
    m = _RETURN_PCT_PATTERN.search(text)
    if m:
        return float(m.group(1))
    return None


def detect_contradictions(
    raw_goal: str,
    success_criteria: str | None,
    risk: str | None,
    time_horizon: str | None,
    must_not_do: list[str] | None,
) -> list[str]:
    """
    Run all contradiction rules against intake fields.

    Returns a list of human-readable notice strings.
    An empty list means no contradictions detected.
    """
    notices: list[str] = []
    goal_lower = (raw_goal or "").lower()
    sc_text = (success_criteria or "") + " " + (raw_goal or "")
    return_pct = _extract_return_pct(sc_text)
    must_not_do = must_not_do or []
    must_not_lower = [x.lower() for x in must_not_do]

    # CON-01: very_low risk AND return target > 8%
    if risk == "very_low" and return_pct is not None and return_pct > 8:
        notices.append(
            f"CON-01: You've indicated very low risk tolerance but a return target of "
            f"{return_pct:.0f}%. Most strategies that target {return_pct:.0f}% carry "
            f"drawdown risk above your stated limit. The system will search for candidates "
            f"that fit your risk constraint — but the candidates may have lower return "
            f"potential than your target. The system will proceed within your stated constraints."
        )

    # CON-02: very_low risk AND no exclusions AND goal mentions "returns"
    if (
        risk == "very_low"
        and not must_not_do
        and re.search(r"\b(returns?|profit|gain)\b", goal_lower)
    ):
        notices.append(
            "CON-02: You've indicated very low risk, but haven't listed any exclusions. "
            "Broad equity strategies with no exclusions typically carry more volatility "
            "than a very-low-risk tolerance implies. Consider adding exclusions "
            "(e.g., 'no leveraged positions', 'no small caps') or adjusting your risk "
            "tolerance. The system will proceed within your stated constraints."
        )

    # CON-03: fast time horizon AND goal contains long-term signals
    if time_horizon == "fast" and _LONG_TERM_SIGNALS.search(raw_goal):
        long_term_signal = _LONG_TERM_SIGNALS.search(raw_goal).group(0)
        notices.append(
            f"CON-03: Your goal mentions '{long_term_signal}' but your stated time horizon "
            f"is short-term. These are in tension. Long-term stability strategies require "
            f"longer evaluation periods. If the horizon is short, the system's validation "
            f"evidence will be limited. The system will proceed within your stated constraints."
        )

    # CON-04: fast time horizon AND very_low risk
    if time_horizon == "fast" and risk == "very_low":
        notices.append(
            "CON-04: Very-low-risk strategies with very short time horizons are difficult "
            "to validate. Validation requires enough history to observe meaningful drawdown "
            "events. A short time horizon limits what the system can confirm. "
            "The system will proceed within your stated constraints."
        )

    # CON-05: must_not_do contains something that appears positively in raw_goal
    for exclusion in must_not_lower:
        # Check if the exclusion keyword appears in goal text (indicating positive mention)
        # Use a short keyword extraction (first significant word of the exclusion)
        words = [w for w in exclusion.split() if len(w) > 3]
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", goal_lower):
                notices.append(
                    f"CON-05: Your goal mentions '{word}' favorably, but your exclusion list "
                    f"also includes '{exclusion}'. These conflict. Please clarify whether "
                    f"'{word}' should be included or excluded before we continue."
                )
                break

    # CON-06: return target > 20% AND low or very_low risk
    if (
        risk in ("low", "very_low")
        and return_pct is not None
        and return_pct > 20
    ):
        notices.append(
            f"CON-06: A return target of {return_pct:.0f}% annually is high. Strategies "
            f"at this return level have historically carried significant drawdown risk. "
            f"At '{risk}' risk tolerance, the system may not find candidates that can reach "
            f"this target without violating your stop conditions. "
            f"The system will proceed within your stated constraints."
        )

    return notices
