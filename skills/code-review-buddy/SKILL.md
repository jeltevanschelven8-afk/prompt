---
name: code-review-buddy
description: >-
  Review a diff, pull request or file the way a careful senior colleague would:
  hunt for bugs, unhandled edge cases, confusing names and maintainability
  problems, then report findings ranked by severity, each with a concrete fix.
  Use this skill whenever the user asks to review code, check a PR or diff before
  merging, says things like look over my changes, is this ok to merge, what would
  a reviewer say, or types Dutch phrases such as "review mijn code", "kijk even
  naar deze PR" or "is dit goed zo". Also use it when the user pastes code and
  asks for feedback.
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "review, code review, pull request, diff, bugs, feedback, nakijken, codekwaliteit"
  version: "1.0.0"
  summary_nl: "Leest je diff, PR of bestand na en geeft bevindingen op ernst gesorteerd, elk met een concrete oplossing."
---

# Code review buddy

A good review catches the bug that would have paged someone at 3 a.m., and skips the twenty nitpicks that drown it out. This skill reviews changes with that priority in mind: correctness first, then robustness, then readability and maintainability, and it always pairs a finding with a fix the author can apply.

## Workflow

1. **Establish what changed and why.** Get the diff rather than whole files when possible (`git diff main...HEAD`, `git diff --staged`, or `gh pr diff 123`). Read the PR description or ask for one sentence of intent. A change can only be judged against what it is supposed to do.
2. **Read the surrounding code.** For every changed function, open its callers and the types it touches. Most real bugs live at the boundary between the new lines and the old ones: a caller that passes `null`, a return value that changed shape.
3. **Pass 1: correctness.** Trace the happy path, then the unhappy ones. Look for off-by-one errors, inverted conditions, missing `await`, unhandled errors, mutation of shared state, wrong units, time zones, and integer or float surprises.
4. **Pass 2: edge cases and robustness.** Empty input, a single item, very large input, unicode, concurrent calls, retries, partial failure, and missing configuration. Ask: what happens the second time this runs?
5. **Pass 3: security and data.** Untrusted input reaching SQL, shell commands, file paths or HTML; secrets in logs; authorization checks that moved or vanished.
6. **Pass 4: readability and maintainability.** Names that lie, functions doing three things, duplicated logic, dead code, missing or misleading comments, tests that do not actually assert the new behaviour.
7. **Rank and trim.** Sort findings by severity and drop anything that is pure taste unless the project's style guide or linter says otherwise. Fewer, sharper findings get acted on.
8. **Verify where cheap.** If tests exist, run them (`npm test`, `pytest`, `go test ./...`) and say whether you did. Never claim tests pass unless you ran them.

## Severity levels

- **Blocker**: wrong results, data loss, crash, security hole. Must be fixed before merge.
- **Major**: likely bug in a realistic edge case, or a design choice that will hurt soon.
- **Minor**: readability, naming, small duplication.
- **Nit**: optional polish. Keep these few, and label them so the author can ignore them.

## Quick checks by kind of change

Different changes hide different bugs, so adjust the focus:

- **Database migrations:** reversible? Safe on a large table without locking it? Default values for existing rows?
- **API or schema changes:** backwards compatible for clients already deployed? Versioned if not?
- **Concurrency and async code:** shared state, ordering assumptions, cancellation, timeouts.
- **Config and feature flags:** sane default when the value is missing; flag removed when no longer needed.
- **Tests only:** do they assert outcomes, and would they fail if the feature broke?
- **Dependency bumps:** lockfile updated, changelog checked for breaking changes.

## Output format

Start with a two-line verdict, then the findings table-free so code snippets stay readable:

```markdown
**Verdict:** Request changes. 1 blocker, 2 major, 1 minor.
**Summary:** Pagination logic is solid; the retry wrapper can double-charge on timeout.

### [Blocker] Retry can repeat a non-idempotent charge (payments/charge.ts:42)
The `withRetry` wrapper retries on timeout, but a timeout does not mean the
charge failed. A slow success followed by a retry charges the customer twice.
**Fix:** pass an idempotency key derived from the order id, or only retry on
connection errors raised before the request is sent.

### [Major] Empty cart returns 500 (cart/total.py:18)
`max(items, key=...)` raises `ValueError` on an empty list.
**Fix:** `if not items: return Decimal("0")` before the call, and add a test.
```

End with a short "What looks good" line. Authors take criticism better when they can see the reviewer actually understood the change, and it tells them what not to change.

## Pitfalls and when to ask

- If the diff is huge (over roughly 800 lines), say so and propose reviewing it in chunks by module or commit, rather than skimming everything.
- If intent is unclear, ask instead of guessing; a bug report against the wrong intent wastes both sides' time.
- Do not rewrite the code wholesale in the review. Show the minimal fix; offer a fuller refactor separately.
- Do not apply fixes to the working tree unless the user asks. A review is advice, and the author stays in charge of their branch.
- Mark uncertain findings as questions ("Is `user` ever undefined here?") rather than stating them as bugs.

## Scope

This skill reviews code. It is not for writing new features, large refactors (see refactor-safely) or writing a test suite from scratch (see unit-test-writer), though it will point out where those are needed.
