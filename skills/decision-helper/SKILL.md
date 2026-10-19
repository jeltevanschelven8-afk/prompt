---
name: decision-helper
description: >-
  Help the user make a decision they are stuck on by clarifying what matters, laying out the real
  options, scoring them in a weighted pros and cons matrix, naming the risks, separating reversible
  from irreversible choices, and ending with a clear recommendation. Use this skill whenever the
  user weighs options or asks "should I", "which one should I pick", "X or Y", "help me decide",
  "pros and cons", "ik twijfel tussen", "help me kiezen" or "wat zou jij doen", for jobs, purchases,
  tools, tech stacks, offers or plans.
license: "MIT"
metadata:
  author: "prompt"
  category: "productivity"
  tags: "decision, beslissen, kiezen, pros and cons, matrix, criteria, risk, afweging"
  version: "1.0.0"
  summary_nl: "Helpt je kiezen met heldere criteria, een gewogen voor- en nadelenmatrix, risico's en een duidelijk advies."
---

# Decision helper

Most hard decisions are hard because the criteria are fuzzy, not because the options are complex.
Making the criteria explicit and weighted usually makes the answer visible. This skill guides that
process and then commits to a recommendation, because a list of pros and cons without a conclusion
leaves the user where they started.

## Workflow

1. **Frame the decision.** Write it as one question: "Which laptop do I buy for under 1,200 euro?"
   Ask when the decision must be made and what happens if they do nothing; doing nothing is often
   a real option and belongs in the list.
2. **Draw out criteria.** Ask what a great outcome looks like a year from now. Turn answers into
   4-7 criteria (cost, growth, time with family, risk). Include must-haves separately: an option
   that fails a must-have is out, no matter its score.
3. **Weigh the criteria.** Let the user distribute 100 points, or rank and assign 1-5. Their weights,
   not yours, because the decision is theirs. If they hesitate, propose weights and ask them to adjust.
4. **List options.** Include the obvious ones, "do nothing / wait", and one creative option such
   as a hybrid or a trial ("ask for a 3-month pilot").
5. **Score each option** 1-5 per criterion with a one-line reason. Mark scores that rest on
   assumptions; those are what to verify.
6. **Check reversibility.** A reversible choice (a tool with a monthly plan) deserves a fast decision
   and a trial. An irreversible or expensive one (selling a house) deserves more data first. This
   framing often reduces anxiety more than the matrix does.
7. **Name risks.** For the top two options: what could go wrong, how likely, and what would limit
   the damage. A quick pre-mortem helps: "It is a year later and this went badly. Why?"
8. **Recommend.** State the choice, the main reason, what would change your mind, and the next step.

## Output template

```markdown
## Decision: <question>  (decide by <date>)

**Must-haves:** <list>  -> eliminated: <option> (fails <must-have>)

| Criterion (weight) | Option A | Option B | Wait 3 months |
|---|---|---|---|
| Salary (30) | 4 - +15% | 3 - same | 3 |
| Learning (25) | 5 - new stack | 2 | 2 |
| Commute (20) | 2 - 50 min | 5 - remote | 5 |
| Stability (25) | 3* - startup | 5 | 4 |
| **Weighted score** | **3.55** | **3.65** | **3.40** |

*assumption, verify: funding runway of the startup

**Reversibility:** A is hard to undo within a year; B keeps options open.
**Key risks:** A - startup runs out of money (medium) -> ask about runway in the next interview.

**Recommendation:** <option>, because <main reason>.
**I would change my mind if:** <specific fact>.
**Next step:** <one concrete action>.
```

Compute the weighted score as the sum of (weight x score) / 100 and show it with two decimals, so the
user can check the arithmetic.

## Gut check

When the scores are close (within about 0.3), say so: the matrix is telling you both options are fine.
Ask the user how they feel when you announce the winner. Relief or disappointment is real data about
a criterion that was missing or underweighted; add it and rescore rather than ignoring it.

## Pitfalls and when to ask

- Do not invent facts about options (prices, salaries, specs). Ask, or mark them as estimates to check.
- Watch for criteria that double count (cost and affordability) and merge them.
- For medical, legal or major financial decisions, structure the thinking but recommend talking to a
  qualified professional before acting; you are not a licensed advisor.
- If the user clearly already decided and wants confirmation, say what you see and still name the
  biggest risk; that is more useful than agreement.

## Scope

For choices between options. For turning a chosen option into steps, plan it afterwards as a
separate task.
