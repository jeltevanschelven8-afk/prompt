---
name: stress-test-and-fix
description: >-
  Aggressively stress-test the user's own code to find bugs, then fix them. Use this skill whenever the user asks to "break", "attack", "stress-test", "hammer", "push to the limit", "find bugs in", "harden", "make bulletproof", "fuzz", or "try to crash" their code, function, script, module, API, or app — even if they only say something casual like "see if you can break this" or "is this robust?". Also trigger when the user shares code and asks whether it handles edge cases, bad input, large input, or concurrency. The skill covers the full loop: generate hostile inputs, run them, record failures, fix the root cause, and re-run until everything passes.
---

# Stress-test and fix

The goal of this skill is to take a piece of the user's code, throw everything at it that could plausibly go wrong, and then leave the code in a better state than you found it: bugs fixed, regression tests in place, and a clear report of what changed.

Think of it as being the most unreasonable user the code will ever meet — and then being the engineer who cleans up afterwards.

## Scope and safety

This is for code the user owns or is allowed to modify. "Attacking" here means adversarial *testing* of their own software: malformed input, extreme sizes, race conditions, resource exhaustion, and so on. It does not mean building exploits against third-party systems, writing malware, or probing services the user doesn't control. If a request drifts in that direction, say so and stay with testing their own code.

Always run tests in an isolated way (temp directories, in-memory data, mocks for external services). Never run destructive inputs against real databases, real files the user cares about, or live external APIs.

## The loop

Work through these phases in order. Don't skip the first one — most wasted effort comes from attacking code you don't yet understand.

### 1. Understand the target (5 minutes, not 50)

- Read the code and identify its **contract**: what inputs it accepts, what it promises to return, what it promises never to do (crash, corrupt data, hang, leak).
- Identify the **trust boundaries**: where does data enter from outside (user input, files, network, env vars, CLI args)?
- Note the language, runtime, test framework already in use, and how to run the existing tests. Reuse the project's conventions; don't introduce a new test framework if one exists.
- If you can't run the code at all (missing deps, no entry point), fix that first or ask the user — a stress test you can't execute is just speculation.

### 2. Build the attack plan

Write down (briefly, for yourself and the report) the categories you'll attack. Pick the ones that apply; don't force all of them onto a three-line helper function.

**Input shape**
- Empty: `""`, `[]`, `{}`, `None`/`null`, `0`, `-1`
- Wrong type: string where number expected, list where dict expected, float where int expected
- Boundaries: off-by-one at every limit (0, 1, max, max+1, max-1), empty vs single-element collections
- Unicode: emoji, right-to-left text, combining characters, null bytes, very long single "characters", mixed normalisation forms
- Encoding: invalid UTF-8, BOMs, CRLF vs LF, trailing whitespace
- Structure: deeply nested data, circular references, duplicate keys, missing required fields, extra unexpected fields

**Scale**
- Huge inputs: strings of 10 MB, lists of a million items, files bigger than RAM
- Many small operations: call it 100 000 times in a loop and watch memory and time
- Pathological cases for the algorithm: worst-case sort order, hash collisions, regex catastrophic backtracking (`(a+)+$` style), quadratic blow-ups

**Numbers**
- Zero, negative, `NaN`, `±Infinity`, integer overflow at 32/64-bit limits, floats near precision limits, `-0.0`
- Very large and very small magnitudes in the same calculation

**Time and state**
- Calls in the wrong order (close before open, read before init)
- Calling twice, calling after failure, calling after cancel
- Clock edge cases: leap years, DST transitions, timezone-less timestamps, epoch 0, year 2038, year 10000

**Concurrency** (if the code is used concurrently)
- Same operation from N threads/tasks at once
- Shared mutable state, check-then-act races, double initialisation

**Environment and resources**
- Missing files, read-only directories, disk full, permission denied
- Network timeouts, partial responses, connection reset mid-stream (mock these)
- Missing env vars, env vars with surprising values
- Slow dependencies: what happens when a call takes 30 seconds?

**Injection-style inputs** (for anything that builds strings for another interpreter)
- Path traversal (`../../etc/passwd`), shell metacharacters, SQL quotes, format-string specifiers, HTML/JS in text fields, newlines in log messages

### 3. Attack

- Write the stress tests as real test files in the project's test framework, not as throwaway REPL snippets. They become the regression suite.
- For input-shape attacks, property-based / fuzz testing beats hand-written cases when available (`hypothesis` for Python, `fast-check` for JS/TS, `proptest` for Rust, `go-fuzz`/native fuzzing for Go). Use it if the project already has it or it's a cheap, obvious addition; otherwise hand-write a dense table of cases.
- Put time and memory limits on every test so a hang or leak shows up as a failure instead of a frozen terminal.
- Run everything. Capture: the input, the expected behaviour, the actual behaviour (exception, wrong value, hang, memory spike), and a minimal reproduction.
- Keep a running **findings list** as you go. Each finding gets a severity:
  - **Critical**: data loss/corruption, security hole, crash on realistic input
  - **High**: crash or wrong result on unusual-but-plausible input, unbounded resource use
  - **Medium**: wrong result on genuinely exotic input, poor error messages
  - **Low**: cosmetic, inconsistency, missing validation that's harmless

### 4. Fix

Now switch hats from attacker to engineer.

- **Fix the root cause, not the symptom.** If a function crashes on `None`, ask why `None` reaches it at all. Sometimes the right fix is validation at the trust boundary, not a null-check in every function.
- **One finding, one change, one test.** Each fix should be small, reviewable, and covered by the regression test that found it. Don't bundle a refactor into a bug fix.
- **Preserve behaviour the user relies on.** Rerun the existing test suite after every fix. If the existing tests break, your fix changed the contract — stop and check with the user before continuing.
- **Fail loudly over failing silently.** Prefer raising a clear, specific error for invalid input over returning a default that hides the problem — unless the code's contract is explicitly lenient.
- **Don't fix what you shouldn't.** Some "bugs" are deliberate design decisions or out of scope. If a fix would require changing a public interface, touching code outside the target, or making a judgment call about intended behaviour, list it under "needs decision" in the report instead of guessing.
- Order fixes by severity. If there are many, fix critical and high, then ask whether to continue.

### 5. Verify and repeat

- Rerun the full stress suite plus the existing tests. Everything green.
- Then do one more attack round on the code you just changed — fixes introduce bugs too. Pay special attention to the error-handling paths you added, which are the least-exercised code in most projects.
- Stop when a full round finds nothing new, or when only "needs decision" items remain.

### 6. Report

End with a short report. Use this structure:

```
## Stress test report: <target>

**Rounds:** N  **Tests added:** N  **Findings:** N (C critical, H high, M medium, L low)

### Fixed
- [Critical] <one-line description> — <file:line> — covered by <test name>
- ...

### Needs your decision
- <finding> — <why I didn't just fix it> — <options>

### Survived
Categories attacked that held up fine: <list>, so the user knows what *was* checked.

### How to run
<exact command to run the new tests>
```

Keep it factual. The user should be able to read the report in under a minute and know exactly what changed and what still needs a call from them.

## Tone and judgement

- Be proportionate. A three-line utility function gets a focused table of twenty cases, not a four-hour fuzzing campaign. A payment-handling module gets the full treatment.
- Don't pad the findings list. Ten real bugs beat forty "could theoretically" items.
- When you're unsure whether something is a bug or intended, say so and ask — in the report, not by stopping the whole run.
- If the code is in a language or framework you can't execute in the current environment, say that upfront, write the tests anyway, and give the user the command to run them.
