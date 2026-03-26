# Layer 0 — Target Respondent Profile

**Purpose**: Define who Haruki should talk to first, why, and what to learn from them.
**Date**: 2026-03-26
**Related**: `mom_test_run_plan.md`, OL-016

---

## Primary Respondent Profile

**Who**: Individual systematic / quantitative traders who personally research and build investment strategies.

**Specifically**:
- Has spent ≥6 months researching or developing at least one systematic investment strategy
- Has personally experienced abandoning a strategy direction after investing significant research time
- Works independently or in a small team (≤5 people) — not inside a large quant fund's infrastructure
- Uses programmatic tools (Python, R, QuantConnect, Zipline, backtrader, or similar)
- Evaluates strategies against data, not purely discretionary / gut-based

**Why this profile first**:

This is the smallest viable learning target because:

1. **Accessible**: Individual quant traders are reachable through online communities (QuantConnect, r/algotrading, EliteTrader, Quantopian alumni, Twitter/X quant circles). No institutional gatekeepers.
2. **Pain is personal**: They bear the full cost of wasted research time themselves. In a fund, the cost is distributed. For individuals, a month spent on a fragile strategy direction is a month of their own time and capital.
3. **Decision-making is visible**: They make the go/no-go decision on strategy directions themselves. No committee, no PM layer. The exact decision Give Me a DAY targets is theirs to make.
4. **Honest feedback is likely**: They are not evaluating your product for procurement. They are describing their own workflow. Lower social pressure to be polite.
5. **Volume exists**: There are thousands of active individual systematic traders globally, enough to find 10–15 candidates quickly.

**Why NOT institutional quant researchers first**:
- Harder to reach (gatekeepers, compliance, NDAs)
- Their workflow includes institutional infrastructure that individual traders lack — different pain profile
- Feedback is slower (scheduling, approvals)
- They are a valid later target, not a first-pass target

---

## Exclusion Profiles

Do NOT interview these people in Layer 0:

| Profile | Why excluded |
|---------|-------------|
| Discretionary / fundamental traders | They do not face the systematic strategy evaluation problem |
| Passive investors (index, buy-and-hold) | No strategy research pain |
| Fintech product managers | They evaluate products, not strategy directions |
| Friends who know about Give Me a DAY | Contaminated responses — they will evaluate the idea, not describe their pain |
| People who have never abandoned a strategy direction | No direct experience with the core pain |
| Crypto-only traders without systematic methodology | Different problem space; may not generalize |
| People who only paper-trade with no real capital intent | Pain intensity is lower; learning signal is weaker |

---

## What We Are Trying to Learn

Layer 0 interviews must answer these questions, in priority order:

| # | Question | Why it matters |
|---|----------|----------------|
| 1 | Do individual systematic traders actually spend significant time evaluating strategy directions before committing? | If evaluation is trivial or instant for them, the core pain may not exist |
| 2 | What does their current evaluation process look like? | Reveals the real workflow we're competing against |
| 3 | How often do they abandon a direction after investing time? | Frequency = pain severity proxy |
| 4 | What is the cost of a wrong direction for them? (time, capital, opportunity) | Quantifies the pain |
| 5 | Do they compare multiple strategy directions before picking one? | Tests whether multi-candidate comparison (core product feature) maps to real behavior |
| 6 | What tools/methods do they currently use to pre-validate? | Reveals existing substitutes and competitive landscape |
| 7 | What would they change about their current evaluation process? | Open-ended pain probe — may reveal unexpected needs |

**What we are NOT trying to learn in Layer 0**:
- Whether they like the product idea
- Whether they would pay for it
- Whether the UI makes sense
- Whether the technical architecture is right
- Whether the pricing is right

---

## Signals That This Profile Is Wrong

If ≥2 of the following emerge during interviews, the primary profile needs revision:

| Signal | What it means |
|--------|---------------|
| Respondents say strategy evaluation takes <1 hour and is not painful | The pain is too small for this profile |
| Respondents never abandon strategy directions — they always follow through | The "wasted effort" pain does not exist here |
| Respondents say "I just backtest immediately, there's no pre-evaluation phase" | The pre-validation step we're targeting may not exist in their workflow |
| Respondents describe a completely different primary pain (data quality, execution, not evaluation) | The product's core value proposition misses their actual problem |
| Respondents are unreachable — Haruki cannot find or schedule 3 within 2 weeks | The profile is theoretically right but practically inaccessible |

If profile invalidation occurs: close OL-016 with a rejection verdict. Open a new loop for ICP revision. Do not force-fit the data.

---

## How Many Interviews Are Enough

**First pass**: 3–5 interviews.

- 3 is the minimum for OL-016 closure (per `mom_test_run_plan.md`)
- 5 is the target if scheduling permits
- Do NOT go beyond 5 before synthesizing. More interviews without synthesis produces noise, not signal.

**After synthesis**: If pain is confirmed but ICP needs refinement, run a second pass of 3–5 with adjusted targeting. But this is a separate decision, not part of Layer 0.

**Decision gate after first pass**:
- Pain confirmed → proceed to showing product to 2–3 respondents (Phase 2 per `USER_JUDGMENT_REVIEW_LAUNCH_LOOP.md`)
- Pain not found → revise ICP hypothesis, reopen targeting
- Pain found but different from expected → revise product framing, then re-interview
