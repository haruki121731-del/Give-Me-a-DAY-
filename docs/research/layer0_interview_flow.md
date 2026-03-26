# Layer 0 — Interview Execution Guide

**Purpose**: Step-by-step guide for running Mom Test interviews in Layer 0.
**Date**: 2026-03-26
**Related**: `mom_test_run_plan.md`, `layer0_target_profile.md`

---

## Pre-Interview Prep (15 min before each call)

1. **Review the respondent's background**: Re-read their public work or how you reached them. Identify 1–2 specific things to reference in the opening.
2. **Set up note-taking**: Open `docs/research/mom_test_logs/interview_NNN.md` (use the template in `mom_test_run_plan.md`). Have it ready to type into during or immediately after the call. Do not rely on memory.
3. **Confirm the goal**: You are here to learn about their workflow. You are not here to explain, pitch, or validate your product idea.
4. **Turn off: pitch mode.** If you feel the urge to say "actually, what we're building is..." — suppress it entirely.

---

## Opening Script (2–3 min)

Say something close to this, in your own words:

> "Thanks for taking the time. What I'm researching is how people who build systematic strategies decide whether a new direction is worth pursuing before committing serious time to it — the early stage, before full backtesting and development.
>
> I don't have anything to show you or pitch. I just want to hear about your actual experience. The most useful thing you can tell me is what really happens — not what you think should happen.
>
> Can I start by asking you to walk me through how you actually approach a new strategy idea when it first comes up?"

What this opening does:
- Sets the expectation that this is a learning conversation, not a product demo
- Signals you want real behavior, not opinions about products
- Flows directly into Q1 without awkward transition

---

## Conversation Flow

Run the questions roughly in order. The sequence builds context: early questions establish their real workflow; later questions probe pain depth. Do not skip ahead unless they naturally covered it already.

Each question should generate 2–5 minutes of conversation. If someone gives a one-sentence answer, follow up with: "Can you tell me more about that?" or "What happened next?" or "What was that like?"

Aim for 20 minutes total. 30 is acceptable. Do not go over 30 without asking permission.

---

## 10 Core Questions

These are taken directly from `mom_test_run_plan.md`. They are reproduced here for in-call reference.

**Q1**: "Walk me through how you evaluate whether a new strategy idea is worth pursuing. What does that process look like for you today?"

*Listen for*: Is there a process at all? Is it ad hoc or systematic? How early in the idea does it start?

---

**Q2**: "Tell me about the last time you started researching a strategy direction that you ended up abandoning. What happened?"

*Listen for*: How far did they get before abandoning? What triggered the decision? How much time was lost? How did it feel?

---

**Q3**: "Before you commit serious time — backtesting, data acquisition, infrastructure — how do you currently decide whether it's worth going deeper?"

*Listen for*: Is there a deliberate pre-validation step? Or do they go straight to implementation? What is their threshold?

---

**Q4**: "What is the hardest part of that early evaluation? What do you wish were easier?"

*Listen for*: Don't suggest answers. Wait. The unprompted answer is the most valuable.

---

**Q5**: "Have you ever been confident a strategy would work, only to find out later it was fragile in a way you should have caught earlier? What happened?"

*Listen for*: A confident "yes" with a real story is gold. "Not really" is also informative — may mean they are not the right profile.

---

**Q6**: "When you look at a strategy direction you haven't tested yet, what do you believe could be wrong about it?"

*Listen for*: Do they naturally enumerate assumptions? Or do they struggle? This tells you whether assumption-awareness is a real gap for this person.

---

**Q7**: "Do you ever compare multiple strategy directions against each other before picking one to develop? How do you do that comparison today?"

*Listen for*: "I usually just pick one" vs. "I always compare 2–3." The product's multi-candidate structure is either resonant or not.

---

**Q8**: "What tools or resources do you currently use when evaluating a new strategy direction before heavy investment?"

*Listen for*: This reveals the real competitive landscape. "My own judgment" is a competitor. "FactSet + Python notebook" is a competitor. "Nothing systematic" is an opportunity.

---

**Q9**: "If you could eliminate one type of wasted effort from your strategy research workflow, what would it be?"

*Listen for*: Is early direction evaluation the top pain? Or is it something else — data quality, execution, infrastructure? What actually ranks first?

---

**Q10**: "Is there anything about how you evaluate strategies that you think most people misunderstand or get wrong?"

*Listen for*: This question asks nothing about your product. It reveals sophistication level and what they believe is broken about the current state of practice.

---

## Optional Follow-Up Questions

Use these if a topic warrants deeper exploration, not as substitutes for the 10 core questions.

- "How long did that take you, roughly?"
- "What would have needed to be different for you to have caught that earlier?"
- "Did you talk to anyone else about it at the time, or work through it alone?"
- "Would you have done anything differently if you'd had more data up front?"
- "How confident were you at the time that the direction was solid?"
- "What's your current signal that a direction is worth abandoning vs. just needs more work?"

---

## Red-Flag Questions to Avoid

Never ask these. They contaminate data.

| Question | Why it's bad |
|----------|-------------|
| "Would you use a product that helps you validate strategies?" | Hypothetical future behavior. Always gets "yes." Means nothing. |
| "What do you think of this idea: [describe product]?" | Shifts to product feedback. People are polite. |
| "How much would you pay for this?" | Premature. Price answers are guesses. |
| "Do you think other people in your field have this problem?" | Deflects to opinion, not their personal experience. |
| "If we built [feature], would that solve your problem?" | Tests your solution, not their problem. |
| "Is this a real problem for you?" | Leading. They'll say yes to not seem dismissive. |

---

## How to End the Interview Well

**2–3 minutes before the 20-minute mark**, start closing:

> "This has been really useful — exactly the kind of thing I was hoping to learn. I don't want to take more than the 20 minutes I asked for. Can I ask one last thing: is there anyone else you know who builds systematic strategies who might have a different perspective on this? I'm trying to talk to a range of people."

This does three things:
1. Respects their time and ends cleanly
2. Opens the possibility of a warm referral (the highest-value next step)
3. Ends on a forward-looking note rather than an awkward close

If they offer to chat longer and the conversation is productive: take it.

After the call:

> "Thanks again — this was genuinely helpful. If anything I learn seems relevant to share back with you, I'll do that. Can I follow up if a specific question comes up?"

---

## What to Capture Immediately After the Call

Within 30 minutes of hanging up, fill in `docs/research/mom_test_logs/interview_NNN.md`. Memory degrades fast.

Specifically:

| Item | What to write |
|------|---------------|
| **Pain confirmation** | Did they confirm past experience with wasted effort on a fragile direction? (Q2/Q5) |
| **Pre-validation process** | Do they have one? Is it systematic or ad hoc? What does it look like? (Q3) |
| **Comparison behavior** | Do they compare multiple directions? (Q7) |
| **Top wasted effort** | Their Q9 answer, verbatim or close paraphrase |
| **Current substitutes** | What they actually use today (Q8) |
| **Surprise finding** | Anything that contradicted the product hypothesis |
| **Direct quotes** | 2–3 verbatim quotes worth keeping — exact words matter |
| **Evidence labels** | Mark each finding as Observed / Inferred / Unknown |
| **Referrals received** | Names or handles of people they mentioned |

Do not synthesize across interviews until ≥3 are complete. The synthesis step is separate and uses `layer0_synthesis_framework.md`.
