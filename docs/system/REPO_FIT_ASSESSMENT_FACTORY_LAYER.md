# REPO_FIT_ASSESSMENT_FACTORY_LAYER.md

**Purpose**: Assess whether this repo should later add a PRD-driven autonomous factory layer.
**Date**: 2026-03-25
**Author**: Agent (Session 8)
**Supersedes**: `docs/system/REPO_FIT_ASSESSMENT.md` (Session 6 — written when OL-017 was 6/12 partial; now 12/12 closed)
**Input files read**:
- CLAUDE.md, CURRENT_STATE.md, SESSION_HANDOFF.md, OPEN_LOOPS.md, DECISIONS.md
- docs/system/core_loop.md, docs/system/technical_design.md, docs/system/execution_layer.md, docs/system/internal_schema.md, docs/system/factory_layer_preconditions.md, docs/system/REPO_FIT_ASSESSMENT.md
- docs/state/product.md, docs/state/engineering.md, docs/state/ops.md
- docs/implementation_status.md

---

## 1. Repo Identification

| Field | Value |
|-------|-------|
| Repo name | `Give-Me-a-DAY-` |
| Owner | `haruki121731-del` |
| Remote URL | `github.com/haruki121731-del/Give-Me-a-DAY-` |
| Branch assessed | `main` (SHA `0964936`) |
| Key identity files present | `CLAUDE.md` ✓, `CURRENT_STATE.md` ✓, `SESSION_HANDOFF.md` ✓, `OPEN_LOOPS.md` ✓ |

**Confidence: HIGH.** Repo identity confirmed by remote URL, top-level structure (`backend/`, `frontend/`, `evals/`, `ops/`, `CLAUDE.md`, `SYSTEM_PRINCIPLES.md`), and git log matching session history. This is not a greenfield repo and not a different project.

---

## 2. Existing Repo Identity

**Source**: CLAUDE.md (rank 1), SYSTEM_PRINCIPLES.md (rank 1), docs/state/product.md (rank 3)

Give Me a DAY is a **validation-first product for investment strategy research**. Its primary identity as of this assessment:

- Accepts a natural-language investment goal from a user
- Internally runs a 12-step pipeline: Goal → Frame → Spec → Candidates → Evidence → Validation → Audit → Recommend → Present → Approve → Operate → Re-evaluate
- Returns a conditionally recommended strategy direction with explicit rejection logic and assumption exposure
- Operates the approved strategy as a Paper Run (simulated, no real money — D-005)

The product's defining value — per CLAUDE.md — is **comparison, rejection, and conditional recommendation under explicit uncertainty**. It is not code generation, not generic AI workflow automation, not a productivity tool.

CLAUDE.md contains explicit pushback rules against drifting into:
- generic workflow automation
- "build anything and market anything" framing
- one-click production orchestration
- universal deployment infrastructure

Current maturity (Observed + Inferred from repo):
- Backend 12-step pipeline: Rounds 1–6.12 implemented (Inferred: last verified 2026-03-18)
- LLM eval baseline: 12/12 cases scored, all modules acceptable (Observed: 2026-03-25)
- Frontend: 5-page React app implemented (Inferred: no re-run post-Round 6.12)
- Live users: **zero** (Observed)
- Customer validation: **zero interviews** (Observed: OL-016 open, not started)
- Production deployment: **none confirmed** (Unknown)
- Railway cron natural trigger: **unconfirmed** (Unknown: OL-019 open)

---

## 3. Existing Relevant Systems

The following repo systems are relevant to the proposed factory-layer idea:

| System | Location | Relevance to Factory Layer |
|--------|----------|---------------------------|
| 12-step backend pipeline | `backend/src/pipeline/`, `backend/src/execution/` | Factory dev-coordination must not touch this |
| LLM eval framework | `evals/`, `scripts/eval_runner.py`, `.github/workflows/eval-run.yml` | Factory QA module would be a peer, not a replacement |
| Daily report pipeline | `ops/run.sh`, `.github/workflows/daily-report.yml` | Factory orchestration would extend ops, not replace it |
| OpenHands issue→PR loop | `.github/workflows/openhands.yml` | Closest existing analogue to dev-coordination automation |
| State/truth architecture | `SYSTEM_PRINCIPLES.md`, `DECISIONS.md`, `docs/state/*.md` | Factory state must integrate with this, not bypass it |
| factory_layer_preconditions.md | `docs/system/factory_layer_preconditions.md` | Already tracks the 4 conditions; this file extends that analysis |
| CI (`pr-build.yml`) | `.github/workflows/pr-build.yml` | Factory QA depends on this being stable |

The `openhands.yml` workflow (Issue → Claude API → PR creation) is the most structurally adjacent existing system. It demonstrates that this repo already has one layer of AI-driven dev coordination. The proposed factory layer would be a structured extension of that pattern — not a novel concept.

The LLM eval framework (`eval_runner.py`, rubric, 12 cases) evaluates **product output quality**. A factory layer's QA module would evaluate **build pipeline quality**. These are distinct concerns that must remain namespaced separately.

---

## 4. Fit Analysis

### Where it aligns

| Alignment point | Repo evidence |
|----------------|---------------|
| Repo already has AI-driven dev coordination | `openhands.yml` — Issue → PR loop confirmed E2E (Session 4) |
| Repo already has eval infrastructure | `evals/`, `scripts/eval_runner.py`, 12-case rubric |
| Repo already has state architecture for AI agents | `SYSTEM_PRINCIPLES.md` truth hierarchy, `docs/state/*.md` |
| Product thesis supports meta-layer eventually | CLAUDE.md: "convert AI intelligence into real-world successful outcomes, then improve future outcomes by learning from validation and runtime feedback" |
| Factory concept was already evaluated and preconditioned | `docs/system/REPO_FIT_ASSESSMENT.md` (Session 6) + `docs/system/factory_layer_preconditions.md` |

The factory layer concept is **not alien to this repo**. The repo was explicitly assessed for it in Session 6. Preconditions were written. The concept was judged viable-later, not rejected-never.

### Where it does not align (currently)

| Misalignment point | Repo evidence |
|-------------------|---------------|
| Product is pre-user and pre-PMF | OL-016 open, zero interviews, zero live users (Observed) |
| v1_boundary excludes adjacent capabilities | CLAUDE.md explicitly rejects "one-click production orchestration" and "universal deployment infrastructure" |
| D-001 not yet re-scoped | DECISIONS.md: "2-week goal locked to minimum loop establishment" — not yet confirmed achieved or re-scoped |
| Ops baseline not fully stable | Railway cron natural trigger OL-019 unconfirmed; ops/run.sh has one confirmed live run |
| Factory adds state without confirmed placement | Truth hierarchy has no assigned rank for factory state |

---

## 5. Collision Analysis

### Collision 1: Product identity (HIGH)
A GTM coordination module — one of the factory layer's proposed components — generates marketing artifacts, outreach copy, and external messaging. CLAUDE.md has an explicit pushback rule against "generic workflow automation" and "build anything and market anything" framing. If the factory layer's GTM module is scoped broadly (not constrained to investment-validation-domain-specific outputs), it repositions the repo.

**Evidence**: CLAUDE.md §Pushback Rules — "Do not drift into generic workflow automation. Even if it sounds commercially broader, it weakens the wedge."

**Mitigation condition**: GTM module must be scoped exclusively to "generate marketing artifacts specific to a validated Give Me a DAY recommendation package." Not "generate marketing for any PRD."

### Collision 2: Scope boundary (HIGH)
`docs/product/v1_boundary.md` (referenced in CLAUDE.md and DECISIONS.md D-005) explicitly excludes "one-click production orchestration" and "universal deployment infrastructure." A factory layer coordinating dev + eval + GTM is structurally close to both.

**Evidence**: CLAUDE.md §Explicitly Out of Scope for v1 — "one-click production orchestration," "universal deployment infrastructure."

**Mitigation condition**: Factory layer must not be framed as production orchestration. It must be scoped as "PRD-intake → structured coordination → handoff" with human approval gates at each stage (consistent with D-003).

### Collision 3: Validation-order inversion (HIGH)
A factory layer automates the build and GTM process for a product. The product currently has zero customer validation signal. Building automation to ship faster is premature when what to ship is unvalidated.

**Evidence**: OL-016 open (zero Mom Test interviews), CURRENT_STATE.md top blockers, DECISIONS.md D-001.

**Mitigation condition**: OL-016 must close (≥3 Mom Test interviews with findings recorded) before any factory GTM module design begins. This is C1 in `factory_layer_preconditions.md`.

### Collision 4: State truth contamination (MEDIUM)
The factory layer introduces new operational state: PRD versions, factory run history, dev sprint status, GTM campaign tracking. The existing truth hierarchy (SYSTEM_PRINCIPLES rank 1 → DECISIONS rank 2 → state files rank 3 → daily reports rank 4 → SESSION_HANDOFF rank 5) has no assigned slot for factory state. Unranked state creates conflicting truth sources for AI agents.

**Evidence**: SYSTEM_PRINCIPLES.md §2 Core Operating Principles — "State may be separated by domain, but top-layer direction must remain unified."

**Mitigation condition**: Factory state must be assigned a truth precedence rank and documented in SYSTEM_PRINCIPLES.md before any factory state files are created. Inferred appropriate rank: 3.5 (below product state files, above daily reports).

### Collision 5: Ops maturity (MEDIUM)
The current ops layer has one confirmed live run. Railway cron natural trigger is unconfirmed (OL-019). Adding factory orchestration on top of an unreliable ops baseline multiplies failure modes.

**Evidence**: docs/state/ops.md — "Natural trigger status: Unknown — no schedule-triggered run confirmed yet (OL-019)." docs/state/engineering.md — DeepSeek eval pipeline required three secret-name correction commits before succeeding.

**Mitigation condition**: OL-019 (Railway cron natural trigger) must close, and eval pipeline must demonstrate ≥2 consecutive successful runs, before factory orchestration is layered on top.

---

## 6. Preconditions

From `docs/system/factory_layer_preconditions.md` — updated to reflect current state:

| ID | Condition | Current Status | Evidence |
|----|-----------|---------------|---------|
| C1 | OL-016 closed — ≥3 Mom Test interviews completed, findings recorded | **UNMET** | OL-016 open, zero interviews scheduled (Observed) |
| C2 | OL-017 closed — all 12 eval cases scored, stable LLM quality baseline | **MET** | 12/12 cases scored 2026-03-25, all modules acceptable (Observed) |
| C3 | D-001 "minimum loop establishment" goal confirmed achieved and explicitly re-scoped by Haruki | **UNMET** | D-001 still active in DECISIONS.md; no closure or re-scope recorded |
| C4 | Factory files designed in isolated namespace without touching product scope | **UNMET** | No factory design work started |

**Net status**: 1 of 4 preconditions met. Not sufficient to proceed to architecture design.

**Additional conditions identified in this assessment** (beyond factory_layer_preconditions.md):

| ID | Condition | Current Status |
|----|-----------|---------------|
| C5 | OL-019 closed — Railway cron natural trigger confirmed | UNMET |
| C6 | Factory state assigned truth precedence rank in SYSTEM_PRINCIPLES.md | UNMET |
| C7 | Eval pipeline demonstrates ≥2 consecutive successful runs post-DeepSeek migration | UNMET (1 run confirmed: 2026-03-25 rerun0722) |

---

## 7. Timing Judgment

**Judgment: Add later with explicit preconditions.**

This is unchanged from `REPO_FIT_ASSESSMENT.md` (Session 6), confirmed with updated evidence.

**Why not now:**

1. **C1 is unmet and is a people problem, not a system problem.** OL-016 (customer validation) has zero progress. A factory layer that automates shipping a pre-PMF product automates shipping the wrong thing faster. The repo's own CLAUDE.md makes this explicit: the product must convert intelligence into "real-world successful outcomes" — which requires first knowing what outcomes users actually want.

2. **D-001 is not re-scoped.** The 2-week goal is "minimum loop establishment." Factory-layer design is not minimum. Until D-001 is explicitly closed and re-scoped by Haruki, adding a factory layer contradicts the active strategic decision in DECISIONS.md.

3. **Ops baseline is still maturing.** The eval pipeline required 5+ debugging cycles across multiple sessions to produce one clean run. Railway cron natural trigger is unconfirmed. The ops layer is not yet stable enough to serve as the foundation for factory orchestration.

**Why not never:**

1. The concept fits the product's deeper thesis (CLAUDE.md: "improve future outcomes by learning from validation and runtime feedback").
2. Structural attachment points exist (`openhands.yml` as precedent, `evals/` as existing eval infrastructure, `docs/state/` as state architecture).
3. Session 6 already wrote explicit preconditions and judged it viable-later — this assessment confirms that judgment with updated evidence.

**What changed since Session 6:**

- C2 is now MET (OL-017 closed, 12/12 eval cases scored). This removes one blocker.
- C1, C3, C4, C5, C6, C7 remain unmet.
- Net: timing judgment is unchanged. Closer than Session 6 (1/4 core preconditions met vs 0/4), but not ready.

---

## 8. Structural Placement If Added Later

Only if all preconditions (C1–C7) are met. This section describes conceptual placement only — not design.

**What must be isolated:**

The factory layer must live in a dedicated namespace that does not modify existing product directories. Proposed conceptual structure (not a design spec):

```
factory/              ← new top-level directory (isolated namespace)
  prd/                ← PRD documents (trigger input)
  state/              ← factory operational state (truth rank: 3.5)
  workflows/          ← factory-specific GitHub Actions (separate from product CI)
  scripts/            ← factory orchestration scripts (separate from ops/run.sh)
  docs/               ← factory design docs (separate from docs/system/)
```

**What must NOT be shared without explicit namespacing:**

- `ops/run.sh` — product ops, not factory ops
- `evals/` — product eval, not factory QA
- `.github/workflows/pr-build.yml` — product CI, not factory CI
- `docs/state/*.md` — product state, not factory state
- `backend/`, `frontend/` — untouched by factory layer

**Dependency direction (if added):**

Factory layer depends on product layer, not the reverse. Factory QA checks that product pipeline is green. Product pipeline does not know factory exists.

---

## 9. Non-Negotiables

These must not change even if the factory layer is eventually added. All grounded in rank-1 or rank-2 files.

| Item | Source | Reason |
|------|--------|--------|
| CLAUDE.md product identity | CLAUDE.md (rank 1 context) | Defines what the repo is and is not. Must not be broadened to accommodate factory scope. |
| 12-step core loop | `docs/system/core_loop.md` | Factory coordination must not modify product pipeline behavior. |
| Internal schema objects | `docs/system/internal_schema.md` | Factory must not add objects to product schema. |
| v1 scope boundary | CLAUDE.md §Explicitly Out of Scope for v1 | "One-click production orchestration" remains excluded. Factory layer is only viable if scoped differently from this. |
| D-003 (no direct main push) | DECISIONS.md | All factory automation changes must go through branch/PR with human merge judgment. |
| D-004 (no secret values) | DECISIONS.md | Factory layer must not handle secrets differently. |
| State truth hierarchy | SYSTEM_PRINCIPLES.md | Factory state must be assigned a rank and documented before creation, not after. |
| CLAUDE.md non-negotiables | CLAUDE.md §Product Non-Negotiables | No recommendation without critique, no candidate without assumptions, no validation plan without failure conditions — factory QA must enforce these, not dilute them. |
| Human approval boundaries | SYSTEM_PRINCIPLES.md §5 | Legal-risk actions, external communications, billing changes, and production execution remain human-only. Factory automation must not cross these. |

---

## 10. Final Recommendation

**Add later. Not now. Not never.**

This repository should eventually add a PRD-driven autonomous factory layer, but only after the following conditions are satisfied:

1. **OL-016 closed** (C1): ≥3 Mom Test interviews completed with recorded findings. This is the single most important precondition. No factory layer should be designed before customer validation confirms what the product is for and who it is for.

2. **D-001 re-scoped** (C3): Haruki explicitly closes the "minimum loop establishment" phase and re-states the next strategic goal. A factory layer design is premature until the current phase is declared done.

3. **Ops baseline stable** (C5, C7): OL-019 (Railway cron) closed, and eval pipeline demonstrates ≥2 consecutive successful runs after DeepSeek migration.

4. **Factory state ranked** (C6): Truth precedence rank assigned in SYSTEM_PRINCIPLES.md before any factory state file is created.

5. **Isolated namespace confirmed** (C4): Factory design committed to an isolated `factory/` namespace. No factory files in `backend/`, `frontend/`, `evals/`, `ops/`, or `docs/system/` without explicit boundary documentation.

**C2 is the only precondition currently met** (OL-017 closed, 12/12 eval cases scored 2026-03-25). Progress was made. But 1/4 core preconditions met is not sufficient to begin architecture design.

**The correct next action is not factory-layer work.** It is:
- Haruki: OL-016 (Mom Test) — highest remaining blocker, blocks everything
- Haruki + Agent: Confirm D-001 closure when minimum loop is demonstrably established
- Agent: Monitor eval pipeline for second consecutive successful run (C7)

The factory layer is the right idea for this repo at the right stage. That stage is not now.
