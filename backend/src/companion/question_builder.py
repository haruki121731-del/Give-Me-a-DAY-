"""
Companion AI — Question builder.

Generates CompanionQuestion objects from fired trigger IDs.
Questions use fixed templates per spec §5.5.
Maximum 4 questions returned (T6 and T7 appear as notices, not questions).
Priority order: T3, T4, T5, T1/T2, then Q-REFINE.
"""

from .models import CompanionQuestion
from .trigger_evaluator import TriggerResult

_MAX_QUESTIONS = 4


def _q_success() -> CompanionQuestion:
    return CompanionQuestion(
        id="Q-SUCCESS",
        text=(
            "What would make this worthwhile for you?\n\n"
            "For example: \"beat the stock market index over 3 years\", "
            "\"8% per year\", \"double what I put in over 10 years\", "
            "\"match inflation without big losses\".\n\n"
            "A rough target is fine — the system will work within it."
        ),
        type="free_text",
        optional=False,
    )


def _q_risk() -> CompanionQuestion:
    return CompanionQuestion(
        id="Q-RISK",
        text=(
            "How much are you comfortable losing before you'd want the system "
            "to stop automatically?\n\n"
            "For example: \"stop if I've lost 5% of what I started with\", "
            "\"I can handle losing 25% if the long-term upside is there\", "
            "\"I'm very cautious — stop at the first sign of trouble\".\n\n"
            "The system has built-in stops — this helps calibrate them to your tolerance."
        ),
        type="free_text",
        optional=False,
    )


def _q_time() -> CompanionQuestion:
    return CompanionQuestion(
        id="Q-TIME",
        text=(
            "How long are you thinking about this strategy?\n\n"
            "For example: \"I want to see results in 6 months\", "
            "\"I'm thinking about a 3-year horizon\", "
            "\"long term — 10 years or more\".\n\n"
            "This affects how the system evaluates candidates."
        ),
        type="free_text",
        optional=False,
    )


def _q_scope(out_of_scope_terms: list[tuple[str, str]]) -> CompanionQuestion:
    """Build a redirect notice for the first detected out-of-scope term."""
    term, redirect = out_of_scope_terms[0]
    return CompanionQuestion(
        id="Q-SCOPE",
        text=(
            f"Your goal mentions {term}. The system currently validates strategies "
            f"for Japanese and US equities using public daily data. {term} is outside "
            f"this scope.\n\n"
            f"Would you like to adjust your goal to focus on {redirect}, "
            f"or would you like to proceed and see what the system can test within "
            f"these boundaries?"
        ),
        type="redirect_notice",
        optional=True,
    )


def _q_refine() -> CompanionQuestion:
    return CompanionQuestion(
        id="Q-REFINE",
        text=(
            "Your goal is noted. Before we start, one quick question: is there anything "
            "the system should specifically avoid — particular stocks, sectors, or "
            "trading styles you don't want?\n\n"
            "(This is optional. You can skip it.)"
        ),
        type="free_text",
        optional=True,
    )


def build_questions(
    trigger_result: TriggerResult,
) -> list[CompanionQuestion]:
    """
    Build ordered question list from fired triggers.
    Max 4 questions. T6 contradictions are notices (handled separately).
    T7 produces a redirect notice (counted toward the 4 limit).
    Priority: T3 → T4 → T5 → T1/T2 → T7 → Q-REFINE.
    """
    questions: list[CompanionQuestion] = []
    fired = set(trigger_result.fired)

    if len(questions) < _MAX_QUESTIONS and ("T2" in fired or "T3" in fired):
        questions.append(_q_success())

    if len(questions) < _MAX_QUESTIONS and "T4" in fired:
        questions.append(_q_risk())

    if len(questions) < _MAX_QUESTIONS and "T5" in fired:
        questions.append(_q_time())

    if len(questions) < _MAX_QUESTIONS and "T7" in fired and trigger_result.out_of_scope_terms:
        questions.append(_q_scope(trigger_result.out_of_scope_terms))

    # T1 alone (short goal, no other gaps) gets Q-REFINE
    if (
        len(questions) < _MAX_QUESTIONS
        and "T1" in fired
        and "T2" not in fired
        and "T3" not in fired
    ):
        questions.append(_q_refine())

    return questions
