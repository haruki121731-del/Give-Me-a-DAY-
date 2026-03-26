# Layer 0 — Synthesis Framework

**Purpose**: Turn 3–5 Mom Test interviews into decisions the repo can act on.
**Date**: 2026-03-26
**Related**: `mom_test_run_plan.md`, `layer0_interview_flow.md`, OL-016

---

## When to Run Synthesis

Run synthesis after ≥3 completed interviews. Do not synthesize after 1 or 2 — patterns require multiple data points. Do not wait for 6+ — synthesis after 3 is faster and more useful than synthesis after 8.

Output file: `docs/research/mom_test_synthesis_01.md`

---

## Step 1: Note Normalization

Before looking for patterns, normalize raw interview notes into a consistent format. For each interview, extract:

```
Interview: NNN
Respondent type: [primary / secondary]

1. Pre-validation process
   - Has one? [Yes / Ad hoc / No]
   - Description: [1–3 sentences]
   - Evidence label: [Observed / Inferred / Unknown]

2. Pain confirmation
   - Confirmed wasted effort on fragile direction? [Yes / No / Partial]
   - Supporting quote (verbatim if possible):
   - Evidence label: [Observed / Inferred / Unknown]

3. Comparison behavior
   - Compares multiple directions? [Yes / Sometimes / No]
   - How they compare: [1–2 sentences]
   - Evidence label: [Observed / Inferred / Unknown]

4. Top wasted effort (Q9 answer)
   - Their answer: [verbatim or close paraphrase]
   - Is early direction evaluation the top pain? [Yes / No / Other ranked higher: ___]

5. Current substitutes
   - What they use today: [list]
   - Evidence label: [Observed / Inferred / Unknown]

6. Surprises / contradictions
   - [Anything unexpected]
```

Complete this for each interview before moving to pattern extraction.

---

## Step 2: Pattern Extraction

After normalizing all notes, look for agreement and disagreement across respondents.

### Signal scoring table

Fill in one row per finding, one column per interview:

| Finding | Interview 001 | Interview 002 | Interview 003 | Interview 004 | Interview 005 | Signal strength |
|---------|--------------|--------------|--------------|--------------|--------------|----------------|
| Has a pre-validation process | | | | | | N/5 |
| Confirmed wasted effort on fragile direction | | | | | | N/5 |
| Compares multiple directions | | | | | | N/5 |
| Evaluation is top wasted effort | | | | | | N/5 |
| Current substitute is "own judgment / nothing systematic" | | | | | | N/5 |

Use: ✓ (confirmed, Observed), ~ (partial or Inferred), ✗ (contradicted or absent), ? (not asked or Unknown)

**Signal strength interpretation**:
- 4–5/5 ✓: Strong signal. High confidence. Can inform product decisions.
- 3/5 ✓: Moderate signal. Worth noting. Not sufficient alone.
- 2/5 ✓: Weak signal. Do not rely on. May need more interviews.
- 0–1/5 ✓: Absent or contradicted. Treat as rejection signal for this finding.

---

## Step 3: Pain Signal Ranking

After the signal scoring table, rank the pains mentioned by frequency and intensity:

| Pain | Mentioned by N respondents | Evidence label | Intensity (High/Medium/Low — based on their language) |
|------|---------------------------|---------------|------------------------------------------------------|
| [e.g., Wasted time on fragile directions] | N/N | Observed | |
| [e.g., Difficulty knowing when to stop] | N/N | Observed | |
| [e.g., Data quality problems] | N/N | Observed | |
| [e.g., Comparison is hard] | N/N | Observed | |

**High intensity signal**: Respondent used strong language ("months wasted," "cost me real money," "still bothers me"), gave a specific story, or returned to this topic unprompted.

**Medium intensity**: Mentioned the pain, had an example, but it was not the first thing that came to mind.

**Low intensity**: Acknowledged the pain when asked, but described it as minor or manageable.

---

## Step 4: Evidence vs. Assumption Separation

After pattern extraction, separate what is confirmed from what remains assumed.

### Evidence table

| Item | Type | Evidence label | Source interviews |
|------|------|---------------|-------------------|
| [specific finding] | Pain / Behavior / Substitute / Rejection | Observed / Inferred / Unknown | NNN, NNN |

Rules:
- **Observed**: Respondent explicitly stated this happened to them, or described a behavior they personally do. Verbatim or near-verbatim quote exists.
- **Inferred**: Agent or interviewer interpretation of what the respondent meant. Must be labeled clearly. Do not treat as Observed.
- **Unknown**: The question was not asked, the respondent was ambiguous, or the topic did not come up.

No item may be promoted from Inferred to Observed without re-reading the original interview notes to confirm a direct statement exists.

### Remaining assumptions (after interviews)

List what is still assumed, not confirmed:

| Assumption | Still held? | What would confirm or reject it |
|------------|-------------|--------------------------------|
| The pain is severe enough to motivate behavior change | Unknown | Would need price/willingness-to-pay signal (premature in Layer 0) |
| Individual quant traders are the right ICP | Partially confirmed / Rejected / Confirmed | |
| Multi-candidate comparison maps to real behavior | | |
| The pre-validation step is the gap, not the backtest | | |

---

## Step 5: Contradiction Tracking

If interviews produced contradictory findings, record them explicitly. Do not smooth over contradictions by averaging.

| Contradiction | Interview A says | Interview B says | How to interpret |
|---------------|-----------------|-----------------|-----------------|
| [e.g., Pre-validation process] | "I always evaluate before committing" | "I just backtest immediately, no pre-step" | Possible ICP segmentation issue — different respondent types? |

Contradictions are informative. They may indicate:
- The ICP is not homogeneous (sub-profiles exist with different behaviors)
- The question was asked differently and produced different answers
- The pain exists for some practitioners but not others

Do not collapse contradictions into a single narrative. Record them and let the decision gate handle them.

---

## Step 6: Decision Gate

After completing Steps 1–5, apply this decision gate. Every branch has a clear next action.

### Gate A: Is the pain real for this respondent set?

**Criteria for "Yes"**:
- ≥3/N respondents confirmed wasted effort on fragile direction (Observed, not Inferred)
- ≥2/N respondents gave specific stories with real time/cost consequences
- ≥1/N respondent identified early direction evaluation as their top wasted effort

**If Yes** → Pain is real. Proceed to Gate B.

**If No** → Pain is absent or weak for this profile. Close OL-016 with rejection verdict. Open new loop for ICP revision. Do not proceed to product testing with this ICP.

**If Partial** (some confirm, some don't) → Attempt ICP segmentation: which sub-profile has the pain? Refine the profile and run 2–3 more interviews with the narrower definition before concluding.

---

### Gate B: Is the ICP correctly defined?

**Criteria for "Yes"**:
- Respondents who confirmed the pain match the primary profile in `layer0_target_profile.md`
- No unexpected exclusion pattern (e.g., if only 2+ year veterans have the pain but beginners don't, the profile needs revision)

**If Yes** → ICP is approximately right. Proceed to Gate C.

**If No** → Revise the profile. Record the revised ICP hypothesis. Run second pass of interviews before concluding.

---

### Gate C: Is the current product framing relevant?

**Criteria for "Yes"**:
- The pain respondents described is the gap between "initial idea" and "committed development" — which is what Give Me a DAY targets
- Respondents' current substitutes are ad hoc, manual, or non-existent — suggesting an actual product gap
- The comparison / multi-candidate behavior exists (at least sometimes) in real workflows

**If Yes** → Product framing is approximately relevant. Proceed to Phase 2 (show product to 2–3 confirmed-pain respondents).

**If No** → The product addresses a different gap than the one respondents actually experience. Product framing needs revision. Do not show the product yet. Record the gap between product framing and observed pain, and open a new loop for framing revision.

---

## Step 7: Repo State Update After First Synthesis

After synthesis is complete and the decision gate is applied, write the following back to repo state:

### Always write:

1. **`docs/research/mom_test_synthesis_01.md`** — full synthesis document
2. **`OPEN_LOOPS.md`** — update OL-016 status (closed with verdict, or updated with revised ICP)
3. **`docs/state/product.md`** — update "Current Unknowns" table: mark "Live user validation" with the synthesis verdict (Confirmed / Rejected / Inconclusive)
4. **`SESSION_HANDOFF.md`** — update with synthesis findings and next action

### If pain confirmed, also write:

5. **`docs/state/marketing.md`** — update ICP section with confirmed respondent profile
6. **`DECISIONS.md`** — add a new decision entry: ICP hypothesis (Confirmed / Revised / Rejected) based on Observed evidence from N interviews, date

### If pain not confirmed, also write:

5. **`DECISIONS.md`** — record rejection of current ICP hypothesis with evidence
6. New open loop for ICP revision

---

## What Good Synthesis Looks Like

A synthesis is good if a new reader can answer these questions from it:

- Who did we talk to?
- What did they actually say about their workflow? (Not our interpretation — their words.)
- Which parts of our original hypothesis were confirmed? Which were rejected?
- What remains unknown?
- What should we do next, and why?

A synthesis is bad if it:
- Smooths over contradictions to tell a clean story
- Uses "respondents generally felt..." without specific evidence
- Promotes Inferred findings to Observed status
- Concludes "the product is validated" based on positive reactions to the idea
- Misses the distinction between "they said the pain exists" and "they showed the pain exists through specific past behavior"

The test: can you point to a specific quote from a specific interview for each key finding? If yes, it is a good synthesis. If no, it is speculation dressed as research.
