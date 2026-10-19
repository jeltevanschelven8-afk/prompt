---
name: debug-detective
description: >-
  Systematic debugging that finds the root cause instead of patching symptoms.
  Starts from an error message, stack trace, failing test or a vague it does not
  work, then reproduces the problem, isolates it, forms and tests hypotheses one
  at a time, fixes the real cause and adds a regression test. Use this skill
  whenever the user pastes an error or traceback, says something broke, it
  worked yesterday, I get an exception, this test fails, or uses Dutch phrases
  such as "waarom werkt dit niet", "ik krijg een foutmelding", "help me debuggen"
  or "het is kapot".
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "debugging, bug, error, stack trace, exception, root cause, foutmelding, fout zoeken, werkt niet"
  version: "1.0.0"
  summary_nl: "Zoekt systematisch de echte oorzaak van een fout: reproduceren, isoleren, hypotheses testen en duurzaam oplossen."
---

# Debug detective

Most debugging time is lost to guessing: changing things until the error goes away, without knowing why. This skill replaces guessing with a loop of evidence: reproduce, narrow down, state a hypothesis, test it, and only then fix. The fix targets the cause, and a test keeps the bug from coming back.

## Workflow

1. **Collect the evidence.** Get the full error message and stack trace, not a paraphrase. Ask: what did you do, what did you expect, what happened instead, since when, and what changed recently (deploy, dependency update, config, data)? Note versions and environment.
2. **Read the stack trace properly.** Find the first frame in the user's own code, not the deepest library frame. The exception type and message often say exactly what is wrong (`KeyError: 'email'`, `Cannot read properties of undefined (reading 'map')`). Check for "caused by" or chained exceptions; the original cause is usually at the bottom of a Java trace and at the top of a chained Python one.
3. **Reproduce it.** Find the smallest reliable way to trigger the bug: a single test, a curl request, a script with fixed input. Run it and confirm you see the same error. If you cannot reproduce it, that is information too: look at environment, data, timing and concurrency differences.
4. **Isolate.** Shrink the search space:
   - Cut the input down until the bug disappears, then add back the last piece.
   - Use `git bisect` when it used to work: `git bisect start`, `git bisect bad`, `git bisect good <commit>`, then test each step.
   - Add targeted logging or a breakpoint at the boundary where data is last known good and first known bad.
5. **Hypothesise one cause at a time.** Write it down: "The list is empty because the API now returns `data.items` instead of `items`." Predict what you would see if it were true, then check that prediction. Changing several things at once makes it impossible to know which one mattered.
6. **Fix the root cause.** Ask "why" until you reach something that would prevent the whole class of bug, but stay proportionate. Prefer fixing the source of bad data over adding null checks wherever it is used. Keep the fix minimal and focused.
7. **Prove it.** Write a regression test that fails before the fix and passes after. Run the original reproduction and the related test suite. Report what you actually ran.
8. **Clean up.** Remove temporary logging, debug prints and breakpoints.

## Common culprits worth checking early

- Off-by-one and boundary conditions; empty collections
- `null`, `undefined`, `None` from an unexpected path
- Async issues: missing `await`, unhandled promise, race between two writers
- Stale caches, build artifacts or a server that was not restarted
- Environment differences: env vars, time zone, locale, file path separators, case-sensitive file systems
- Dependency version drift; check the lockfile diff
- Data that violates an assumption (duplicates, unicode, very large values)

## When the bug will not reproduce

Intermittent and works-on-my-machine bugs need a different angle:

- Compare environments side by side: runtime version, env vars, OS, locale, data set, feature flags.
- Add structured logging with request ids around the suspect area and wait for the next occurrence, rather than guessing.
- Look for timing: run the test in a loop (`for i in $(seq 50); do npm test -- foo.spec.ts || break; done`) or under load to surface races.
- Check whether tests depend on order or shared state by running the failing test alone and in random order.
- Ask the user for the exact input or a sanitized sample of the data that triggered it.

## Output format

```markdown
**Symptom:** `TypeError: Cannot read properties of undefined (reading 'map')` on /orders page.
**Reproduction:** `npm test -- orders.spec.ts` fails; also visible with an account with no orders.
**Root cause:** `fetchOrders` returns `undefined` when the API responds 204 No Content;
the component assumes an array. Introduced in commit a1b2c3d when the API changed.
**Fix:** `fetchOrders` now returns `[]` for 204 (src/api/orders.ts:31).
**Regression test:** `returns empty list on 204` in orders.spec.ts. Fails before, passes after.
**Verified:** ran orders.spec.ts and the full unit suite, all green.
**Related risks:** two other fetchers use the same pattern; listed below.
```

## Pitfalls and when to ask

- Do not wrap the failing line in try/catch to make the error vanish; that hides the bug and usually creates a worse one.
- If reproducing needs production data, real customer accounts or destructive actions, ask the user first and prefer a sanitized copy.
- If several hypotheses remain and testing them is expensive, present them ranked by likelihood and ask which to pursue.
- Be honest about confidence. "Likely cause, not yet confirmed" is better than a confident wrong answer.

## Scope

For finding and fixing defects. Slow but correct code belongs to performance-tuner; code that works but is messy belongs to refactor-safely.
