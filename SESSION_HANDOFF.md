# SESSION_HANDOFF.md

**Role**: Startup file for next AI session. Latest only.
**Last updated**: 2026-03-25 (Session 8 — DeepSeek eval complete 12/12 ok; OL-017 + OL-022 closed)

---

**Mode**: Product / Ops — eval baseline established; next priority is OL-016 (Mom Test)

**Branch**: `main` (SHA: f1dfa77)

**Current state**:
- eval-run.yml: working. Secret `DeepSeek_API_KEY` confirmed (length=35). All 12 cases ok.
- `evals/results/run_2026-03-25_rerun0722.jsonl` committed to main (SHA 9570ddf).
- OL-017: CLOSED. 12/12 cases scored. All modules verdict: acceptable.
- OL-022: CLOSED. DeepSeek pipeline working. Correct secret name: `DeepSeek_API_KEY`.
- C2 (factory layer precondition): MET. C1 and C3 remain unmet.

**Eval baseline (Observed, 2026-03-25 — 12/12 cases, provider=deepseek, model=deepseek-chat)**:
| Module | Cases | Avg | Verdict |
|--------|-------|-----|---------|
| DomainFramer | 5/5 | 4.80 | acceptable |
| CandidateGenerator | 4/4 | 4.95 | acceptable |
| ValidationPlanner | 3/3 | 4.93 | acceptable |
- **Recommendation A (unconditional for all archetypes)**: FACTOR, STAT_ARB, HYBRID, ALT_DATA all tested and acceptable.
- DF-05 (ALT_DATA): D6=4, no hallucinations. CG-02 (STAT_ARB): D4=4, acceptable.

**Read First**:
1. `SYSTEM_PRINCIPLES.md`
2. `CURRENT_STATE.md`
3. `OPEN_LOOPS.md` — OL-016 is now highest priority
4. `docs/system/factory_layer_preconditions.md` — C2 MET, C1/C3/C4 unmet

**Unknown**: Railway cron natural trigger (OL-019). Backend tests on current HEAD (last verified 2026-03-18).

**Human Required**:
- **OL-016**: Mom Test — no interviews scheduled, no candidate list exists. Highest remaining blocker.
- Any external outreach
- Factory layer design: blocked until C1 (OL-016) and C3 (D-001 re-scope) are met
