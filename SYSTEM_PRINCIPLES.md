# SYSTEM_PRINCIPLES.md

**Role**: Highest-priority rule file for the Give Me a DAY repository.
**Truth precedence rank**: 1 (overrides all other files when in conflict)

---

## 1. Two-Layer Mission

### Product Mission
Give Me a DAY exists to help all people construct systems that let them utilize AGI to the maximum extent.

The first product expression of this mission is a validate-then-operate system for investment strategies:
- Receives a natural-language goal
- Internally researches, tests, compares, and rejects candidate strategies
- Presents 2 surviving candidates for human approval
- Operates the approved candidate autonomously under predefined stop conditions

### Operating System Mission
The surrounding management, development, marketing, research, and improvement system exists to:
- perform customer-data analysis, research, and other operating work
- reflect those findings back into the system
- repeat daily improvement
- maintain consistency across the full system

---

## 2. Core Operating Principles

1. AI-optimized structure takes priority over human-oriented prose.
2. Observed, Inferred, and Unknown must be clearly separated.
3. Unknowns must be made explicit rather than silently collapsed into apparent certainty.
4. State may be separated by domain, but top-layer direction must remain unified.
5. The repository must contain enough structured state that an AI can reconstruct the operating context from it.
6. Unsupported claims must never be represented as truth.
7. Legal and high-risk decisions must not be autonomously executed by AI.

---

## 3. Non-Negotiables

The system must not allow or normalize the following:

| # | Prohibition |
|---|------------|
| 1 | AI making decisions with major legal risk |
| 2 | Contentless fabrication included as truth |
| 3 | Top-layer direction splitting across files or agents |
| 4 | Secrets being exposed, copied, reused, or hardcoded without explicit authorization |
| 5 | High-cost external actions executed without human approval |
| 6 | Rollback-dangerous changes merged casually |
| 7 | Unverified external facts treated as current truth |

---

## 4. AI Authority Limits

AI agents may autonomously:
- Read any file in the repository
- Create branches and open PRs
- Run read-only scripts and diagnostics
- Generate drafts and proposals for human review
- Write to `docs/`, `ops/`, `scripts/` and domain state files via PR

AI agents must NOT autonomously:
- Push directly to `main`
- Merge their own PRs
- Create or modify secrets, API keys, or credentials
- Initiate paid service subscriptions or billing changes
- Execute production-external actions (send emails, post to external platforms)
- Run destructive database operations
- Modify `.github/workflows/` without human review

---

## 5. Human Approval Boundaries

The following categories require human approval unless already explicitly authorized:

- Legal-risk actions
- High-cost actions (API spend above daily threshold)
- Production-external actions (emails, social posts, external service calls)
- Destructive actions (deletions, resets, overwrites of production data)
- Anything ambiguous that could materially affect money, legal exposure, user-facing systems, or irreversible state

---

## 6. Truth Precedence

When files conflict, the following precedence order governs:

| Rank | File | Role |
|------|------|------|
| 1 | `SYSTEM_PRINCIPLES.md` | Top-level rules and mission |
| 2 | `DECISIONS.md` | Directional decisions with evidence |
| 3 | `docs/state/*.md` | Domain state (confirmed + unknown) |
| 4 | `docs/reports/daily/YYYY-MM-DD.md` | Daily control, not ultimate truth |
| 5 | `SESSION_HANDOFF.md` | Startup context, session-scoped only |

Lower-ranked files must not contradict higher-ranked files.
If contradiction is discovered, escalate to human review.

---

## 7. Evidence Labels

All state assertions must use one of these labels:

| Label | Meaning |
|-------|---------|
| **Observed** | Directly supported by implementation, logs, files, execution results, or other grounded evidence |
| **Inferred** | Reasoned conclusion derived from evidence, but not directly verified |
| **Unknown** | Currently unresolved, missing evidence, or explicitly unverified |

These labels must not be conflated.
Do not promote Inferred to Observed without new evidence.
Do not collapse Unknown into Inferred for the sake of apparent completeness.

---

## 8. Merge / Deploy Principles

1. Prefer reversible changes.
2. All changes must flow through branch → PR → human merge.
3. Do not represent unverified output as success.
4. High-cost, destructive, or production-external actions require human approval.
5. If evidence is missing, label the state as Unknown rather than silently inferring certainty.
6. One PR = one judgment unit. Do not bundle unrelated changes.
