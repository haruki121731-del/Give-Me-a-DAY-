# docs/state/engineering.md

**Domain**: Engineering
**Last updated**: 2026-03-24
**Truth precedence rank**: 3

---

## Domain Purpose

Maintain the current engineering implementation state: what is built, where it lives, what is working, and what is unresolved.

---

## Current Confirmed State

**Evidence label**: Observed (from `docs/implementation_status.md`, `docs/architecture/current_system.md`, GitHub Actions CI)

### Stack
| Layer | Technology | Entry Point |
|-------|-----------|-------------|
| Backend | FastAPI 0.104+ / Python 3.11+ / Pydantic v2 | `backend/src/main.py` |
| Frontend | React 18 / TypeScript / Vite / TailwindCSS | `frontend/src/main.tsx` |
| LLM | Anthropic Claude API (claude-sonnet-4-6) | `backend/src/llm/client.py` |
| Persistence | In-memory store + Supabase run_logs | `backend/src/persistence/` |
| CI | GitHub Actions `pr-build.yml` | `.github/workflows/pr-build.yml` |

### Backend pipeline (Observed: tests pass)
```
[1] GoalIntake → [2] DomainFramer → [3] ResearchSpecCompiler
→ [4] CandidateGenerator → [5] EvidencePlanner → [6] ValidationPlanner
→ [7] DataAcquisition → [8] BacktestEngine → [9] StatisticalTests
→ [10] ComparisonEngine → [11] AuditEngine → [12] RecommendationEngine
→ PresentationBuilder
```
All 12 steps implemented through Round 6.12.

### Confirmed working
- Backend pytest: passing (local, pre-Round 6.12)
- Frontend build: `frontend/dist/` exists (past successful build)
- CI: `pr-build.yml` triggers on PR, confirmed active
- LLM client: `claude-sonnet-4-6` confirmed in `backend/src/llm/client.py`
- Companion AI v1: T1–T7 triggers, CON-01–CON-06 contradiction detection implemented

### Code-truth locations
| Component | Location |
|-----------|----------|
| Domain models | `backend/src/domain/models.py` |
| Pipeline modules | `backend/src/pipeline/` |
| Execution modules | `backend/src/execution/` |
| Judgment / Audit | `backend/src/judgment/` |
| LLM client + prompts | `backend/src/llm/` |
| Frontend pages | `frontend/src/pages/` |
| Tests | `backend/tests/` |

---

## Current Unknowns

| Unknown | Notes |
|---------|-------|
| CI green/red on latest main | No confirmed recent CI run result in state files |
| Live deployment | No production server confirmed. Railway used for ops cron only |
| Backend tests on latest HEAD | `implementation_status.md` last updated 2026-03-18 |
| Frontend tests | No frontend test suite confirmed |
| Real LLM calls in pipeline | Tests use mocks/fallbacks; live LLM quality not validated end-to-end |
| Supabase schema for run_state | `run_state_schema.sql` exists; live migration status unknown |

---

## Related Open Loops

- OL-017: LLM output quality verification — real runs not yet tested
- OL-018: CI status on latest HEAD

---

## Risks

| Risk | Level | Notes |
|------|-------|-------|
| Backend test regression | Medium | Last verified 2026-03-18; changes since then not re-verified |
| No production deployment | High | Product has no live users |
| LLM API cost at scale | Medium | claude-sonnet-4-6 per-call cost in full pipeline runs |

---

## Architecture Constraints

- Main branch is protected: all changes via PR
- No direct main push by AI agents
- One PR = one judgment unit
- Secrets never hardcoded

## Read Next

- `docs/architecture/current_system.md` — detailed architecture overview
- `docs/architecture/module_map.md` — module responsibility map
- `docs/implementation_status.md` — full round-by-round status
