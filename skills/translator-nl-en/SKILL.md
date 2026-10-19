---
name: translator-nl-en
description: >-
  Translate text between Dutch and English, and to or from other languages, while keeping the tone,
  idiom, register (je/u, formal/informal) and formatting of the original. Flags ambiguous or
  culture-specific terms instead of guessing, and keeps Markdown, HTML, placeholders and code intact.
  Use this skill whenever the user asks to translate, localise or "put this in English/Dutch", pastes
  foreign text and asks what it means, or types "vertaal naar het Engels", "vertaal dit", "wat staat
  hier in het Nederlands" or "zet om naar het Nederlands", including emails, UI strings and documents.
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "translation, vertalen, dutch, english, nederlands, engels, localisation, i18n"
  version: "1.0.0"
  summary_nl: "Vertaalt tussen Nederlands en Engels (en andere talen) met behoud van toon, opmaak en spreekwoorden."
---

# Translator NL-EN

A good translation reads as if it had been written in the target language, says exactly what the
original says, and looks the same on the page. Word-for-word translation fails the first test; free
rewriting fails the second. This skill aims for the middle: faithful meaning, natural phrasing.

## Workflow

1. **Establish direction and purpose.** Detect the source language. If the target is not stated and the
   text is Dutch, assume English and vice versa. Note what the text is for (email to a client, website,
   legal notice, chat message), because that decides the register.
2. **Pick the register on purpose.** Dutch forces a choice English hides: *je* or *u*. Follow the
   original when translating into Dutch from a Dutch-speaking context; otherwise use *je* for
   consumer, startup and informal content and *u* for government, legal, healthcare and formal
   business letters. Tell the user which you chose so they can switch it.
3. **Translate meaning, then polish for flow.** Restructure sentences where the target language wants it.
   Dutch puts verbs at the end of subordinate clauses and tolerates long compounds; English prefers
   shorter sentences and active verbs.
4. **Handle idioms by equivalent, not literally.** "Nu komt de aap uit de mouw" becomes "now we see what
   is really going on", not a monkey and a sleeve. If no equivalent exists, translate the meaning.
5. **Preserve everything that is not prose.** Keep Markdown, HTML tags, line breaks, bullet structure,
   placeholders like `{name}` or `%s`, URLs, code, product names and numbers exactly as they are.
6. **Localise conventions** where the reader expects it, and say so: decimal comma vs point (1.234,56 vs
   1,234.56), date order (17-10-2026 vs October 17, 2026), currency position (EUR 25 / € 25,-).
7. **Flag, do not guess.** Collect terms that are ambiguous, legal or domain-specific in a short note
   after the translation.

## Classic traps between Dutch and English

| Dutch | Tempting but wrong | Usually right |
|---|---|---|
| eventueel | eventually | possibly, if needed |
| actueel | actual | current, topical |
| controleren | control | check, verify |
| solliciteren | solicit | apply (for a job) |
| bellen | to bell | to call |
| Graag gedaan | Gladly done | You're welcome |
| Met vriendelijke groet | With friendly greeting | Kind regards |
| BV / ZZP'er | (left as is for UK/US readers) | private limited company / freelancer (self-employed) |

## Output format

Give the translation first, clean and ready to paste. Then, only if there is something to say, a short
notes block:

```
[translation]

---
Notes
- Register: used "you" informal; switch to "u" in Dutch if this goes to a government body.
- "aanmaning" translated as "reminder"; if this is a formal legal demand, "formal notice" fits better.
- Kept {customer_name} and the Markdown links unchanged.
```

Example: *"Kun je even checken of de offerte klopt? Dan kan ik hem morgen versturen."* becomes
*"Could you quickly check whether the quote is correct? Then I can send it out tomorrow."* No notes
needed.

## When to stop and ask

- Legal, medical or contractual text where a wrong word has consequences: translate, but recommend a
  professional review and flag every term you were unsure of.
- The target variant matters and is unclear (British vs American English, Flemish vs Netherlands Dutch).
- Wordplay, slogans or rhymes that cannot survive translation; offer two or three adapted options.
- Placeholder or tag structure that looks broken in the source; do not repair it silently.

## Scope

For translation and localisation. Proofreading a text in its own language is a different job (see a
proofreading skill). This skill does not certify translations for official use.
