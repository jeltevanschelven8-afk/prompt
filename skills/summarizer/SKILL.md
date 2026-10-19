---
name: summarizer
description: >-
  Summarise long documents, reports, email threads, chat exports, articles, papers or meeting
  transcripts into a TL;DR, key points, decisions, action items and open questions, at an adjustable
  length from one line to a full page. Stays faithful to the source and marks what is unclear. Use this
  skill whenever the user asks to summarise, condense, "give me the gist", "what are the key points",
  "tl;dr", or types "vat dit samen", "maak een samenvatting", "wat zijn de belangrijkste punten" or
  "kort samengevat", including when they paste a long text or attach a file without further instructions.
license: "MIT"
metadata:
  author: "prompt"
  category: "productivity"
  tags: "summary, samenvatting, tldr, meeting notes, notulen, transcript, key points, actiepunten"
  version: "1.0.0"
  summary_nl: "Vat lange documenten, mailthreads of transcripten samen in een TL;DR, kernpunten, besluiten en open vragen."
---

# Summarizer

A summary is useful when the reader can act on it without opening the original, and trust that nothing
important was dropped or added. Length matters less than selection: the right five points beat twenty
paraphrased paragraphs. This skill picks the format to fit the source and the reader.

## Workflow

1. **Identify the source type and the reader's goal.** A meeting transcript needs decisions and action
   items; a research paper needs question, method, findings and limits; an email thread needs where it
   stands now and what is expected of the user. If the user said why they need it ("for my manager",
   "to decide whether to read it"), let that drive the selection.
2. **Read the whole source.** For very long material, work section by section and keep running notes,
   then summarise the notes. Skimming only the start is how summaries miss the conclusion.
3. **Separate what was said from what was decided.** In threads and meetings, proposals often get
   reversed later; report the final state and mention the reversal only if it matters.
4. **Pick the length.** Default to the standard format below. Respect explicit requests ("in one
   sentence", "max 100 words", "bullet points only").
5. **Keep it faithful.** Use the source's numbers, names and dates exactly. Do not add outside facts or
   your own opinion unless asked; if you add context, label it.
6. **Mark uncertainty.** Unclear speakers in a transcript, contradictions, missing attachments: list them.

## Standard output format

```
TL;DR
One or two sentences with the main point and its consequence.

Key points
- 3-7 bullets, most important first, each one self-contained.

Decisions
- What was decided, by whom if known.

Action items
- [ ] Owner - task - deadline (if stated)

Open questions
- What remains unresolved or unclear in the source.
```

Drop empty sections rather than writing "none". An article has no action items.

### Length presets

| Ask | Deliver |
|---|---|
| "one line" / "in één zin" | Single sentence, max ~30 words |
| "short" / "kort" | TL;DR + 3 bullets |
| default | Full format above, usually 150-300 words |
| "detailed" / "uitgebreid" | Section-by-section summary with headings that mirror the source |

## Example

Source: a 40-message email thread about moving a product launch.

```
TL;DR
Launch moves from 3 to 17 November because the payment provider certification is late; marketing
campaign shifts with it.

Key points
- Certification expected 10 November (provider's estimate, not confirmed).
- Press release stays on 3 November but without a date for availability.
...
Action items
- [ ] Sanne - update campaign planning - Friday
Open questions
- Who informs the two pilot customers? Not agreed in the thread.
```

## Pitfalls

- **Over-compression**: "The team discussed the budget" says nothing. Say what about the budget.
- **Losing the hedge**: if the source says "probably" or "estimated", keep it.
- **Language**: summarise in the language the user writes to you, unless they ask otherwise; keep
  quotes in the original language.
- **Sensitive content** (HR, medical, legal): summarise neutrally and do not editorialise.

## When to stop and ask

- The source is truncated, a file did not load fully, or attachments are referenced but missing.
- The reader's goal is unclear and the source is long and varied; ask what they need it for.

## Scope

This skill condenses existing content. It does not verify facts against outside sources, and it is not
meant for writing new content such as a report from scratch.
