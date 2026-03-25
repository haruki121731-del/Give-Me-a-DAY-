# OPEN_LOOPS.md

**Role**: Full list of unresolved loops. Optimized for AI execution and closure.
**Last updated**: 2026-03-25 (Session 8 — DeepSeek rerun complete 12/12 ok; OL-017 and OL-022 closed)

---

## AI Control Summary

| Category | Loops |
|----------|-------|
| Highest priority | OL-016 (P1 — customer validation) |
| Human-required | OL-016 (requires real interviews), legal review (see `docs/state/risk.md` R-003) |
| External-blocked | OL-016 (requires real interviews) |
| Direction-risk | OL-016 (PMF unknown — all product direction is unvalidated until resolved) |

---

## Open Loops

---

### OL-022 — CLOSED 2026-03-25
**Title**: Eval provider / key — DeepSeek migration complete; 12/12 cases ok
**Domain**: Engineering / Ops
**Priority**: P1
**Status**: CLOSED
**Closed by**: GitHub Actions run 23529627331 (SHA f1dfa77) on 2026-03-25T07:22Z
**Resolution**:
- Root cause chain: Anthropic credit exhausted → migrated to DeepSeek → secret name mismatches (`deepseekllm` → `DEEPSEEK_API_KEY` → `DeepSeek_API_KEY`) fixed across 3 commits
- Final working config: `ANTHROPIC_API_KEY: ${{ secrets.DeepSeek_API_KEY }}`, `LLM_BASE_URL=https://api.deepseek.com/anthropic`, `LLM_MODEL=deepseek-chat`, `LLM_PROVIDER=deepseek`
- Verify step confirmed: `ANTHROPIC_API_KEY: set (length=35)`
- All 12 eval cases ran successfully. Result committed as `run_2026-03-25_rerun0722.jsonl`

---

### OL-016
**Title**: Mom Test / customer validation
**Domain**: Marketing / Product
**Priority**: P1
**Status**: open
**Owner**: human
**Blocker**: No candidate list, no interview sessions scheduled
**Next Action**: Human creates target interview list; agent drafts outreach copy for review
**Unknowns**: ICP not validated; no user signal; messaging fit unknown
**Related Files**: `docs/state/marketing.md`, `docs/state/product.md`
**Close Condition**: ≥ 3 Mom Test interviews completed; findings recorded in `docs/marketing/logs/`
**Do Not**: Conduct outreach or publish content without human approval

---

### OL-017 — CLOSED 2026-03-25
**Title**: LLM output quality — eval run 01 complete (12/12 cases scored)
**Domain**: Product / Engineering
**Priority**: P1
**Status**: CLOSED
**Closed by**: DeepSeek rerun `run_2026-03-25_rerun0722.jsonl` + agent scoring 2026-03-25
**Final Results (Observed — provider=deepseek, model=deepseek-chat)**:
- DomainFramer: 5/5 cases. Avg 4.80. Verdict: acceptable.
- CandidateGenerator: 4/4 cases. Avg 4.95. Verdict: acceptable.
- ValidationPlanner: 3/3 cases. Avg 4.93. Verdict: acceptable.
- No `not_ready` or `internal_only` verdict on any case.
- DF-05 (ALT_DATA): D6=4, no hallucinations. CG-02 (STAT_ARB): D4=4, acceptable.
**Recommendation revised**: **A (unconditional for FACTOR/STAT_ARB/HYBRID/ALT_DATA archetypes)** — all archetypes tested. Weakest dimension D3 on DF-04 (vague input, justified). System acceptable for internal v1 testing across all archetypes.
**Related Files**: `evals/results/run_2026-03-25_rerun0722.jsonl`, `evals/results/scores_2026-03-25.csv`, `docs/state/engineering.md`

---

### OL-019
**Title**: Railway cron natural trigger confirmation
**Domain**: Ops
**Priority**: P2
**Status**: open
**Owner**: agent (detect) / human (respond)
**Blocker**: Waiting for UTC 00:00 natural trigger on Railway
**Next Action**: Agent checks Railway logs after next UTC 00:00; records exit code and trigger event type in `docs/state/ops.md`
**Unknowns**: Whether Railway cron fires `bash ops/run.sh` correctly; whether exit code is 0 on Railway environment; whether generated report is pushed to repo
**Observed so far**: Last 10 checked `daily-report.yml` GitHub Actions runs show only `push` / `pull_request` event types — no `schedule`-triggered run confirmed. Railway cron configured as `bash ops/run.sh` (not GitHub Actions).
**Related Files**: `docs/state/ops.md`, `ops/run.sh`, Railway dashboard
**Close Condition**: At least 1 natural Railway cron run confirmed with exit code 0 and report file in `docs/reports/daily/`; result recorded with Observed label

---

## Closed Loops (archive)

| ID | Title | Closed | Reason |
|----|-------|--------|--------|
| OL-001 | `pr-build.yml` not created | 2026-03-24 | PR #7 |
| OL-002 | `docs/architecture/current_system.md` missing | 2026-03-24 | PR #8 |
| OL-003 | `docs/agents/ownership.md` / `guardrails.md` missing | 2026-03-24 | PR #9 |
| OL-004 | `docs/reports/daily/_template.md` missing | 2026-03-24 | PR #10 |
| OL-005 | docs/ folder structure missing | 2026-03-24 | PR #6 |
| OL-006 | `scripts/ai/` missing | 2026-03-24 | PRs #6, #11, #12, #13 |
| OL-007 | main 2 commits ahead of origin | 2026-03-24 | PRs #15–#17 |
| OL-008 | 4 unstaged files | 2026-03-24 | Merged into OL-014 |
| OL-009 | LLM live test not run | 2026-03-24 | GitHub Actions Run #3: OpenRouter confirmed |
| OL-010 | OpenHands GitHub Action not configured | 2026-03-24 | Haruki setup complete |
| OL-011 | GitHub Secrets unverified | 2026-03-24 | Run #3: all secrets confirmed |
| OL-012 | Railway cron not configured | 2026-03-24 | Railway cron set to `bash ops/run.sh` |
| OL-013 | Supabase free tier cap | 2026-03-24 | Inactive project deleted; active project confirmed |
| OL-014 | Unpushed commits / unstaged changes on main | 2026-03-24 | PRs #15, #16 |
| OL-015 | OpenHands E2E test | 2026-03-24 | PR #22 merged (Session 4) |
| OL-018 | CI green confirmation on latest HEAD | 2026-03-24 | CI run 23493826997: Frontend Build ✅ + Backend Tests ✅ on feat/state-architecture-v1 tip bdb668fa5 (same app code as main) |
| OL-020 | State architecture + grounding audit (two open PRs) | 2026-03-24 | PR #23 (state arch) + PR #24 (grounding audit) both merged to main |
| OL-021 | LLM eval package — open PR, awaiting merge + first run | 2026-03-25 | PR #25 (eval package), PR #26/#27 (eval runner) merged; first run executed (6/12 Observed); OL-017 continues for remaining 6 |
