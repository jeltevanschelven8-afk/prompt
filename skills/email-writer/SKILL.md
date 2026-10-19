---
name: email-writer
description: >-
  Write or rewrite emails in Dutch or English with the right tone for the reader, a subject line that says
  what the mail is about, the purpose in the first sentence, one clear ask, and nothing that does not need to
  be there. Handles requests, follow-ups, bad news, complaints, and replies to difficult messages. Use this
  skill whenever the user asks to "write an email", "reply to this mail", "make this sound more professional",
  or "shorten this email", or says "schrijf een mail", "help me deze mail te beantwoorden", or "maak deze
  mail vriendelijker".
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "email, mail, writing, tone, business writing, schrijven, zakelijk, nederlands"
  version: "1.0.0"
  summary_nl: "Schrijft of herschrijft je e-mails in het Nederlands of Engels: duidelijk onderwerp, doel voorop, één vraag, kort."
---

# Email writer

People read email in a few seconds, often on a phone, between other things. An email works when the reader
knows from the subject and first line what it is about and what you need from them. This skill writes for
that reader, and leaves the decision to send with the user.

## Workflow

1. **Get the essentials.** Who is the reader and what is the relationship (client, manager, colleague,
   stranger)? What should happen after they read it? Any deadline? Which language? If the user pasted a
   mail to reply to, read it fully and note every question it asks, so none get missed.
2. **Pick the tone deliberately.** Match the reader and the situation: warm and direct for colleagues,
   polite and precise for clients, calm and factual for complaints. In Dutch, decide between "je" and "u"
   based on how the other person writes or on the relationship; ask if unclear, because getting it wrong
   is noticed.
3. **Write the subject line.** Specific and scannable, ideally with the action or topic: "Approval needed:
   Q3 budget by Fri 14 Nov", "Vraag over factuur 2024-118". Avoid "Question" or "Update".
4. **Lead with the purpose.** The first sentence says why you are writing. Context comes after, and only
   as much as the reader needs to answer.
5. **Make one ask, clearly.** One request, with a date if timing matters, placed where it cannot be missed.
   If there really are several questions, number them so the reader can answer point by point.
6. **Cut.** Remove throat-clearing ("I hope this email finds you well" can stay only if it fits the
   relationship), repeated points, and hedging. Aim for under 150 words for most mails.
7. **Close simply.** A short closing line and sign-off in the right register: "Best regards" / "Met
   vriendelijke groet" for formal, "Thanks," / "Groet," for familiar.
8. **Offer a variant when tone is uncertain.** For sensitive mails, give a softer and a firmer version and
   explain the difference in one line.

## Example (Dutch rewrite)

Original from the user: a long mail starting with an apology and burying the question in paragraph three.

```
Onderwerp: Graag uw akkoord op offerte website vóór 20 november

Beste mevrouw De Vries,

Wilt u de bijgevoegde offerte voor de nieuwe website vóór 20 november goedkeuren? Dan kunnen we in
december live gaan.

De offerte bevat de drie onderdelen die we op 4 november bespraken; de prijs is ongewijzigd.
Heeft u vragen, dan bel ik u graag.

Met vriendelijke groet,
Sanne Bakker
```

## What the user receives

The email ready to paste (subject plus body), followed by a short note when useful:
- what changed and why, for rewrites (e.g. "moved the request to the first line, cut 120 words");
- any assumption made (names, dates, "u" vs "je") that the user should check;
- optionally one alternative version with a different tone.

## Pitfalls and when to ask

- Do not invent facts, dates, amounts, or promises. Use clear placeholders like [date] and point them out.
- For emotionally charged mails (complaints, conflicts, resignations), suggest the user waits before
  sending and keep the draft factual; angry mails rarely achieve their goal.
- Legal, HR, or contractual wording can have consequences; flag it and suggest a check by the right person.
- Drafting is the job here. Do not send mail on the user's behalf unless they explicitly ask and confirm.
- If the user's goal conflicts with the tone they asked for ("make it friendly but threaten to cancel"),
  point it out and propose a version that is firm and polite.

## Scope

This skill writes individual emails. Newsletters, marketing campaigns, and long reports are different
formats; meeting follow-ups with full minutes are better handled as meeting notes first.
