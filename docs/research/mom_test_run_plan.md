# mom_test_run_plan.md

**Purpose**: Operational plan for executing The Mom Test customer validation interviews for Give Me a DAY v1.
**Related open loop**: OL-016 (Mom Test / customer validation)
**Last updated**: 2026-03-25
**Evidence standard**: All interview outputs must be labelled Observed. No synthesized, inferred, or representative data.

---

## Interview Objective

Determine whether the pain Give Me a DAY addresses — the difficulty of knowing whether an investment strategy direction is worth pursuing before committing to building it — is real, frequent, and currently unsolved for target respondents.

**Not** the objective: validating that the product interface is usable, that respondents like the idea, or that respondents would pay a specific price. Those questions are premature until the pain is confirmed.

The Mom Test principle: ask about their life, not your idea. The interview succeeds if you come away with evidence about what respondents actually do today — not what they say they would do with your product.

---

## Target Respondent Profile

### Primary target (interview first)

Quantitative or systematic investment practitioners who build or evaluate investment strategies — any of:
- Quant researchers at hedge funds, asset managers, or proprietary trading firms
- Individual systematic traders with ≥1 year of strategy research experience
- Data scientists at financial institutions who work on alpha research or strategy evaluation
- Academics or graduate researchers in quantitative finance with applied strategy research experience

**Required**: Direct personal experience deciding whether to pursue or abandon a strategy direction. They have felt the cost of pursuing a direction that turned out to be fragile.

### Secondary target (interview after ≥2 primary)

Adjacent roles with related pain:
- Investment analysts who evaluate systematic strategies for investment committees
- Portfolio managers who oversee strategy development teams
- Fintech founders who have built investment tools or data products

### Exclusion criteria

Do not interview:
- People whose job is UI/UX, product management, or sales — they evaluate products, not strategy directions
- Passive investors (index funds, buy-and-hold) — they do not face the strategy evaluation problem
- Non-practitioners who are interested in the product idea but have no direct experience with the pain
- Friends or colleagues who know about the product — their responses will be contaminated

---

## 10 Interview Questions

Use these in order. Do not skip to later questions before the earlier ones produce a clear answer. The sequence builds context — early questions establish what they actually do today; later questions probe depth of pain.

**Q1**: "Walk me through how you evaluate whether a new strategy idea is worth pursuing. What does that process look like for you today?"

*Why*: Establishes ground truth. If they have no process, or it is trivially simple, the pain may not exist for this respondent. If the process is elaborate, you are learning about the real workflow.

---

**Q2**: "Tell me about the last time you started researching a strategy direction that you ended up abandoning. What happened?"

*Why*: Real past behavior, not hypothetical. Listen for: how far in did they get before abandoning? What triggered the decision? How costly was the wasted effort?

---

**Q3**: "Before you commit serious time to a strategy direction — backtesting, data acquisition, infrastructure — how do you currently decide whether it's worth going deeper?"

*Why*: This is the exact gap Give Me a DAY addresses. You are looking for: is there a lightweight pre-validation step? If not, why not? If yes, is it systematic or ad hoc?

---

**Q4**: "What is the hardest part of that early evaluation? What do you wish were easier?"

*Why*: Open-ended pain probe. Do not suggest answers. Listen for: data availability concerns, assumption clarity, comparison to alternatives, confidence calibration.

---

**Q5**: "Have you ever been confident a strategy would work, only to find out later it was fragile in a way you should have caught earlier? What happened?"

*Why*: Probes the falsifiability problem — the core product value. Real stories here are gold. A confident "yes" with a real story indicates the pain is deep.

---

**Q6**: "When you look at a strategy direction you haven't tested yet, what do you believe could be wrong about it?"

*Why*: Tests assumption-awareness. The product assumes users struggle to identify weak assumptions. Some experts do this naturally — they may not need help. Others have blind spots. You want to know which type of respondent this is.

---

**Q7**: "Do you ever compare multiple strategy directions against each other before picking one to develop? How do you do that comparison today?"

*Why*: Tests whether the multi-candidate comparison structure (a core product feature) maps to real behavior. If respondents say "I usually just pick the one that seems most promising," the comparison feature may not resonate. If they say "I always compare 2–3 before committing," it does.

---

**Q8**: "What tools or resources do you currently use when evaluating a new strategy direction before heavy investment?"

*Why*: Reveals existing solutions and substitutes. The answer tells you who the real competition is — not other products, but their current behavior. "I use FactSet and my own judgment" is a real competitor.

---

**Q9**: "If you could eliminate one type of wasted effort from your strategy research workflow, what would it be?"

*Why*: Direct pain priority ranking. You are checking whether the pain Give Me a DAY addresses (wasted effort on fragile directions) is top-of-mind, or whether something else entirely ranks higher.

---

**Q10**: "Is there anything about how you evaluate strategies that you think most people misunderstand or get wrong?"

*Why*: The best Mom Test question — it does not reveal the product at all, but it reveals how sophisticated they are and what they believe about the problem space. Often produces the most honest, useful answer.

---

## 5 Anti-Pattern Questions to Avoid

These questions produce contaminated or useless data. Do not use them.

**AP-1**: "Would you use a product that helps you validate investment strategies before building them?"
*Why bad*: Hypothetical future behavior. People always say yes to hypothetical products that sound reasonable. Tells you nothing.

**AP-2**: "What do you think of this idea: [describe the product]?"
*Why bad*: Solicits opinion on your idea. Respondents are polite. You will hear "that's interesting" whether the pain is real or not.

**AP-3**: "How much would you pay for a tool that does X?"
*Why bad*: Pricing questions are premature and unreliable before pain confirmation. Price answers are guesses, not commitments.

**AP-4**: "Do you ever feel like you waste time on strategies that don't work out?"
*Why bad*: Leading question. The answer is always yes. Does not tell you whether the pain is severe enough to motivate behavior change.

**AP-5**: "If we built [specific feature], would that solve your problem?"
*Why bad*: Tests your solution, not their problem. Puts respondents in "product feedback mode" where they optimize your solution rather than describing their actual experience.

---

## Note-Taking Template

Use this during or immediately after each interview. Do not rely on memory. File at `docs/research/mom_test_logs/interview_NNN.md`.

```markdown
# Interview NNN

**Date**: YYYY-MM-DD
**Duration**: N minutes
**Respondent type**: [primary / secondary]
**Role**: [general description — not full name unless respondent consents to named record]
**Context**: [how they were reached, what their background is]

---

## Key signals (fill during or immediately after interview)

### Pain confirmation
- [ ] Confirmed past experience of wasted effort on fragile direction (Q2/Q5)
- [ ] Has an ad hoc pre-validation process (Q3)
- [ ] Has no pre-validation process (Q3)
- [ ] Expressed assumption-awareness gap (Q6)
- [ ] Uses multi-candidate comparison (Q7)

### Pain priority
Q9 answer (verbatim or close paraphrase):
> [their answer]

Rank within their workflow (did they name this as top pain? secondary? not a priority?):

### Current substitutes
What tools/processes do they use today (Q8)?
- [list]

### Surprise / unexpected finding
[Anything that contradicted the product hypothesis, or revealed a pain point not anticipated]

### Direct quotes worth keeping
> [quote 1]
> [quote 2]

---

## Evidence classification

| Item | Type | Evidence label |
|------|------|---------------|
| [specific finding] | Pain / Behavior / Substitute / Rejection | Observed |

---

## Interviewer notes
[What to follow up on. What questions produced the best signal. What to ask differently next time.]
```

---

## Evidence Capture Format

After each interview, the agent will process the notes into a structured evidence record. Each record must have an evidence label:

- **Observed**: Respondent explicitly stated this happened to them, or described a behavior they perform
- **Inferred**: Agent interpretation of what the respondent meant (label clearly — do not treat as Observed)
- **Unknown**: Relevant question not asked, or respondent gave ambiguous answer

No evidence record may be labeled Observed based on paraphrase or summary without the interviewer confirming it matches the respondent's actual statement.

---

## Synthesis Template

After ≥3 interviews, agent writes `docs/research/mom_test_synthesis_01.md` using this structure:

```markdown
# Mom Test Synthesis 01

**Interviews conducted**: N
**Date range**: YYYY-MM-DD to YYYY-MM-DD
**ICP hypothesis tested**: [state the hypothesis being tested]

---

## Summary verdict
[One sentence: does the pain exist for this respondent set? What is the confidence level?]

---

## Confirmed pain points (Observed)
For each: description, supporting evidence (interview + quote reference), frequency signal (mentioned by N/N respondents)

## Confirmed rejections (Observed)
For each: what was rejected, why, which respondents, what this means for product scope

## Adjacent needs (Observed)
Pain points mentioned that are adjacent but not identical to the product's core value

## ICP clarifications
Did the interviews clarify who has the pain more acutely? Who less? What changed about the respondent profile?

## Current substitutes identified
What respondents actually use today — the real competitive landscape

## Open questions
What remains unknown after these N interviews that affects product direction

---

## Evidence log
[Table of all evidence items with label, source interview, and whether Observed/Inferred/Unknown]
```

---

## OL-016 Closure Criteria

OL-016 may be closed when ALL of the following are true:

1. **Interview count**: ≥3 completed interviews with respondents matching the primary target profile
2. **Records exist**: ≥3 interview notes filed in `docs/research/mom_test_logs/` using the template above
3. **Synthesis written**: `docs/research/mom_test_synthesis_01.md` exists and addresses all synthesis template sections
4. **At least one of**:
   - At least 1 confirmed pain point matching the product's core value (Observed, not Inferred)
   - At least 1 confirmed rejection with reason recorded (this is also valid closure — a clear rejection with reason is as valuable as a confirmation)
   - At least 1 adjacent need documented that clarifies ICP scope
5. **Evidence labels used**: All findings labelled Observed, Inferred, or Unknown — no unlabelled conclusions

**Not sufficient for closure**:
- 3 interviews where respondents said the product "sounds interesting" — this is not confirmation of pain
- Agent-synthesized "likely pain points" without direct interview evidence
- Interviews with excluded respondent categories

If interviews reveal the ICP hypothesis was wrong (no pain found, or wrong people interviewed), close OL-016 with a rejection verdict and open a new loop for ICP revision. A clear rejection is valid closure.

---

## Outreach Note

Agent can draft outreach copy on request after Haruki provides a respondent list. Agent must not send any outreach without Haruki's explicit approval of the copy and recipient list. This is a hard guardrail — see D-003 (no external action without human approval).

Outreach copy should ask for 20 minutes to learn about their strategy research process. It must not describe or sell the product. The Mom Test principle: learn from their experience, not their opinion of your product.
