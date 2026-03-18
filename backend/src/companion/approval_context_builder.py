"""
Companion AI — Approval context builder.

Generates ApprovalContext from pipeline artifacts for the given run + candidate.
Called by GET /api/v1/runs/{run_id}/approval-context.

Reads: candidate_cards, evidence_plans, user_intent from pipeline store.
Writes: nothing (read-only to pipeline data).
Does not modify recommendation, approval, or Paper Run logic.
"""

import re
from datetime import datetime, timedelta
from typing import Any

from .models import (
    ApprovalContext,
    ComprehensionCheck,
    RiskAnnotation,
    StopConditionTranslation,
)

# ── Risk annotation template library (spec §7.4) ──────────────────────────────

_RISK_TEMPLATES: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"crowding|factor crowding", re.IGNORECASE),
        "When many strategies use the same signals, they can all sell at the same time. "
        "During market stress, this can cause larger losses than the backtest predicted.",
    ),
    (
        re.compile(r"regime change|regime shift|regime", re.IGNORECASE),
        "This strategy works better in certain market environments than others. "
        "If the market changes character — for example, from a rising to a falling market — "
        "the strategy may underperform until conditions return.",
    ),
    (
        re.compile(r"overfitting|curve.?fitting", re.IGNORECASE),
        "There is a risk that this strategy looks good in historical data partly because "
        "it was fitted to that data. Out-of-sample performance may be weaker than the "
        "backtest suggests.",
    ),
    (
        re.compile(r"data quality|data availability", re.IGNORECASE),
        "This strategy depends on data quality. If the data source changes, goes offline, "
        "or provides errors, the strategy's signals may degrade. The system monitors for "
        "this (SC-04).",
    ),
    (
        re.compile(r"cost assumption|transaction cost", re.IGNORECASE),
        "The backtest assumes specific transaction costs (10bps commission + 10bps spread). "
        "Real costs may be higher, especially during volatile periods. "
        "Higher costs reduce net returns.",
    ),
    (
        re.compile(r"liquidity", re.IGNORECASE),
        "This strategy may trade stocks that are difficult to buy or sell in large quantities. "
        "In a real execution context, the actual prices achieved may differ from those "
        "assumed in the backtest.",
    ),
    (
        re.compile(r"short selling|short position|short exposure", re.IGNORECASE),
        "If this strategy takes short positions, losses on the short leg are theoretically "
        "unlimited. The Paper Run simulates this but real short exposure should be reviewed "
        "carefully before live execution.",
    ),
]

_NO_ANNOTATION = "No additional plain-language annotation available."


def _annotate_risk(risk_text: str) -> RiskAnnotation:
    for pattern, annotation in _RISK_TEMPLATES:
        if pattern.search(risk_text):
            return RiskAnnotation(original_risk_text=risk_text, annotation=annotation)
    return RiskAnnotation(
        original_risk_text=risk_text,
        annotation=f"{risk_text} — {_NO_ANNOTATION}",
    )


# ── Stop condition translations (spec §7.3) ───────────────────────────────────

def _build_stop_translations(virtual_capital: float) -> list[StopConditionTranslation]:
    stop_value = virtual_capital * 0.80
    re_eval_date = (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")

    return [
        StopConditionTranslation(
            id="SC-01",
            virtual_capital_amount=virtual_capital,
            plain_language=(
                f"**SC-01 — Automatic stop if the portfolio loses 20% of its starting value.**\n\n"
                f"With ¥{virtual_capital:,.0f} virtual capital, this would trigger if the "
                f"simulated value fell to ¥{stop_value:,.0f}. At that point, the system stops "
                f"all simulated trading and notifies you. You would need to review the situation "
                f"and re-approve to continue.\n\n"
                f"This is the most likely condition to trigger. It fires automatically — "
                f"you do not need to monitor it."
            ),
        ),
        StopConditionTranslation(
            id="SC-02",
            plain_language=(
                "**SC-02 — Automatic stop if the strategy underperforms the market for "
                "3 months in a row.**\n\n"
                "'Underperform' means the strategy's return is lower than the benchmark "
                "index for three consecutive calendar months — even if the strategy is not "
                "losing money in absolute terms. This condition detects strategies that are "
                "working worse than simply holding an index fund."
            ),
        ),
        StopConditionTranslation(
            id="SC-03",
            plain_language=(
                "**SC-03 — Automatic pause if the strategy generates an unusual signal.**\n\n"
                "If the strategy's daily signal deviates more than 3 standard deviations "
                "from its historical pattern, the system pauses and notifies you rather than "
                "acting on what may be a data error or model breakdown. You can review and resume."
            ),
        ),
        StopConditionTranslation(
            id="SC-04",
            plain_language=(
                "**SC-04 — Automatic pause if data quality fails for 3 consecutive trading days.**\n\n"
                "If the system cannot obtain reliable market data for 3 days in a row — for "
                "example, because the data source is unavailable or corrupted — it pauses "
                "rather than operating on bad data. You will be notified."
            ),
        ),
    ]


_STOP_CONDITIONS_FOOTER = (
    "These four conditions are set by the system. You cannot change the thresholds in v1. "
    "They exist to protect you from the strategy running in circumstances where it should not run. "
    "All four conditions fire automatically. None require you to monitor the system."
)


# ── Authority disclosure (spec §5.4) ─────────────────────────────────────────

def _build_authority_disclosure(
    candidate_name: str,
    virtual_capital: float,
    re_eval_days: int = 90,
) -> str:
    re_eval_date = (datetime.utcnow() + timedelta(days=re_eval_days)).strftime("%B %d, %Y")
    return (
        f"By approving {candidate_name}, you authorize this system to:\n\n"
        f"1. Access daily market data from Yahoo Finance and FRED on your behalf, "
        f"every trading day, until the strategy is stopped or re-evaluated.\n\n"
        f"2. Simulate running this strategy daily in a virtual portfolio, starting "
        f"with ¥{virtual_capital:,.0f}. No real money is used.\n\n"
        f"3. Automatically stop the simulation if any of the four stop conditions "
        f"are triggered (detailed below). You will be notified when this happens.\n\n"
        f"4. Send you a performance summary every month.\n\n"
        f"5. Re-evaluate this strategy automatically after {re_eval_date}. "
        f"If conditions have changed significantly, you will be asked to re-approve.\n\n"
        f"You can stop the simulation at any time from the status page."
    )


# ── KPI alignment check (spec §7.2) ──────────────────────────────────────────

def _extract_return_pct(text: str) -> float | None:
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:per\s*year|annually|annual|p\.?a\.?|a year)?",
        text,
        re.IGNORECASE,
    )
    return float(m.group(1)) if m else None


def _build_kpi_alignment(
    kpi_anchor: str | None,
    return_band_low: float,
    return_band_high: float,
) -> dict:
    candidate_band_str = f"{return_band_low:.1f}%–{return_band_high:.1f}% per year"

    if not kpi_anchor:
        return {
            "aligned": True,
            "anchor": "No specific return target stated.",
            "candidate_band": candidate_band_str,
            "note": f"This candidate targets {candidate_band_str}, after simulated costs.",
        }

    target_pct = _extract_return_pct(kpi_anchor)

    if target_pct is None:
        # Qualitative anchor
        return {
            "aligned": True,
            "anchor": kpi_anchor,
            "candidate_band": candidate_band_str,
            "note": (
                f"Your goal was: {kpi_anchor}. "
                f"This candidate targets {candidate_band_str}, after simulated costs."
            ),
        }

    # Numerical target — check alignment
    if target_pct > return_band_high * 1.5:
        return {
            "aligned": False,
            "anchor": f"{target_pct:.0f}% per year",
            "candidate_band": candidate_band_str,
            "note": (
                f"Your stated target of {target_pct:.0f}% per year is significantly above "
                f"this candidate's return range of {candidate_band_str}. The system will "
                f"run validation, but this candidate may not reach your target."
            ),
        }
    elif target_pct < return_band_low * 0.5 and return_band_low > 0:
        return {
            "aligned": True,
            "anchor": f"{target_pct:.0f}% per year",
            "candidate_band": candidate_band_str,
            "note": (
                f"This candidate's return range ({candidate_band_str}) is above your "
                f"stated target of {target_pct:.0f}% per year. That is generally a good "
                f"sign — the candidate may deliver more than you need."
            ),
        }
    else:
        return {
            "aligned": True,
            "anchor": f"{target_pct:.0f}% per year",
            "candidate_band": candidate_band_str,
            "note": (
                f"This candidate's return range ({candidate_band_str}) aligns with "
                f"your stated target of {target_pct:.0f}% per year."
            ),
        }


# ── Data access disclosure (spec §7.5) ───────────────────────────────────────

def _build_data_access_disclosure(evidence_items: list[dict]) -> str:
    sources: list[str] = []

    # Count price items
    price_items = [e for e in evidence_items if e.get("category") == "price"]
    if price_items:
        n = len(price_items)
        sources.append(
            f"- Daily stock price data from Yahoo Finance (public source) "
            f"for {n} {'security' if n == 1 else 'securities'}"
        )

    # Macro data
    macro_items = [e for e in evidence_items if e.get("category") == "macro"]
    if macro_items:
        sources.append(
            "- Macro economic data from FRED (US Federal Reserve public data)"
        )

    # Flow data (COT)
    flow_items = [e for e in evidence_items if e.get("category") == "flow"]
    if flow_items:
        sources.append(
            "- Commitments of Traders data from CFTC (US public data)"
        )

    if not sources:
        sources.append("- Daily market data from public sources")

    source_block = "\n".join(sources)
    return (
        f"**What data this strategy uses:**\n\n"
        f"{source_block}\n\n"
        f"All data sources are public and free. No private data or paid subscriptions "
        f"are used. The system accesses these sources every trading day during the Paper Run.\n\n"
        f"If a data source is temporarily unavailable, the system pauses (SC-04) rather "
        f"than operating on incomplete information."
    )


# ── Paper Run explanation (spec §7.6) ────────────────────────────────────────

def _build_paper_run_explanation(virtual_capital: float) -> str:
    return (
        f"**What 'Paper Run' means:**\n\n"
        f"The system will simulate this strategy every trading day using real market data — "
        f"but no real money is used, and no real trades are placed. It starts with a virtual "
        f"portfolio of ¥{virtual_capital:,.0f} (or your adjusted amount). "
        f"All profits and losses are simulated.\n\n"
        f"The purpose of a Paper Run is to observe whether the strategy behaves in live "
        f"market conditions the way the backtests predicted. A strategy that works well "
        f"in historical data sometimes behaves differently when run day-by-day with real data.\n\n"
        f"Paper Run results do not guarantee that real-money execution would produce the "
        f"same outcomes. They are a real-time validation check — not a trading system.\n\n"
        f"In v1, the system only runs Paper Runs. Real-money execution is not available."
    )


# ── Comprehension check (spec §7.7) ──────────────────────────────────────────

def _build_comprehension_check(virtual_capital: float) -> ComprehensionCheck:
    stop_value = virtual_capital * 0.80
    portfolio_value = virtual_capital * 0.79  # below threshold for the question
    return ComprehensionCheck(
        question=(
            f"**Quick check — select the correct answer:**\n\n"
            f"You approved a Paper Run starting with ¥{virtual_capital:,.0f}. "
            f"Six months later, the simulated portfolio is worth ¥{portfolio_value:,.0f}.\n\n"
            f"What does the system do?"
        ),
        options=[
            "A) Continues running — the loss is within my stated tolerance",
            f"B) Stops automatically and notifies me — the 20% drawdown limit was reached",
            "C) Tries to recover the loss by increasing position sizes",
            "D) Waits for me to manually check and decide",
        ],
        correct_index=1,  # B
    )


# ── Main entry point ──────────────────────────────────────────────────────────

def build_approval_context(
    run_id: str,
    candidate_id: str,
    candidate_cards: list[dict],
    evidence_plans: list[dict],
    user_intent: dict | None,
    virtual_capital: float = 1_000_000,
) -> ApprovalContext:
    """
    Build the full ApprovalContext from pipeline artifacts.

    candidate_cards: list of CandidateCard dicts from pipeline store
    evidence_plans: list of EvidencePlan dicts from pipeline store
    user_intent: UserIntent dict (for kpi_anchor extraction)
    virtual_capital: default ¥1,000,000 (user adjustable at approval time)
    """
    # Find the target candidate card
    card: dict[str, Any] = {}
    for c in candidate_cards:
        if c.get("candidate_id") == candidate_id:
            card = c
            break

    candidate_name = card.get("display_name") or card.get("name") or candidate_id

    # Return band
    return_band = card.get("expected_return_band") or {}
    return_band_low = float(return_band.get("low_pct", 0))
    return_band_high = float(return_band.get("high_pct", 0))

    # Key risks
    key_risks: list[str] = card.get("key_risks") or []
    risk_annotations = [_annotate_risk(r) for r in key_risks]

    # KPI anchor from UserIntent (success_definition)
    kpi_anchor: str | None = None
    if user_intent:
        kpi_anchor = user_intent.get("success_definition") or user_intent.get("user_goal_summary")

    # Evidence items for this candidate
    evidence_items: list[dict] = []
    for ep in evidence_plans:
        if ep.get("candidate_id") == candidate_id:
            evidence_items = ep.get("evidence_items") or []
            break

    return ApprovalContext(
        run_id=run_id,
        candidate_id=candidate_id,
        authority_disclosure=_build_authority_disclosure(candidate_name, virtual_capital),
        kpi_alignment=_build_kpi_alignment(kpi_anchor, return_band_low, return_band_high),
        stop_condition_translations=_build_stop_translations(virtual_capital),
        risk_annotations=risk_annotations,
        data_access_disclosure=_build_data_access_disclosure(evidence_items),
        paper_run_explanation=_build_paper_run_explanation(virtual_capital),
        comprehension_check=_build_comprehension_check(virtual_capital),
    )
