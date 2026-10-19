---
name: meeting-notes
description: >-
  Turn rough meeting notes, a chat log, or a full transcript into clean minutes that people actually read,
  with a short summary, the decisions made, action items each with an owner and a due date, open questions,
  and anything parked for later. Flags missing owners or dates instead of guessing. Use this skill whenever
  the user pastes notes or a transcript and asks to "write up the meeting", "make minutes", "summarise this
  call", or "who does what", or says "maak notulen", "werk mijn aantekeningen uit", or "vat dit overleg samen".
license: "MIT"
metadata:
  author: "prompt"
  category: "productivity"
  tags: "meeting notes, minutes, action items, transcript, notulen, vergadering, actiepunten, summary"
  version: "1.0.0"
  summary_nl: "Maakt van ruwe aantekeningen of een transcript nette notulen met besluiten, actiepunten met eigenaar en datum, en open vragen."
---

# Meeting notes

The value of a meeting lives in what was decided and who will do what by when. Raw notes and transcripts
bury that under discussion. This skill extracts it, keeps it faithful to what was actually said, and makes
gaps visible so they can be resolved before everyone forgets.

## Workflow

1. **Read everything once before writing.** Transcripts often reverse decisions halfway ("actually, let's
   not do that"); the final state is what counts. Note the meeting title, date, and attendees if present.
2. **Ask about the audience if it is unclear.** Minutes for the participants can be terse; minutes for
   people who were absent need a little more context. Also check the language: write in the language of
   the meeting unless the user asks otherwise.
3. **Extract decisions.** A decision is something the group agreed on, not something someone proposed.
   Phrase each as a clear statement: "We launch the beta on 3 March with 50 users." If agreement is
   ambiguous in the source, list it under open questions instead.
4. **Extract action items.** Each needs an action starting with a verb, an owner (one person, not "the
   team"), and a due date. When the source lacks an owner or date, write "owner?" or "date?" so it is
   visibly incomplete. Guessing would create commitments nobody made.
5. **Collect open questions and parked topics.** Unresolved points, things waiting on someone outside the
   meeting, and items explicitly postponed.
6. **Write a 2-4 sentence summary.** The gist for someone with 20 seconds: purpose, main outcome, next step.
7. **Compress discussion.** Keep only the reasoning that explains a decision. Drop small talk, repetition,
   and who-said-what unless attribution matters (e.g. a stated objection).
8. **Handle sensitive content with care.** Personal remarks, HR topics, or confidential numbers in a
   transcript may not belong in minutes that are widely shared; ask the user when in doubt.

## Output template

```markdown
# Product sync – 12 Nov 2025
**Attendees:** Anna (PM), Ravi (dev), Lotte (design). **Absent:** Mark.

## Summary
We agreed to cut the export feature from the December release to protect the launch date. Design for the
new onboarding is approved with one change. Next sync: 19 Nov.

## Decisions
1. Export to Excel moves to the January release.
2. Onboarding design approved; step 3 becomes optional.

## Action items
| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Update the release plan and inform support | Anna | 14 Nov |
| 2 | Make onboarding step 3 skippable | Ravi | 18 Nov |
| 3 | Share final onboarding copy | Lotte | date? |

## Open questions
- Do enterprise customers need export in December? (Anna to ask sales)

## Parked
- Pricing page redesign, revisit in January.
```

For Dutch minutes use the same structure with headings like *Samenvatting*, *Besluiten*, *Actiepunten*
(Actie / Eigenaar / Deadline), *Open vragen*, and *Geparkeerd*.

## Pitfalls and when to ask

- Stay faithful. Do not add decisions, deadlines, or numbers that were not in the source, and do not
  soften or sharpen what people said.
- Relative dates ("next Friday") need the meeting date to resolve; if it is missing, ask or keep the
  relative wording.
- If a transcript has speaker labels like "Speaker 2", ask who that is rather than guessing names.
- If the notes are too fragmentary to tell what was decided, say so and list your interpretation as
  questions for the user to confirm.
- Offer, but do not automatically do, follow-ups such as drafting the email to attendees or creating tasks.

## Scope

This skill writes up meetings that already happened. Planning an agenda, writing a standalone email, or
managing a task list over time are separate tasks.
