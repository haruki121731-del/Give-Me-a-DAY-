# blocker_resolution_plan.md

**Purpose**: Concrete resolution paths for the four blockers standing between current state and factory-layer precondition readiness.
**Last updated**: 2026-03-25
**Related**: `docs/system/factory_layer_preconditions.md`, `OPEN_LOOPS.md`, `DECISIONS.md`

---

## Blocker Map

| Blocker | Precondition | Type | Unblocks |
|---------|-------------|------|---------|
| OL-022 (API key credit exhausted) | C2 dependency | Human action | eval-run.yml → OL-017 |
| OL-017 (6 eval cases remaining) | C2 | Agent (after OL-022) | LLM quality baseline → C3 dependency |
| OL-016 (no Mom Test interviews) | C1 | Human action + agent support | Customer signal → C3 dependency |
| D-001 review (minimum loop not confirmed) | C3 | Agent (after OL-016, OL-017, OL-019) | Factory layer gate |

---

## OL-022 — ANTHROPIC_API_KEY Credit Exhaustion

**Owner**: Haruki (human — cannot be resolved by agent)
**Dependency**: None — this is the root blocker
**Required evidence**: `eval-run.yml` workflow dispatch produces 12 ok results (not api_error)

### Resolution path

**Option A — Recharge existing key** (recommended if faster):
1. Go to Anthropic console → `Give Me a DAY` workspace → Billing
2. Add credits to the `for openhands` key
3. Verify: trigger a test workflow dispatch or check `eval-run.yml` logs

**Option B — Rotate key**:
1. Create a new API key in the `Give Me a DAY` Anthropic workspace
2. Go to GitHub repo → Settings → Secrets and variables → Actions
3. Update `ANTHROPIC_API_KEY` secret value with the new key
4. Trigger `eval-run.yml` via workflow_dispatch to verify

**What agent can do now**: Nothing — this requires Haruki's Anthropic account access.

**Success condition**: `eval-run.yml` run produces ≥1 ok result (not api_error) on first case.

**Failure condition**: New key also returns 400 errors → root cause is billing tier or model access, not credit balance. Agent must investigate error message from workflow logs.

**Time estimate**: 5–15 minutes once Haruki initiates.

---

## OL-017 — Complete LLM Eval Run (6 Remaining Cases)

**Owner**: Agent (execution) / Haruki (API key prerequisite)
**Dependency**: OL-022 must resolve first
**Required evidence**: 12/12 ok results in `evals/results/`, per-module averages updated in `docs/state/engineering.md`

### Resolution path

After OL-022 resolves:

**Step 1**: Haruki triggers `eval-run.yml` via workflow_dispatch on GitHub → Actions tab → `eval-run.yml` → Run workflow.

**Step 2**: Agent verifies results committed to `evals/results/` by the workflow's auto-commit step.

**Step 3**: Agent scores new cases using the rubric in `docs/evals/llm_quality_eval.md`:
- D1 Structural Compliance (1–5)
- D2 Instruction Adherence (1–5)
- D3 Falsifiability (1–5)
- D4 Relevance (1–5)
- D5 Diversity — CandidateGenerator only (1–5)
- D6 Non-hallucination (1–5)

**Step 4**: Agent updates `evals/results/scores_YYYY-MM-DD.csv` with 6 new rows.

**Step 5**: Agent writes updated summary appended to `docs/evals/llm_quality_run_01.md` or creates `docs/evals/llm_quality_run_02.md`.

**Step 6**: Agent updates `docs/state/engineering.md` with full 12/12 baseline (Observed label). Updates OL-017 to closed in OPEN_LOOPS.md.

**What agent can do now**: Nothing until OL-022 resolves. The 6 remaining cases are in `evals/llm_quality_cases.json` — agent knows the cases; execution is blocked.

**Success condition**: All 12 cases scored; per-module averages updated with Observed label; recommendation confirmed or revised.

**Failure condition A**: New run produces 12/12 api_error again → OL-022 not actually resolved; return to OL-022 resolution.

**Failure condition B**: Any module scores below threshold on new cases (avg < 2.5 = not_ready) → recommendation changes from A to B; product should not be exposed to users until fixed.

**Priority case ordering** (score these first if partial):
1. DF-05 — ALT_DATA hallucination risk (highest risk)
2. CG-02 — STAT_ARB forbidden behavior adherence
3. VP-02 — ML_SIGNAL sensitivity test generation
4. DF-02, DF-03, CG-04 — coverage completion

---

## OL-016 — Mom Test / Customer Validation

**Owner**: Haruki (interviews — cannot be delegated to agent); Agent (logistics, question prep, synthesis)
**Dependency**: None — can start in parallel with OL-022/OL-017
**Required evidence**: ≥3 interview records in `docs/research/mom_test_logs/`, synthesis in `docs/research/mom_test_synthesis_01.md`

### Resolution path

**What agent has already done**: Written the full interview execution plan at `docs/research/mom_test_run_plan.md` — respondent profile, 10 interview questions, note-taking template, synthesis template, OL-016 closure criteria.

**Step 1 (Haruki — now)**: Read `docs/research/mom_test_run_plan.md`. Identify ≥10 candidate respondents matching the profile.

**Step 2 (Agent — on request)**: Draft outreach copy personalized to the respondent list. Haruki must approve before sending.

**Step 3 (Haruki — do not delegate)**: Conduct ≥3 interviews using the 10 questions in `docs/research/mom_test_run_plan.md`. No agent-mediated interviews — The Mom Test explicitly requires unscripted follow-up based on real human judgment.

**Step 4 (Agent — after each interview)**: Transcribe or structure Haruki's notes into the capture format defined in `docs/research/mom_test_run_plan.md`. File at `docs/research/mom_test_logs/interview_NNN.md`.

**Step 5 (Agent — after ≥3 interviews)**: Write synthesis document at `docs/research/mom_test_synthesis_01.md` using the synthesis template. Identify: confirmed pain points, confirmed rejections (with reasons), adjacent needs, ICP clarifications.

**Step 6 (Haruki + Agent)**: Review synthesis. If OL-016 closure criteria met, close OL-016 in OPEN_LOOPS.md with Observed evidence. If not met, identify ≥3 additional respondents and continue.

**What agent can do now**: `docs/research/mom_test_run_plan.md` is already written. Agent can draft outreach copy as soon as Haruki provides a respondent list.

**Success condition**: ≥3 interview records exist; synthesis written; at least one of: confirmed pain point matching product value, confirmed rejection with reason, adjacent need documented. All with Observed label.

**Failure condition**: ≥3 interviews reveal no pain point matching the product's value, and no adjacent need. This is a valid product outcome — it means the ICP hypothesis was wrong. In this case: record the rejection in DECISIONS.md, revise ICP hypothesis, repeat with new respondent profile.

**Time estimate**: Candidate list → outreach → ≥3 interviews: 1–3 weeks depending on response rate.

**Do not**: Generate synthetic interview data, summarize what respondents "might say," or pre-fill synthesis with inferred conclusions. Evidence must be Observed.

---

## D-001 — Minimum Loop Verification

**Owner**: Agent (assessment) / Haruki (decision and DECISIONS.md entry)
**Dependency**: OL-017 closed + OL-019 confirmed + at least 1 customer signal from OL-016
**Required evidence**: Explicit written judgment by Haruki in DECISIONS.md

### What "minimum loop established" means

D-001 defined the goal as "readable daily build/drift/marketing" over "full automation." The minimum loop is established when:

| Criterion | Current status |
|-----------|---------------|
| CI green on main | Met (Observed: CI run 23493826997) |
| Daily report pipeline firing reliably (natural trigger) | Unmet — OL-019 open |
| LLM quality baseline complete (12/12 eval cases) | Partially met — OL-017 partially met |
| At least 1 customer signal (interview finding or explicit rejection) | Unmet — OL-016 open |

### Resolution path

**Step 1**: OL-019 confirms Railway cron natural trigger (agent detects on next UTC 00:00 cycle).

**Step 2**: OL-017 closes (12/12 eval cases, Observed baseline).

**Step 3**: OL-016 produces at least 1 interview record (Observed signal).

**Step 4 (Agent)**: Write a D-001 review document: current state of each criterion, verdict (established / not established), and if established, proposed re-scope statement for DECISIONS.md.

**Step 5 (Haruki)**: Review and record verdict in DECISIONS.md as new entry (D-007 or later). Options:
- "D-001 confirmed achieved — minimum loop established as of [date]. Factory layer precondition C3 met."
- "D-001 not yet achieved — minimum loop not established. Factory layer deferred."

**What agent can do now**: Track OL-019 (check Railway logs at next UTC 00:00 cycle). Nothing else — this decision requires Haruki's explicit judgment.

**Success condition**: Haruki writes an explicit verdict entry in DECISIONS.md.

**Failure condition**: Haruki defers the review indefinitely → agent flags this as a C3 blocker at next session startup.

---

## Dependency Graph

```
OL-022 (API key — Haruki)
    ↓
OL-017 (eval completion — Agent)
    ↓
         ┌─────────────────────────────────────┐
         │  C2: LLM quality baseline (met)     │
         └─────────────────────────────────────┘
                          +
OL-016 (Mom Test — Haruki + Agent)            OL-019 (cron — Agent detect)
    ↓                                              ↓
         ┌─────────────────────────────────────┐
         │  C1: Customer signal (met)           │
         │  C3: D-001 review (Haruki decides)   │
         └─────────────────────────────────────┘
                          ↓
         ┌─────────────────────────────────────┐
         │  C4: Factory namespace design        │
         │  (Agent, after C1–C3 met)            │
         └─────────────────────────────────────┘
                          ↓
              Factory layer architecture
```

The only blocker that can be addressed right now with zero dependencies is OL-016 (Haruki starts building respondent list today, agent starts drafting outreach copy on request). OL-022 is the next most time-sensitive: every day it is unresolved is a day OL-017 cannot close.
