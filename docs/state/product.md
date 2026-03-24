# docs/state/product.md

**Domain**: Product
**Last updated**: 2026-03-24
**Truth precedence rank**: 3

---

## Domain Purpose

Bridge the product vision and specification into a continuously updated, AI-readable state file.
This file answers: what does the product currently do, what is in scope, what is out of scope, and what remains unresolved.

---

## Current Confirmed State

**Evidence label**: Observed (from `docs/product/product_definition.md`, `docs/product/v1_boundary.md`, `docs/system/core_loop.md`, `docs/implementation_status.md`)

### Product identity
- Give Me a DAY is a validate-then-operate system for investment strategies (v1 wedge)
- Core value: comparison, validation, rejection, and conditional recommendation for high-complexity systems
- The product does not generate generic code or plans; it generates validated, operable direction

### v1 scope (confirmed in spec)
- Internal 12-step pipeline: Goal → Frame → Spec → Candidates → Evidence → Validation → Audit → Recommend → Present → Approve → Operate → Re-evaluate
- User-facing: single goal input screen, loading screen, 2-candidate presentation, approval gate, Paper Run status card, monthly report, quarterly re-evaluation
- Paper Run: simulated only, no real money
- Data sources: public daily OHLCV, FRED macro indicators, CFTC COT, index constituents

### Implementation status
- Rounds 1–6.12 complete: backend 12-step pipeline implemented, tested, and passing
- Frontend: 5-page React app implemented
- No live deployment confirmed (Observed: `docs/implementation_status.md`)

### Key product non-negotiables (from CLAUDE.md)
- No recommendation without critique
- No candidate without exposed assumptions
- No validation plan without failure conditions
- Rejection is a feature, not a failure state

---

## Current Unknowns

| Unknown | Notes |
|---------|-------|
| Live user validation | No Mom Test interviews conducted. No PMF signal. |
| Real API integrations | yfinance + synthetic fallback used; live data quality at scale not tested |
| Deployment environment | No confirmed production deployment; Railway setup only for ops/run.sh cron |
| LLM output quality at scale | Pipeline runs in tests; real-world LLM output quality for DomainFramer/CandidateGenerator not validated with real users |
| Product-market fit | Unknown — v1 is pre-user |

---

## Related Open Loops

- OL-016: Live customer validation (Mom Test) — not started
- OL-017: LLM output quality verification (GoalIntake → DomainFramer real runs)

---

## Risks

| Risk | Level | Notes |
|------|-------|-------|
| v1 scope creep | Medium | Generic workflow automation pressure exists per CLAUDE.md |
| LLM dependency for pipeline quality | High | If LLM output degrades, the full pipeline quality degrades |
| Investment domain regulatory exposure | High | Any real-money operation requires legal review |
| No live users yet | High | PMF entirely unconfirmed |

---

## Related Decisions

- D-001: 2-week goal locked to "minimum loop establishment," not full automation
- D-002: OpenHands deferred until repo truth layer established

## Read Next

- `docs/product/product_definition.md` — full product definition
- `docs/product/v1_boundary.md` — v1 scope contract
- `docs/system/core_loop.md` — 12-step internal loop spec
