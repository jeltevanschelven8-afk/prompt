---
name: refactor-safely
description: >-
  Refactor existing code in small, behaviour-preserving steps, using tests as a
  safety net and committing after each green step, so the code gets cleaner
  without anything breaking. Use this skill whenever the user wants to clean up,
  restructure, simplify, split up, rename, deduplicate or untangle code, says
  this function is too long, make this readable, get rid of this mess, or types
  Dutch phrases like "refactor dit", "maak dit netter", "deze code opschonen" or
  "dit is spaghetticode". It keeps refactoring strictly separate from feature
  changes and bug fixes.
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "refactor, refactoring, clean code, tests, technical debt, opschonen, herstructureren, onderhoudbaarheid"
  version: "1.0.0"
  summary_nl: "Herstructureert je code in kleine, veilige stappen met tests als vangnet, zonder dat het gedrag verandert."
---

# Refactor safely

Refactoring means changing the structure of code without changing what it does. The danger is that a big rewrite quietly changes behaviour and nobody notices until production. This skill avoids that by moving in tiny steps, each one checked by tests, so that if something breaks you know exactly which step did it.

## Workflow

1. **Agree on the goal.** Ask what hurts: too long, duplicated, hard to test, hard to extend for an upcoming feature? A clear goal decides which refactorings are worth doing and when to stop.
2. **Check the safety net.** Find and run the existing tests for the code in question (`npm test -- path`, `pytest tests/test_orders.py`, `go test ./orders/...`). Note the result. If they already fail, stop and tell the user; refactoring on a red baseline hides new breakage.
3. **Add characterization tests if coverage is thin.** Write tests that pin down what the code does today, including odd behaviour. They are not about what it should do; they are a tripwire. Mark surprising behaviour in a comment and mention it to the user rather than fixing it now.
4. **Make sure the working tree is clean.** `git status` should show nothing unrelated, so each step can be committed or reverted on its own.
5. **Plan a sequence of small steps.** Use named refactorings so each step is well understood:
   - Rename variable, function or file
   - Extract function or method; inline function
   - Introduce parameter object; replace magic number with named constant
   - Replace conditional chain with lookup table or polymorphism
   - Move function to the module where its data lives
   - Split a module; remove dead code (after confirming with search that it is unused)
   Share the plan before starting if it touches more than a couple of files.
6. **Execute one step at a time.** Make the change, run the tests, and commit with a message such as `refactor: extract parseLineItem from importOrders`. If tests go red, revert that step (`git checkout -- .` or `git restore .`) and take a smaller one, instead of debugging a tangle.
7. **Keep public behaviour identical.** Same inputs, same outputs, same errors, same side effects, same public signatures unless the user agreed to change them. If a signature must change, update every caller in the same step.
8. **Finish with a review.** Run the full test suite and linter once more and show the overall diff summary (`git diff --stat` from the starting point).

## Keep refactor and feature work apart

Mixing a refactor with a behaviour change makes both impossible to review: a reviewer cannot tell whether a changed output is intentional. If you spot a bug mid-refactor, write it down and report it, finish or pause the refactor, then fix the bug in a separate commit with its own test. The same applies to new features: refactor first to make the change easy, then make the easy change.

## Example step

Before:

```python
def total(order):
    t = 0
    for i in order["items"]:
        t += i["price"] * i["qty"] * (1 - i.get("discount", 0))
    return round(t * 1.21, 2)
```

After two steps (extract function, then name the constant), tests green after each:

```python
VAT_RATE = 0.21

def line_total(item):
    return item["price"] * item["qty"] * (1 - item.get("discount", 0))

def total(order):
    return round(sum(line_total(i) for i in order["items"]) * (1 + VAT_RATE), 2)
```

## Output to the user

After finishing, report:

- **Goal** and whether it was reached
- **Steps taken**, one line each, matching the commits
- **Test status**: which suites ran and their result, or clearly state that tests were not run and why
- **Found but not fixed**: bugs or oddities discovered and left for a separate change
- **Suggested next steps**, if the refactor was deliberately stopped early

## Pitfalls and when to ask

- No tests and the code is hard to test: propose the smallest seam (for example extracting a pure function) and ask before going further.
- The refactor would touch a public API, database schema or file format: ask first; that is a migration, not a refactor.
- Generated code, vendored libraries or lockfiles: leave them alone.
- Formatting churn hides real changes. Run the formatter in its own commit, if at all.
- If the user wants a full rewrite, explain the risk and offer the incremental route; respect their choice.

## Scope

Not for adding features, fixing bugs, or performance work (see performance-tuner). Use code-review-buddy if the user only wants an opinion on what to refactor.
