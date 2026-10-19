---
name: proofreader
description: >-
  Proofread Dutch or English text for spelling, grammar, punctuation and consistency, including Dutch
  dt-fouten, d/t endings, commas, compound words and capitalisation, while keeping the author's own
  voice. Shows every change so the user stays in control. Use this skill whenever the user asks to
  proofread, check, correct or "fix the typos" in a text, email, report, thesis or post, or types "check
  op fouten", "kun je dit nakijken", "verbeter de spelling" or "zitten er dt-fouten in", even when they
  just paste text with a short "klopt dit?".
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "proofreading, spelling, grammar, dt-fouten, spellingscontrole, nakijken, taal, correctie"
  version: "1.0.0"
  summary_nl: "Controleert Nederlandse of Engelse tekst op spelling, grammatica en dt-fouten en laat precies zien wat er verandert."
---

# Proofreader

Proofreading is correcting, not rewriting. The author should recognise their own text afterwards, only
cleaner. That is why this skill separates real errors (always fix) from style suggestions (offer, do not
impose), and shows every change.

## Workflow

1. **Detect language and variant.** Dutch (Netherlands or Flemish), English (British or American). Keep
   the variant the author already uses; do not turn "colour" into "color" unless asked.
2. **Read once for meaning** before fixing anything. Some "errors" are deliberate (quotes, slang, brand
   names, a tone that is informal on purpose).
3. **Fix real errors**: spelling, grammar, verb endings, agreement, punctuation, missing words, doubled
   words.
4. **Check consistency** across the whole text: the same term spelled the same way (e-mail vs email),
   number and date formats, capitalisation in headings, *je* vs *u*, serial comma or not.
5. **Note style issues separately**: very long sentences, unclear references, repetition. Suggest, do not
   change.
6. **Return the corrected text plus a change list** (format below).

## Dutch checks that catch most errors

- **dt-regel**: stam + t with *hij/zij/het* and with *je* after the verb is gone: *hij wordt*, *word je*,
  but *wordt je broer*. Test by swapping in *lopen*: *hij loopt* → *hij wordt*.
- **Voltooid deelwoord**: 't kofschip (x) decides -d or -t: *gefietst*, *gebeld*, *verhuisd*. Verbs whose
  stem ends in d or t keep it: *verwacht*, *beantwoord*.
- **Verleden tijd**: *hij antwoordde*, *zij praatte*, so double letters are correct here.
- **Samenstellingen** are written as one word: *klantenservice*, *ziekenhuisopname*, not *klanten service*.
  Use a hyphen for vowel clashes (*zee-egel*) and with an abbreviation (*cv-formulier*).
- **Komma's**: a comma between two finite verbs (*Als je klaar bent, bel me*), not before *dat* in a
  normal subordinate clause.
- **Hun/hen/zij**: *hun* is possessive or indirect object, *hen* after a preposition, *zij* as subject.
- Classic confusions: *als/dan* after comparatives (*groter dan*), *u/uw*, *me/mijn*, *zei/zij*.

## English checks

- its / it's, your / you're, their / there / they're, affect / effect, then / than.
- Subject-verb agreement across long phrases ("The list of items *is*").
- Comma splices, dangling modifiers, apostrophes in plurals ("FAQs", not "FAQ's").
- Dutch-English interference: "I am working here since 2020" → "I have been working here since 2020".

## Output format

```
Corrected text
--------------
[full text with all real errors fixed]

Changes (7)
- "hij word" → "hij wordt" (dt-regel)
- "klanten service" → "klantenservice" (samenstelling)
- "Als je klaar bent bel me" → "Als je klaar bent, bel me" (komma tussen twee werkwoorden)
- ...

Suggestions (not applied)
- Paragraph 2, sentence 1 is 48 words; consider splitting after "project".
```

For long texts, group changes by type ("12 x komma, 3 x dt") and list only the non-obvious ones in
full. If the user prefers it, show changes inline as `~~oud~~ **nieuw**` instead.

## When to stop and ask

- A sentence is ambiguous and the fix depends on what was meant; ask instead of choosing a meaning.
- The text mixes variants or languages in a way that might be intentional.
- The user's house style differs from standard rules (Groene Boekje vs a company style guide); follow
  theirs once known.
- A file needs editing: write the corrected version as a new file or show it, rather than overwriting the
  original without asking.

## Scope

This skill corrects existing text. Translation, rewriting for a different audience, or shortening a
text are separate jobs. It does not fact-check content.
