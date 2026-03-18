# Companion AI v1 Specification

**Status**: Design-complete. Not yet implemented.
**Last updated**: 2026-03-18
**Scope**: v1 only — Goal Intake (Step 1) and Approval Gate (Step 10)
**Supersedes**: Initial draft of this file (same path)

---

## 1. Companion AI v1 Purpose

The Companion AI is a structured governance support layer that sits at the two
points where human judgment enters the system.

It has one job at each point:

**At Goal Intake**: Convert what the user actually wants — stated in everyday language —
into the structured constraints the pipeline needs to produce a valid, non-misleading
validation run.

**At Approval Gate**: Help the user understand, in plain terms, exactly what they are
authorizing — what the system will do on their behalf, what could go wrong, what
constitutes success, what external data it will access — before they commit.

The Companion AI is **not** a chatbot. It does not answer general questions.
It does not improve prompts. It does not explain investment concepts.
It surfaces governance gaps and translates technical system contracts into
language a non-expert user can act on.

---

## 2. User Problems It Solves

### 2.1 At Goal Intake

**Problem: Silent defaults compound downstream.**

The current `process_goal_intake()` assigns defaults when fields are missing —
`risk_preference = medium`, `time_horizon = one_week` — without the user knowing.
These defaults directly determine `minimum_evidence_standard` in the ResearchSpec,
candidate generation parameters, validation thresholds, and audit severity levels.
A wrong default propagates silently through all 12 pipeline steps. The user sees
no indication that the strategy they approved was optimized for a risk tolerance
they never consciously set.

**Problem: Vague goals produce misaligned candidates.**

"I want to make money in the stock market" and "I want a 7% annual return with
limited drawdown for a 3-year retirement fund" produce different research problems,
different candidates, and different audit criteria. The current system treats both
the same way.

**Problem: Out-of-scope goals proceed to the pipeline.**

The current domain classification is keyword-based. A user who types a goal involving
crypto, leveraged products, or options will fail the domain check — but only after
submission, with a generic rejection. The Companion intercepts before submission.

**Problem: Contradictions are invisible until audit findings.**

A user who wants "high returns" but sets `risk_preference = very_low` will receive
audit findings that cite risk/return tradeoff problems. But that contradiction was
knowable at intake. Surfacing it there — with the user present and able to correct —
is better than surfacing it as a validation failure the user cannot act on.

### 2.2 At Approval Gate

**Problem: The approval gate is performative, not substantive.**

Three checkboxes can be checked in 10 seconds. Nothing in the current flow verifies
that the user has read, understood, or genuinely consented to any of the content.
The approval gate is the ethical boundary between validation and autonomous operation.
A performative gate is not a gate.

**Problem: Users cannot evaluate what they are authorizing.**

The approval screen shows technical content — candidate strategy names, stop condition
identifiers, return bands. A non-expert user cannot translate "SC-01: max drawdown
-20%" into what will happen to their Paper Run and what they will need to do if it
triggers. They cannot relate the candidate's `expected_return_band` to the success
definition they stated at intake. They cannot assess whether the strategy's
key_risks are within their stated tolerance.

**Problem: Data access is unexplained.**

The approved strategy will acquire market data daily from external sources (Yahoo
Finance, FRED). The user has not been told what external services are accessed on
their behalf, what happens if those services fail, or whether the data is public
or private. In v1 this is low-stakes (public data only), but the precedent must
be correct.

**Problem: Authority scope is unexplained.**

The user approves a candidate. But what have they actually authorized the system
to do? The answer is specific: run signals daily, simulate trades at T+1, check
four stop conditions, halt automatically if any trigger, send notifications, re-evaluate
quarterly, request re-approval on candidate change. That is a meaningful grant of
authority. The user should know this before clicking Approve.

---

## 3. Architecture Placement

The Companion AI is a **thin support module** positioned at the API boundary,
before and during the two user-interaction steps. It does not touch the internal
pipeline.

```
┌──────────────────────────────────────────────────────────────┐
│  USER                                                         │
│                                                               │
│  Types goal → [Companion Goal Intake] → UserIntent           │
│                        ↓                                      │
│               (optional clarification                         │
│                questions, ≤4 total)                          │
│                                                               │
│  [INTERNAL PIPELINE — 12 steps — user does not see this]      │
│                                                               │
│  Reviews 2 candidates → [Companion Approval Gate]             │
│                                  ↓                            │
│                        (translations, authority               │
│                         disclosure, comprehension             │
│                         check, then checkboxes)               │
│                                  ↓                            │
│                              Approval                         │
│                                  ↓                            │
│                           Paper Run begins                    │
└──────────────────────────────────────────────────────────────┘
```

**What the Companion reads:** `CreateRunRequest`, `CandidateCard[]`,
`PresentationContext`, `Recommendation`, `Approval` schema.

**What the Companion writes:** `CompanionContext` (attached to `UserIntent` and
`Approval` for traceability — read-only to pipeline logic).

**What the Companion does not touch:** Steps 2–9, any pipeline module,
`DomainFrame`, `ResearchSpec`, `Candidate`, `EvidencePlan`,
`ValidationPlan`, `Audit`, `Recommendation`, `PaperRunState`.

**New backend module:** `backend/src/companion/`

**New API endpoints:**
- `POST /api/v1/runs/preflight` — trigger evaluation + question generation
- `POST /api/v1/runs/preflight/submit` — answer ingestion + constraint refinement
- `GET /api/v1/runs/{run_id}/approval-context` — approval translations + authority disclosure

The existing `POST /api/v1/runs` endpoint is unchanged. Preflight is optional.
A client that submits directly bypasses the Companion (valid for automated/API use).

---

## 4. Conversation Flow

### 4.1 Goal Intake flow

```
[1] User submits goal text (and optional fields)

[2] POST /api/v1/runs/preflight
    → Companion evaluates triggers (§5.1)
    → Returns CompanionGoalResponse:
        { needs_clarification, questions[], contradictions[], inferences[] }

[3a] IF needs_clarification = false:
     → Frontend proceeds directly to POST /api/v1/runs
     → No questions shown. No delay.

[3b] IF needs_clarification = true:
     → Frontend shows Companion question set (max 4 questions)
     → Each question is shown one at a time, or grouped if related
     → If contradictions[] is non-empty, contradiction notice shown first
       (before any questions — user sees it while still at intake)

[4] User answers questions
    → POST /api/v1/runs/preflight/submit (answers + original request)
    → Companion applies inference rules (§5.3)
    → Returns refined CreateRunRequest + inference summary for user review

[5] User reviews inference summary
    → Short display: "Based on your answers, we understood:
       - Risk tolerance: conservative (will stop at ~10% loss)
       - Time horizon: 1-year view
       - Success target: beat the market index"
    → User can correct any field before submitting
    → User clicks "Start Validation"

[6] POST /api/v1/runs fires with refined request
    → Pipeline begins (12-step internal engine)
```

**Important:** Step 5 is not a second approval gate. It is a transparency moment —
showing the user what was inferred from their answers before the pipeline runs.
It must be fast and non-blocking. If the user does not want to review, a "Looks
good — start" button is sufficient.

### 4.2 Approval Gate flow

```
[1] Pipeline completes. Frontend receives 2 candidate cards.

[2] GET /api/v1/runs/{run_id}/approval-context
    → Companion builds ApprovalContext:
        { authority_disclosure, kpi_alignment_check, stop_condition_translations[],
          risk_translations[], paper_run_explanation, data_access_disclosure,
          comprehension_check }

[3] Frontend renders Approval screen in this order:

    ── WHAT YOU ARE APPROVING ──────────────────────────────────
    [Authority disclosure block]
    "By approving, you authorize this system to:..."

    ── YOUR GOAL VS THIS CANDIDATE ─────────────────────────────
    [KPI alignment check]
    "You asked for [X]. This candidate targets [Y]."
    [Flag if misaligned]

    ── WHAT COULD GO WRONG ─────────────────────────────────────
    [Key risks in plain language]
    [Stop conditions in plain language]
    "If any of the above triggers, the system stops automatically."

    ── WHAT DATA THIS WILL USE ─────────────────────────────────
    [Data access disclosure]
    "This strategy reads daily market data from..."

    ── WHAT PAPER RUN MEANS ────────────────────────────────────
    [Paper Run explanation]

    ── QUICK CHECK ─────────────────────────────────────────────
    [Comprehension check — 1 question, must pass to enable checkboxes]

    ── CONFIRM ─────────────────────────────────────────────────
    [Three checkboxes — risks_reviewed, stop_conditions_reviewed,
     paper_run_understood]
    [Approve button — disabled until all three checked]

[4] User approves
    → POST /api/v1/runs/{run_id}/approve (unchanged endpoint)
    → Approval object created (unchanged schema + companion_context field)
    → Paper Run begins
```

**The approval flow is not a conversation.** It is a structured disclosure sequence
followed by a gate. The Companion generates the disclosure content and the
comprehension check. The user does not type answers — they read, answer one
multiple-choice question, and check boxes.

---

## 5. Data and Constraint Mapping Design

### 5.1 Goal Intake trigger evaluation

The Companion evaluates the following triggers after receiving `CreateRunRequest`.
Triggers are checked in order. If none fire, `needs_clarification = false`.

| # | Trigger | Condition |
|---|---------|-----------|
| T1 | Goal too short | `len(goal.strip()) < 40` |
| T2 | No measurable outcome | No number, percentage, or comparator found in goal text |
| T3 | Success criteria missing | `success_criteria` is empty AND T2 is true |
| T4 | Risk preference not provided | `risk` field is None |
| T5 | Time horizon not provided | `time_horizon` field is None |
| T6 | Contradiction detected | See §6 contradiction rules |
| T7 | Out-of-scope signal | Goal text contains out-of-scope marker (see §5.2) |

T1 alone does not trigger clarification if T2 and T3 are both false (a short but
complete goal is fine). T3 alone does not trigger if `success_criteria` is empty
but the goal text contains a measurable target.

**Maximum questions generated:** 4. If more than 4 triggers fire, questions are
prioritized: T6 (contradiction) is shown as a notice (not a question), T7 is shown
as a notice, then T3, T4, T5, T1/T2 in that order. Remaining gaps become
`open_uncertainties`.

### 5.2 Out-of-scope signal detection

The following patterns in goal text trigger a T7 notice (not a blocking error —
the user may clarify or redirect):

| Pattern | Signal text example | Redirect offered |
|---------|-------------------|-----------------|
| Crypto assets | "bitcoin", "ethereum", "crypto", "web3", "NFT" | "Japanese or US equities" |
| FX trading | "forex", "currency pair", "FX", "USD/JPY" | "macro equity strategy" |
| Leveraged products | "2x", "3x", "leveraged ETF", "margin" | "equity strategy without leverage" |
| Options/derivatives | "options", "calls", "puts", "futures", "derivatives" | "equity strategy" |
| Real estate | "REIT" is in-scope; "property", "real estate direct" is not | "equity REIT exposure" |
| Penny stocks / illiquid | "penny stock", "micro-cap" | "small-cap strategy" |

Notice text:

> **Note**: Your goal mentions [X]. The system currently validates investment strategies
> for Japanese and US equities using public daily data. [X] is outside this scope.
> Would you like to focus on [redirect], or restate your goal?

If the user proceeds without adjusting, `must_not_do` is left unchanged and the
domain classification step will handle it. This is not a hard block.

### 5.3 Constraint inference rules

Applied to free-text answers at `POST /api/v1/runs/preflight/submit`.

All inference is **pattern-based in v1** (regex + keyword extraction, no LLM).
LLM-based inference is a v2 enhancement.

#### Risk preference inference

Inference operates on the answer to Q-RISK (§5.5). Applied in order; first match wins.

| Answer signal | Inferred `risk_preference` |
|--------------|---------------------------|
| "preserve", "don't lose", "protect", "safe", "lose nothing", loss threshold < 8% | `very_low` |
| "small loss", "conservative", loss threshold 8–18%, "not much risk" | `low` |
| "some ups and downs", "moderate", "can handle market swings", loss threshold 18–35% | `medium` |
| "aggressive", "high risk", "willing to lose a lot", loss threshold > 35% | `high` |
| No clear signal | Default `medium`, flagged in `open_uncertainties` |

**Threshold extraction**: If the user states a specific percentage ("lose up to 15%"),
that number is extracted and used as-is for threshold comparison, regardless of
surrounding language.

#### Time horizon inference

Applied to answer to Q-TIME (§5.5).

| Answer signal | Inferred `time_horizon_preference` |
|-------------|-----------------------------------|
| "days", "this week", "next week", "quick" | `fast` |
| "month", "30 days", "short term", "few weeks" | `one_month` |
| "few weeks", "1-2 months" | `one_week` |
| "6 months to 2 years", "medium term" | `one_month` (closest v1 option) |
| "years", "long term", "3+", "5 years", "decade", "retirement" | `quality_over_speed` |
| No clear signal | Default `one_week`, flagged in `open_uncertainties` |

#### Success definition extraction

If the answer to Q-SUCCESS contains a numerical target, that text becomes
`success_definition` verbatim (first 200 chars). If the answer is qualitative only,
the Companion maps to the appropriate archetype in `_default_success_definition()`
from `goal_intake.py` and records the mapping:

```
open_uncertainties.append(
  "success_definition inferred from qualitative answer: '{answer}' → '{mapped}'"
)
```

#### KPI extraction for approval alignment

The inferred `success_definition` is retained as a `kpi_anchor` in `CompanionContext`.
This is used at Approval Gate (§7.2) to check whether the presented candidate's
`expected_return_band` plausibly corresponds to what the user stated they wanted.
The KPI anchor is not used by the pipeline — only by the Companion's approval
disclosure logic.

### 5.4 Authority boundary mapping

At Approval Gate, the Companion translates the abstract act of approval into a
specific list of authorized actions. This list is derived from the pipeline
architecture and is fixed in v1.

**Authority disclosure template (generated once per candidate at approval time):**

```
By approving Candidate [name], you authorize this system to:

1. Access daily market data from Yahoo Finance and FRED on your behalf,
   every trading day, until the strategy is stopped or re-evaluated.

2. Simulate running this strategy daily in a virtual portfolio, starting
   with [virtual_capital, formatted]. No real money is used.

3. Automatically stop the simulation if any of the four stop conditions
   are triggered (detailed below). You will be notified when this happens.

4. Send you a performance summary every month.

5. Re-evaluate this strategy automatically after [re-evaluation date].
   If conditions have changed significantly, you will be asked to re-approve.

You can stop the simulation at any time from the status page.
```

The `virtual_capital` is drawn from `RuntimeConfig.initial_virtual_capital`
(default ¥1,000,000, user-adjustable at approval time).

This block appears at the top of the Approval screen, before candidate details.
It is the first thing the user reads.

### 5.5 Question templates

Questions are generated from triggered rules. Only questions with a fired trigger
are shown. Questions are rewritten to use the user's own words where available.

**Q-SUCCESS** (fires on T2, T3):

> "What would make this worthwhile for you?
>
> For example: "beat the stock market index over 3 years", "8% per year",
> "double what I put in over 10 years", "match inflation without big losses".
>
> A rough target is fine — the system will work within it."

**Q-RISK** (fires on T4):

> "How much are you comfortable losing before you'd want the system to stop
> automatically?
>
> For example: "stop if I've lost 5% of what I started with", "I can handle
> losing 25% if the long-term upside is there", "I'm very cautious — stop at
> the first sign of trouble".
>
> The system has built-in stops — this helps calibrate them to your tolerance."

**Q-TIME** (fires on T5):

> "How long are you thinking about this strategy?
>
> For example: "I want to see results in 6 months", "I'm thinking about a
> 3-year horizon", "long term — 10 years or more".
>
> This affects how the system evaluates candidates."

**Q-SCOPE** (fires on T7 — not a question; a redirect notice, shown first):

> "Your goal mentions [flagged term]. The system currently validates strategies
> for Japanese and US equities using public daily data. [flagged term] is outside
> this scope.
>
> Would you like to adjust your goal, or would you like to proceed and see what
> the system can test within these boundaries?"

**Q-REFINE** (fires on T1 only, when goal is short but T2/T3 did not fire):

> "Your goal is noted. Before we start, one quick question: is there anything
> the system should specifically avoid — particular stocks, sectors, or
> trading styles you don't want?"
>
> *(This is optional. You can skip it.)*

---

## 6. Contradiction Detection Rules

Contradictions are surfaced as notices, not blocks. The user can proceed with a
contradiction noted in `open_uncertainties`. The pipeline handles the tension in
its own audit logic (Step 7).

The Companion surfaces the contradiction at intake so the user can correct it
consciously, rather than discovering it later in an audit finding they cannot act on.

### Rule set

| ID | Condition | Notice text |
|----|-----------|-------------|
| CON-01 | `risk_preference = very_low` AND return target > 8% annually | "You've indicated very low risk tolerance but a return target of [X]%. Most strategies that target [X]% carry drawdown risk above your stated limit. The system will search for candidates that fit your risk constraint — but the candidates may have lower return potential than your target." |
| CON-02 | `risk_preference = very_low` AND `must_not_do` is empty AND goal mentions "returns" | "You've indicated very low risk, but haven't listed any exclusions. Broad equity strategies with no exclusions typically carry more volatility than a very-low-risk tolerance implies. Consider adding exclusions (e.g., 'no leveraged positions', 'no small caps') or adjusting your risk tolerance." |
| CON-03 | `time_horizon = fast` AND goal contains "stable", "long-term", "retirement", "income" | "Your goal mentions [long-term signal] but your stated time horizon is short-term. These are in tension. Long-term stability strategies require longer evaluation periods. If the horizon is short, the system's validation evidence will be limited." |
| CON-04 | `time_horizon = fast` AND `risk_preference = very_low` | "Very-low-risk strategies with very short time horizons are difficult to validate. Validation requires enough history to observe meaningful drawdown events. A short time horizon limits what the system can confirm." |
| CON-05 | `must_not_do` contains something that appears in `raw_goal` positively | "Your goal mentions [X] favorably, but your exclusion list also includes [X]. These conflict. Please clarify whether [X] should be included or excluded." |
| CON-06 | Return target > 20% annually AND `risk_preference = low` or `very_low` | "A return target of [X]% annually is high. Strategies at this return level have historically carried significant drawdown risk. At [risk_preference] risk tolerance, the system may not find candidates that can reach this target without violating your stop conditions." |

**Notice display rules:**
- All fired notices are shown at once, before questions
- Each notice names the specific conflict, using the user's own words
- Each notice ends with a conditional: "The system will proceed within your stated constraints" or "Please clarify before we continue" (CON-05 requires clarification — the conflict is unresolvable without it)
- Notices are not errors. They are warnings with context.

### Contradiction propagation

If a contradiction is not resolved by the user (they proceed anyway), each contradiction
is appended to `open_uncertainties` in the final `UserIntent` with the text:

```
"Unresolved contradiction [CON-XX]: [summary]. Pipeline will apply [primary constraint]."
```

The primary constraint preference order: `risk_preference` overrides return target.
`must_not_do` overrides `raw_goal` signals. This is documented in the uncertainty.

---

## 7. Approval Support Behavior

### 7.1 What must remain human-approved

The following decisions cannot be made by the system without explicit user action.
The Companion does not weaken or shortcut any of these.

| Decision | Why it must be human | Companion role |
|----------|---------------------|----------------|
| Candidate selection (Primary vs. Alternative) | Directly affects what strategy runs | None — user selects on Presentation screen |
| Risk acknowledgment | User must personally accept that loss is possible | Translate risk language; require checkbox |
| Stop condition acknowledgment | User must understand automatic halt behavior | Translate each condition; require comprehension check |
| Paper Run consent | User must know no real money is used but real data and daily computation are | Explicit explanation; require checkbox |
| Virtual capital amount | User sets their own mental frame for paper loss significance | Show default, allow adjustment, explain what it means |
| Re-approval after halt | After any stop condition fires, a new approval is required | Explain this at first approval so it is not a surprise |

**What the Companion does not do:**

- Auto-confirm checkboxes if user has answered comprehension check correctly
- Skip any disclosure block based on user profile or past runs
- Reduce the number of required confirmations
- Suggest which candidate to approve

### 7.2 KPI alignment check

Before presenting the candidate's return band, the Companion checks whether the
candidate plausibly aligns with the user's stated success criteria.

**Alignment check logic:**

```
kpi_anchor = CompanionContext.kpi_anchor (from Goal Intake)

IF kpi_anchor contains a numerical return target:
    extract target_return_pct from kpi_anchor

    IF target_return_pct > candidate.expected_return_band.high_pct * 1.5:
        → misalignment: candidate return band is well below user's target
        → show KPI gap notice

    IF target_return_pct < candidate.expected_return_band.low_pct * 0.5:
        → overdelivery notice: candidate targets more than user needs
        → show note (not a warning — this is good, but worth noting)

    IF within normal range:
        → show alignment confirmation: "This candidate's return range aligns
          with your stated target of [X]."

IF kpi_anchor is qualitative only (no number extracted):
    → show: "Your goal was [summary]. This candidate targets [return band] per year,
      after simulated costs."
```

The KPI alignment check is shown directly above the candidate card at Approval Gate.
It is not shown on the Presentation screen (which is about candidate comparison,
not approval governance).

### 7.3 Stop condition translation

Each stop condition is rendered in plain language before the `stop_conditions_reviewed`
checkbox. Technical identifiers are preserved alongside translations.

**SC-01** plain language:

> **SC-01 — Automatic stop if the portfolio loses 20% of its starting value.**
>
> With [¥1,000,000] virtual capital, this would trigger if the simulated value
> fell to [¥800,000]. At that point, the system stops all simulated trading and
> notifies you. You would need to review the situation and re-approve to continue.
>
> This is the most likely condition to trigger. It fires automatically — you do
> not need to monitor it.

**SC-02** plain language:

> **SC-02 — Automatic stop if the strategy underperforms the market for 3 months in a row.**
>
> "Underperform" means the strategy's return is lower than the [Nikkei 225 / S&P 500]
> benchmark for three consecutive calendar months — even if the strategy is not losing
> money in absolute terms. This condition detects strategies that are working worse
> than simply holding an index fund.

**SC-03** plain language:

> **SC-03 — Automatic pause if the strategy generates an unusual signal.**
>
> If the strategy's daily signal deviates more than 3 standard deviations from its
> historical pattern, the system pauses and notifies you rather than acting on
> what may be a data error or model breakdown. You can review and resume.

**SC-04** plain language:

> **SC-04 — Automatic pause if data quality fails for 3 consecutive trading days.**
>
> If the system cannot obtain reliable market data for 3 days in a row — for example,
> because the data source is unavailable or corrupted — it pauses rather than
> operating on bad data. You will be notified.

**After all four conditions:** The Companion adds:

> These four conditions are set by the system. You cannot change the thresholds in v1.
> They exist to protect you from the strategy running in circumstances where it
> should not run. All four conditions fire automatically. None require you to
> monitor the system.

### 7.4 Risk translation

Each `key_risk` string from the CandidateCard is annotated with a plain-language
expansion. In v1, annotations are generated from a template library keyed to
risk category patterns. LLM-generated annotations are deferred to v2.

**Template library — v1 categories:**

| Risk category pattern | Plain-language annotation |
|----------------------|--------------------------|
| "crowding", "factor crowding" | "When many strategies use the same signals, they can all sell at the same time. During market stress, this can cause larger losses than the backtest predicted." |
| "regime", "regime change", "regime shift" | "This strategy works better in certain market environments than others. If the market changes character — for example, from a rising to a falling market — the strategy may underperform until conditions return." |
| "overfitting", "curve-fitting" | "There is a risk that this strategy looks good in historical data partly because it was fitted to that data. Out-of-sample performance may be weaker than the backtest suggests." |
| "data quality", "data availability" | "This strategy depends on data quality. If the data source changes, goes offline, or provides errors, the strategy's signals may degrade. The system monitors for this (SC-04)." |
| "cost assumption", "transaction costs" | "The backtest assumes specific transaction costs (10bps commission + 10bps spread). Real costs may be higher, especially during volatile periods. Higher costs reduce net returns." |
| "liquidity" | "This strategy may trade stocks that are difficult to buy or sell in large quantities. In a real execution context, the actual prices achieved may differ from those assumed in the backtest." |
| "short selling" | "If this strategy takes short positions, losses on the short leg are theoretically unlimited. The Paper Run simulates this but real short exposure should be reviewed carefully before live execution." |

If no template matches a risk string, the annotation is:

> [risk text as provided] — no additional plain-language annotation available.

### 7.5 Data access disclosure

Before the `paper_run_understood` checkbox, the Companion renders the data access
block. This is generated from the candidate's evidence plan (retrieved from
the pipeline store for this run).

**Template:**

> **What data this strategy uses:**
>
> - Daily stock price data from [Yahoo Finance / public source] for
>   [N] securities
> - [If applicable: Macro economic data from FRED (US Federal Reserve public data)]
> - [If applicable: Commitments of Traders data from CFTC (US public data)]
>
> All data sources are public and free. No private data or paid subscriptions
> are used. The system accesses these sources every trading day during the Paper Run.
>
> If a data source is temporarily unavailable, the system pauses (SC-04) rather
> than operating on incomplete information.

**What is not disclosed** (because it is internal pipeline detail, invisible by design):
- The specific backtest parameters
- The signal generation logic
- The portfolio construction method
- The statistical tests run

These are intentionally hidden. Disclosing them would require the user to interpret
them, which defeats the purpose of the product.

### 7.6 Paper Run explanation

Fixed text, shown before the `paper_run_understood` checkbox:

> **What "Paper Run" means:**
>
> The system will simulate this strategy every trading day using real market data —
> but no real money is used, and no real trades are placed. It starts with a virtual
> portfolio of [¥1,000,000] (or your adjusted amount). All profits and losses are
> simulated.
>
> The purpose of a Paper Run is to observe whether the strategy behaves in live
> market conditions the way the backtests predicted. A strategy that works well
> in historical data sometimes behaves differently when run day-by-day with real data.
>
> Paper Run results do not guarantee that real-money execution would produce the
> same outcomes. They are a real-time validation check — not a trading system.
>
> In v1, the system only runs Paper Runs. Real-money execution is not available.

### 7.7 Comprehension check

One multiple-choice question, required before checkboxes are enabled.

The question is seeded from SC-01 (drawdown) because it is the most concrete,
the most likely to trigger, and the most consequential for the user to understand.

**Question:**

> **Quick check — select the correct answer:**
>
> You approved a Paper Run starting with ¥1,000,000. Six months later, the
> simulated portfolio is worth ¥790,000.
>
> What does the system do?
>
> ○ (A) Continues running — the loss is within my stated tolerance
> ○ (B) Stops automatically and notifies me — the 20% drawdown limit was reached
> ○ (C) Tries to recover the loss by increasing position sizes
> ○ (D) Waits for me to manually check and decide

**Correct answer:** (B)

**On incorrect answer:**

> That's not the right answer. Based on SC-01, if the portfolio falls 20%
> (from ¥1,000,000 to ¥800,000 or below), the system stops automatically and
> notifies you. You would then review the situation and decide whether to
> re-approve and continue.
>
> ¥790,000 is below ¥800,000 — so SC-01 would have already triggered.
>
> Please re-read the stop condition descriptions above before continuing.

After a second incorrect answer:

> The system requires you to review the stop conditions before proceeding.
> If you have questions, please read the SC-01 description above again or
> restart this page.

There is no maximum attempt limit. The user must answer correctly to proceed.
This is not a punitive gate — the question is easy for anyone who has read SC-01.

---

## 8. v1 Scope and Out-of-Scope

### In scope (v1)

| Component | Description |
|-----------|-------------|
| Trigger evaluation at Goal Intake | Detect incomplete/ambiguous goals, out-of-scope signals, contradictions |
| Clarification questions (≤4) | Q-SUCCESS, Q-RISK, Q-TIME, Q-SCOPE (redirect notice), Q-REFINE |
| Constraint inference | Pattern-based: risk_preference, time_horizon_preference, success_definition, must_not_do |
| Contradiction surfacing | Rules CON-01 through CON-06, shown before questions |
| Inference review step | Show user what was inferred before pipeline starts |
| Authority disclosure block | Fixed template rendered at Approval Gate |
| KPI alignment check | Compare kpi_anchor to candidate expected_return_band |
| Stop condition translations | Plain-language for SC-01 to SC-04, with user's virtual capital amount |
| Risk annotations | Template-based, keyed to risk category patterns |
| Data access disclosure | Generated from evidence plan for the run |
| Paper Run explanation | Fixed template |
| Comprehension check | SC-01 multiple-choice, must pass before checkboxes enabled |
| CompanionContext | Optional tracing block attached to UserIntent and Approval |

### Out of scope (v1)

| Excluded | Reason |
|----------|--------|
| LLM-based inference | Latency, unpredictability, incorrect plain-language risk. Deferred to v2 |
| Companion involvement in pipeline steps 2–9 | Pipeline is intentionally opaque. Companion does not interpret internal results |
| Multi-turn conversation | Companion has at most 1 round-trip per intake, 0 round-trips at approval |
| General investment Q&A | Not this product. Users who ask investment questions should be redirected, not answered |
| Companion memory across sessions | v1 is stateless per run. No user profile |
| Stop condition threshold negotiation | Thresholds are fixed. Companion explains them, does not modify them |
| Personalization of internal pipeline | Companion context does not influence pipeline logic |
| Second comprehension check (beyond SC-01) | One is sufficient. More checks add friction without proportional benefit |
| Companion involvement in Paper Run or re-evaluation | These steps are autonomous. No user governance required unless a halt occurs |
| Skip logic for "expert" users | All users go through the same gate. Expertise does not bypass the approval contract |
| Companion-suggested candidates | The Companion does not advise. It discloses. Recommendation is the pipeline's job |

### Constraints preserved

The Companion AI does not break and must not weaken any of the following:

| Constraint | How preserved |
|-----------|--------------|
| Investment-first v1 | Companion redirects out-of-scope goals, does not accept them |
| Paper Run only | Paper Run explanation is mandatory at approval. Cannot be skipped |
| 2-candidate model | Companion does not interact with candidate presentation. Cards shown as-is |
| Approval-before-runtime | Comprehension check and checkboxes are added to approval, not removed |
| Hidden internal validation engine | Companion discloses what the user needs to approve; does not expose pipeline internals |

---

## 9. Recommended Implementation Sequence

The Companion should be implemented in three distinct passes. Each pass is
independently deployable. No pass breaks existing functionality.

### Pass 1: Goal Intake clarification (backend only)

**Deliverables:**
- `backend/src/companion/` module with:
  - `trigger_evaluator.py` — trigger evaluation logic (§5.1, §5.2)
  - `constraint_inferrer.py` — pattern-based inference rules (§5.3)
  - `contradiction_detector.py` — contradiction rules CON-01 to CON-06 (§6)
  - `question_builder.py` — question template generation (§5.5)
- New Pydantic models: `CompanionQuestion`, `CompanionGoalResponse`,
  `CompanionAnswers`, `CompanionContext`
- `POST /api/v1/runs/preflight` endpoint
- `POST /api/v1/runs/preflight/submit` endpoint
- Tests: trigger evaluation, inference rules (all pathways), contradiction detection

**Does not require:** any frontend changes, any pipeline changes

### Pass 2: Goal Intake frontend wiring

**Deliverables:**
- `InputPage.tsx` updated to:
  - Call `/preflight` after initial submission
  - Show contradiction notices (if any) inline
  - Show clarification questions (if `needs_clarification = true`)
  - Show inference review step before submitting to `/api/v1/runs`
- No new pages required — all within current InputPage flow

**Requires:** Pass 1 complete

### Pass 3: Approval Gate support

**Deliverables:**
- `backend/src/companion/approval_context_builder.py` — generates all approval
  disclosure blocks from pipeline store data
- `GET /api/v1/runs/{run_id}/approval-context` endpoint
- Risk annotation template library
- Comprehension check logic
- `ApprovalPage.tsx` updated to:
  - Fetch `/approval-context` on mount
  - Render authority disclosure, KPI alignment check, stop condition translations,
    risk annotations, data access disclosure, Paper Run explanation
  - Render comprehension check before enabling checkboxes
- Tests: approval context generation, comprehension check pass/fail logic

**Requires:** Pass 1 and 2 complete (for CompanionContext schema); pipeline store
access (already available via `get_store()`)

---

## Appendix A: New Schema Objects

```python
class CompanionQuestion(BaseModel):
    id: str                      # "Q-SUCCESS" | "Q-RISK" | "Q-TIME" | "Q-SCOPE" | "Q-REFINE"
    text: str
    type: str                    # "free_text" | "multiple_choice" | "redirect_notice"
    options: list[str] = Field(default_factory=list)
    optional: bool = False

class CompanionGoalResponse(BaseModel):
    needs_clarification: bool
    questions: list[CompanionQuestion]
    contradictions: list[str]    # Human-readable contradiction notices
    inferences: list[dict]       # [{field, from_text, inferred_value}]

class CompanionAnswers(BaseModel):
    answers: dict[str, str]      # question_id -> free-text or selected option

class StopConditionTranslation(BaseModel):
    id: str                      # "SC-01" | "SC-02" | "SC-03" | "SC-04"
    plain_language: str
    virtual_capital_amount: Optional[float] = None  # SC-01 only

class RiskAnnotation(BaseModel):
    original_risk_text: str
    annotation: str

class ComprehensionCheck(BaseModel):
    question: str
    options: list[str]           # A through D
    correct_index: int           # 0-based

class ApprovalContext(BaseModel):
    run_id: str
    candidate_id: str
    authority_disclosure: str
    kpi_alignment: dict          # {aligned: bool, anchor: str, candidate_band: str, note: str}
    stop_condition_translations: list[StopConditionTranslation]
    risk_annotations: list[RiskAnnotation]
    data_access_disclosure: str
    paper_run_explanation: str
    comprehension_check: ComprehensionCheck

class CompanionContext(BaseModel):
    # Attached to UserIntent.companion_context and Approval.companion_context
    # Optional field — pipeline logic never reads this
    questions_asked: list[str] = Field(default_factory=list)
    inferences_made: list[dict] = Field(default_factory=list)
    contradictions_flagged: list[str] = Field(default_factory=list)
    comprehension_check_passed: bool = False
    comprehension_check_attempts: int = 0
    companion_active: bool = True
```

These objects live in `backend/src/companion/models.py`.
They do not extend or modify any existing domain model.
`CompanionContext` is added as `Optional[CompanionContext] = None` to
`UserIntent` and `Approval` in `backend/src/domain/models.py`.

---

## Appendix B: Files Requiring Minor Consistency Updates

The following existing files have minor gaps relative to this spec. Updates
are minimal — no rewrites, no scope changes.

| File | Gap | Recommended update |
|------|-----|-------------------|
| `docs/product/v1_boundary.md` | No mention of Companion AI in user-facing component list | Add one row to the user-facing table: "Companion AI support — optional clarification at Goal Intake and disclosure layer at Approval Gate" |
| `docs/system/core_loop.md` Step 1 | "The user types what they want" — does not acknowledge optional clarification | Add 1 sentence: "If the goal is incomplete or ambiguous, an optional Companion AI layer asks up to 4 clarifying questions before Step 1 output is finalized." |
| `docs/system/core_loop.md` Step 10 | Approval Gate description does not mention plain-language disclosure | Add 1 sentence: "A Companion AI layer provides plain-language translations of stop conditions, risk items, and data access before the user is shown the confirmation checkboxes." |
| `docs/implementation_status.md` | Companion AI listed nowhere | Add new section: "Companion AI: spec complete, not yet implemented." |

None of these updates change product identity, v1 boundary, or pipeline behavior.
They add one sentence or one table row to acknowledge what this spec defines.

---

**Role of this document**: Authoritative v1 spec for the Companion AI layer.
Defines scope, behavior, architecture fit, governance model, and constraints.
Implementation must not exceed this spec without explicit re-scoping.
This document does not supersede any other source-of-truth document.
Where it touches core loop or boundary documents, those documents take precedence
and should be updated for consistency per Appendix B.
