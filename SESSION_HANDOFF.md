# SESSION_HANDOFF.md

**Role**: Startup file for next AI session. Latest only.
**Last updated**: 2026-03-25 (Session 6 — eval run 01 partial, PR pending)

---

**Mode**: Engineering / Eval — Run 01 results ready for PR merge

**Branch**: `feat/eval-run-01-results` (PR open — eval run 01 results + state updates)

**Now**:
1. **Human: merge `feat/eval-run-01-results` PR** (eval run 01 results, OL-017 partial data)
2. **Human: resolve OL-022** — ANTHROPIC_API_KEY credit exhausted. Either:
   - Recharge the `for openhands` key in the `Give Me a DAY` Anthropic workspace, OR
   - Create a new API key → update `ANTHROPIC_API_KEY` in GitHub repository secrets
3. After API key resolved: trigger `eval-run.yml` via workflow_dispatch → completes remaining 6 eval cases (DF-02, DF-03, DF-05, CG-02, CG-04, VP-02)
4. After remaining 6 cases run: agent scores and closes OL-017 with full 12/12 coverage

**Eval Run 01 Results (Observed, 2026-03-25 — 6/12 cases)**:
- DomainFramer (DF-01, DF-04): avg 4.6 — acceptable
- CandidateGenerator (CG-01, CG-03): avg 5.0 — acceptable
- ValidationPlanner (VP-01, VP-03): avg 4.9 — acceptable
- **Recommendation A (conditional)**: Limited human testing permitted on FACTOR archetype goals
- **DO NOT expose ALT_DATA or STAT_ARB goal types** until DF-05 + CG-02 are scored

**Success**: PR merged; OL-022 resolved; `eval-run.yml` triggered and produces 12/12 ok results

**Read First**:
1. `SYSTEM_PRINCIPLES.md`
2. `CURRENT_STATE.md`
3. `OPEN_LOOPS.md` — note OL-022 (new, human-required) and OL-017 (partial)
4. `docs/evals/llm_quality_run_01.md` — run 01 summary
5. `docs/state/engineering.md` — eval results section

**Unknown**: DF-05 (ALT_DATA hallucination), CG-02 (STAT_ARB forbidden behavior), VP-02 (ML_SIGNAL sensitivity test), DF-02, DF-03, CG-04 scores. Railway cron natural trigger unconfirmed (OL-019).

**Human Required**:
- **OL-022**: API key recharge or rotation (blocks 6 eval cases)
- PR merge for `feat/eval-run-01-results`
- Any external outreach (OL-016)
