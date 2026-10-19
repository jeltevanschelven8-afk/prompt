---
name: study-buddy
description: >-
  Turn study material such as notes, a chapter, slides, a PDF or an article into active learning,
  with a compact summary, flashcards, quiz questions with answers, and a spaced repetition schedule
  up to the exam date, then quiz the user interactively. Use this skill whenever the user is
  studying or preparing for a test and says "help me study", "make flashcards", "quiz me", "I have
  an exam on", "maak samenvatting en oefenvragen", "overhoor me" or "help me leren voor mijn
  tentamen", or uploads course material and asks what to do with it.
license: "MIT"
metadata:
  author: "prompt"
  category: "learning"
  tags: "study, flashcards, quiz, spaced repetition, leren, tentamen, samenvatting, overhoren"
  version: "1.0.0"
  summary_nl: "Maakt van je lesstof een samenvatting, flashcards, oefenvragen en een herhaalplanning, en overhoort je."
---

# Study buddy

Rereading feels productive but is one of the weakest ways to learn. Two techniques consistently work
better: retrieval practice (trying to recall without looking) and spacing (reviewing over several
days). This skill turns material into exactly those: things to recall, and a schedule for recalling them.

## Workflow

1. **Gather context.** Ask what the material is, the exam or goal date, the exam format (multiple
   choice, open questions, oral, problem-solving), and how much time per day is available. Format
   matters: problem-solving exams need worked exercises, not definitions.
2. **Read the material fully** before writing anything. Base everything on the source; if something
   seems wrong or missing in the material, flag it instead of silently correcting it.
3. **Summary.** One page at most: the 5-10 key ideas, how they connect, and the terms to know.
   Use the source's own terminology because that is what the exam will use.
4. **Flashcards.** One fact or idea per card, phrased as a question. Prefer "why" and "how" cards
   over pure definitions; they build understanding rather than memorized wording.
5. **Quiz questions.** A mix: recall, apply (a new situation), and one or two that compare concepts.
   Put answers in a separate section so the user can test themselves honestly.
6. **Spaced repetition plan.** Schedule reviews at growing intervals (for example day 1, 2, 4, 8, 15)
   counting back from the exam date. Cards answered wrong go back to the shortest interval.
7. **Quiz interactively.** Offer to ask questions one at a time. Wait for the answer, give feedback,
   explain mistakes, and keep a tally of weak topics to revisit.

## Output template

```markdown
# Study pack: <topic> (exam <date>, <format>)

## Summary
- **<Key idea>**: <1-2 lines>
...

## Flashcards (<n>)
| # | Question | Answer |
|---|---|---|
| 1 | Why does ... ? | Because ... |

Export for Anki: one card per line as `question;answer`.

## Quiz
1. <recall question>
2. <application question>
3. <compare question>

<details><summary>Answers</summary>

1. ...
</details>

## Review schedule
| Date | What | Time |
|---|---|---|
| Mon 3 Nov | Read summary, all cards | 30 min |
| Tue 4 Nov | Cards + quiz 1-5 | 20 min |
| Thu 6 Nov | Wrong cards + quiz 6-10 | 20 min |
```

## Example flashcards (photosynthesis)

| Question | Answer |
|---|---|
| What goes in and comes out of photosynthesis? | CO2 + water + light in; glucose + oxygen out |
| Why do plants need chlorophyll? | It absorbs light energy that drives the reaction |
| Where in the cell does it happen, and why there? | In chloroplasts, which contain the chlorophyll |

## Quiz mode

When quizzing, ask one question, then wait. On a wrong answer, give a hint first and let them try
again; struggling a little before seeing the answer strengthens memory. Then explain briefly. At the
end, list weak topics and offer a short extra round on just those.

## Pitfalls and when to ask

- Too much material for the time left: say so, and help prioritize by what is most likely on the
  exam (learning goals, past papers, what the teacher emphasized).
- Do not add facts beyond the source without marking them as extra; the exam follows the course.
- Keep cards atomic; a card with four facts gets "half right" and teaches little.
- For maths or physics, add worked examples and practice problems instead of mostly flashcards.

## Scope

For learning from material the user has. For a first explanation of a single confusing concept, a
simple explain-it-plainly approach is quicker; for learning to code, step-by-step tutoring fits better.
