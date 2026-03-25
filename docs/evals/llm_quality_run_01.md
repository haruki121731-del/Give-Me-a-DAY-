# LLM Quality Eval — Run 01

**Date**: 2026-03-25
**Model tested**: claude-sonnet-4-6 (production pipeline model)
**Eval framework version**: 1.0
**Rubric reference**: `docs/evals/llm_quality_eval.md`
**Cases source**: `evals/llm_quality_cases.json`
**OL-017 ref**: This is the first execution pass. OL-021 phase 1 closes here.

---

## Execution Status

| Metric | Value |
|--------|-------|
| Cases defined | 12 |
| Cases run | 6 (50%) |
| Cases not run (API error) | 6 (50%) |
| Run method | In-context generation, claude-sonnet-4-6 via Cowork session |
| Intended method | GitHub Actions eval-run.yml with claude-3-haiku-20240307 |
| Blocker | `ANTHROPIC_API_KEY` in GitHub Secrets — credit balance exhausted (400 error) |

### Coverage by module

| Module | Defined | Run | Not Run |
|--------|---------|-----|---------|
| DomainFramer | 5 | 2 (DF-01, DF-04) | 3 (DF-02, DF-03, DF-05) |
| CandidateGenerator | 4 | 2 (CG-01, CG-03) | 2 (CG-02, CG-04) |
| ValidationPlanner | 3 | 2 (VP-01, VP-03) | 1 (VP-02) |

**Note on execution context**: The 6 run cases were generated in-context using claude-sonnet-4-6, the production pipeline model. This differs from the intended eval model (claude-3-haiku-20240307) in capability but tests the actual model used in production. Results are labelled accordingly. The 6 unrun cases will be executed when the API key is recharged/rotated.

---

## Module-Level Score Summary

Rubric: 1–5 per dimension. Average ≥ 4.0 = acceptable. Any dimension ≤ 2 = not_ready.

### DomainFramer (2 cases run)

| Case | D1 | D2 | D3 | D4 | D6 | Avg | Verdict |
|------|----|----|----|----|-----|-----|---------|
| DF-01 (normal factor) | 5 | 5 | 4 | 5 | 5 | 4.8 | acceptable |
| DF-04 (vague input) | 5 | 5 | 3 | 4 | 5 | 4.4 | acceptable |
| **Module avg** | | | | | | **4.6** | **acceptable** |

**Key findings**:
- Structural compliance: perfect across both cases
- Falsifiability (D3): strong on specific inputs (DF-01: numeric thresholds throughout); drops to 3 on vague inputs where the constraint is justified
- Non-hallucination (D6): Jegadeesh & Titman 1993, AQR momentum, Asness et al. 2013, and SPIVA statistics are all real and accurately described. No fabrications detected.
- Relevance (D4): correctly uses UNCLASSIFIED for vague input rather than forcing a specific archetype

**Unrun cases gap**: DF-02 (stat arb), DF-03 (hybrid), DF-05 (ALT_DATA hallucination risk) — the highest hallucination-risk case is in the unrun set.

---

### CandidateGenerator (2 cases run)

| Case | D1 | D2 | D4 | D5 | D6 | Avg | Verdict |
|------|----|----|----|----|-----|-----|---------|
| CG-01 (normal FACTOR) | 5 | 5 | 5 | 5 | 5 | 5.0 | acceptable |
| CG-03 (rejection constraint) | 5 | 5 | 5 | 5 | 5 | 5.0 | acceptable |
| **Module avg** | | | | | | **5.0** | **acceptable** |

**Key findings**:
- Diversity (D5): consistently strong — the 3 candidate types are genuinely architecturally different across both cases. Specifically: CG-01 delivers a pure price sort vs risk-adjusted signal vs multi-factor composite. Not just different parameter values.
- Constraint adherence (D2): CG-03 correctly rejected the '12-month return sort' in all 3 candidates and produced genuinely alternative approaches (earnings momentum, price reversal hybrid, ML).
- Known risks: specific and non-generic across all candidates — named concrete failure modes (モメンタムクラッシュ, small-cap liquidity, earnings data lag) rather than boilerplate.
- assumption.failure_impact: populated and non-circular for all candidates.

**Unrun cases gap**: CG-02 (STAT_ARB with forbidden behaviors), CG-04 (MACRO with free-data constraint) — the constraint-adherence cases for non-FACTOR archetypes are not yet covered.

---

### ValidationPlanner (2 cases run)

| Case | D1 | D2 | D3 | Avg | Verdict |
|------|----|----|-----|-----|---------|
| VP-01 (normal FACTOR) | 5 | 5 | 5 | 5.0 | acceptable |
| VP-03 (blocking gap) | 5 | 5 | 4 | 4.8 | acceptable |
| **Module avg** | | | | **4.9** | **acceptable** |

**Key findings**:
- VP-01 is the strongest output of the entire run. All 4 required tests present. Every failure_condition contains a numeric threshold or explicit statistical criterion (Sharpe < 0.5, t < 1.65, drawdown > 40%, consecutive windows failing, etc.).
- VP-03 correctly handles blocking gap: every test method_summary acknowledges the data availability constraint. ABORT conditions are explicit. Sensitivity test correctly added (required for high validation_burden).
- Minor D3 gap on VP-03: T-04 regime split failure conditions reference sample sizes rather than performance thresholds — borderline measurable but acceptable.

**Unrun cases gap**: VP-02 (ML_SIGNAL high burden) — whether sensitivity test is correctly generated for this specific scenario is not yet confirmed.

---

## Biggest Failure Modes Observed

None of the 6 run cases produced a `not_ready` or `internal_only` verdict. This is a positive result.

The primary risks that were **not tested** due to API key exhaustion:
1. **DF-05** (ALT_DATA hallucination risk): this is the highest-risk case for hallucinated dataset names, Sharpe ratios, and cited research outcomes. It remains Unknown.
2. **CG-02** (STAT_ARB with forbidden overnight positions): constraint adherence on non-FACTOR archetypes is not yet confirmed.
3. **VP-02** (ML_SIGNAL validation): whether sensitivity test is generated for ML-specific risks is not yet tested.

---

## Assessment Against Rubric Thresholds

| Threshold | Criterion | Status |
|-----------|-----------|--------|
| not_ready | Any dimension ≤ 2 | Not triggered on any run case |
| internal_only | Any avg 2.5–3.9 | Not triggered |
| acceptable | All dims ≥ 3, avg ≥ 4.0 | ✅ All 6 run cases qualify |
| ready | All dims ≥ 4, avg ≥ 4.5 | ✅ 5 of 6 run cases qualify (DF-04 = 4.4, borderline) |

---

## Is Current Quality Acceptable for Limited Human Testing?

**Yes, with conditions — for the 3 tested scenarios (normal FACTOR inputs, rejection constraints, blocking gap handling).**

Conditions:
1. The ANTHROPIC_API_KEY credit exhaustion must be resolved and the remaining 6 cases must be run — particularly DF-05 (ALT_DATA hallucination) and CG-02 (STAT_ARB forbidden behavior check)
2. Limited testing should be scoped to investment goals that resemble DF-01 (FACTOR strategy, specific goal, clear success definition) — the archetype and input type where quality is confirmed
3. Vague user inputs (DF-04 type) produce lower D3 scores — acceptable but the validation plan will be less specific; user should be warned
4. ALT_DATA and STAT_ARB goals should not be exposed until DF-05 and CG-02 are tested

---

## Human-Required Action

**ANTHROPIC_API_KEY in GitHub Secrets is exhausted. Haruki must:**
1. Recharge the `for openhands` key in the `Give Me a DAY` Anthropic workspace, OR
2. Create a new API key and update `ANTHROPIC_API_KEY` in GitHub repository secrets
3. After resolving: trigger `eval-run.yml` via workflow_dispatch — it will auto-commit results to `evals/results/`

**The remaining 6 cases will then run automatically.** Results will appear in `evals/results/run_YYYY-MM-DD.jsonl`.

---

## Raw data

- `evals/results/run_2026-03-25.jsonl` — 6 ok records + 6 api_error records
- `evals/results/scores_2026-03-25.csv` — scores for 6 run cases

---

## Next eval run priority (after API key fix)

1. DF-05 (ALT_DATA hallucination) — highest risk
2. CG-02 (STAT_ARB forbidden behavior adherence)
3. VP-02 (ML_SIGNAL sensitivity test generation)
4. DF-02, DF-03, CG-04 — complete the coverage
