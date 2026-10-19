---
name: bug-report-writer
description: >-
  Turn a vague complaint into a clear, reproducible bug report with numbered steps, expected versus actual
  behaviour, environment details, relevant logs, a severity estimate, and ideally a minimal reproduction.
  Use this skill whenever the user says "it doesn't work", "write a bug report", "file an issue for this",
  "make a GitHub issue", "how do I report this bug", or pastes an error and wants to hand it to someone
  else, including Dutch requests like "schrijf een bugmelding", "het werkt niet, maak er een issue van",
  or "meld deze fout aan de ontwikkelaars".
license: "MIT"
metadata:
  author: "prompt"
  category: "testing"
  tags: "bug report, issue, reproduce, repro, qa, bugmelding, foutmelding, testing"
  version: "1.0.0"
  summary_nl: "Maakt van een vaag probleem een heldere bugmelding met stappen, verwacht versus werkelijk gedrag en een minimale repro."
---

# Bug report writer

A good bug report lets someone who has never seen the problem reproduce it in a few minutes. Most reports
fail because they describe a feeling ("the page is broken") instead of a sequence of events. This skill
turns what the user knows into facts a developer can act on, and is honest about what is still unknown.

## Workflow

1. **Collect what the user already has.** Ask for, or pull from the conversation: what they were trying
   to do, what happened instead, when it started, and any screenshots, error text, or logs. Keep the
   questions short and in one batch so the user is not interrogated step by step.
2. **Pin down reproduction steps.** Rewrite the story as numbered actions starting from a known state
   ("Logged in as a regular user, on the Orders page"). Each step is one action. If you have access to the
   code or app, try to reproduce it yourself and say whether you succeeded.
3. **Separate expected from actual.** Expected is what the user or the spec says should happen; actual is
   what was observed, quoted exactly. Paraphrased error messages are hard to search for, so copy them.
4. **Record the environment.** App version or commit, OS, browser and version, device, account type,
   feature flags, locale. Only include what could plausibly matter, but err on including version numbers.
5. **Trim logs to the relevant part.** Include the stack trace and a few lines around it, not 500 lines of
   noise. Remove personal data, customer names, and anything that looks like a credential before sharing.
6. **Narrow it down.** Does it happen every time or sometimes? Other browsers? Other accounts? Since which
   version? Each answer halves the search space. If you can, build a minimal repro: the smallest input,
   code snippet, or set of steps that still shows the bug.
7. **Estimate severity and say why.** Use the project's scale if it has one; otherwise the scale below.
   Severity is about impact, not about how annoyed the reporter is.
8. **Write a title that would be found by search.** Pattern: *where* + *what goes wrong* + *when*.
   "Checkout: total shows 0.00 after applying a discount code" beats "Checkout bug".

## Severity scale (default)

| Level | Meaning | Example |
|---|---|---|
| Critical | Data loss, security issue, or core flow down for everyone | Orders are not saved |
| High | Core flow broken for some users, no workaround | Safari users cannot pay |
| Medium | Feature broken but a workaround exists | Export fails, copy-paste works |
| Low | Cosmetic or minor annoyance | Misaligned icon in footer |

## Output template

```markdown
**Title:** Checkout: total shows 0.00 after applying a discount code

**Summary:** Applying any valid discount code sets the order total to 0.00 instead of subtracting
the discount. Orders can then be placed for free.

**Steps to reproduce**
1. Add "Blue mug" (12.50) to the cart.
2. Go to Checkout.
3. Enter discount code SAVE10 and click Apply.

**Expected:** Total is 11.25 (10% off).
**Actual:** Total is 0.00; the order can be submitted.

**Frequency:** 5/5 attempts. Also with code WELCOME5.
**Environment:** web app v2.14.1 (commit a1b2c3d), Chrome 129, Windows 11, staging.
**Logs:** `TypeError: Cannot read properties of undefined (reading 'percent')` at cart.js:88
**Severity:** Critical, because orders can be placed without payment.
**Minimal repro:** `applyDiscount({ total: 12.5 }, { code: 'SAVE10' })` returns 0.
**Notes / unknowns:** Not yet tested on production or mobile.
```

Adapt the format to the destination: GitHub and GitLab issues take Markdown as above; Jira prefers the
same headings as fields; a quick message to a colleague can be the title, steps, and actual result only.

## Pitfalls and when to ask

- Do not guess steps you cannot confirm. Mark gaps as "unknown" or ask; an invented step sends the
  developer down the wrong path.
- If the report mixes several problems, split it into separate reports so each can be closed on its own.
- Keep blame out. Describe the behaviour, not who caused it.
- Ask before posting the issue anywhere; write the text and let the user decide where it goes.
- If the "bug" is actually a feature request or a question about intended behaviour, say so and suggest
  the right format.

## Scope

This skill documents a problem. Fixing it is a separate step: once the report is clear, a debugging
workflow can take over.
