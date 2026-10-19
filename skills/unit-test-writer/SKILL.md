---
name: unit-test-writer
description: >-
  Write meaningful unit tests for existing code that check behaviour rather
  than implementation details, cover edge cases and error paths, follow
  arrange-act-assert, and match the framework and conventions the project
  already uses (Jest, Vitest, pytest, JUnit, xUnit, Go testing, RSpec and so
  on). Use this skill whenever the user asks to write tests, add test coverage,
  test this function, says there are no tests for this, or wants to know what to
  test, and for Dutch phrases such as "schrijf tests voor", "voeg unit tests
  toe" or "hoe test ik dit".
license: "MIT"
metadata:
  author: "prompt"
  category: "testing"
  tags: "unit tests, testing, jest, pytest, coverage, edge cases, tdd, testen, testdekking"
  version: "1.0.0"
  summary_nl: "Schrijft zinvolle unit tests voor bestaande code: gedrag in plaats van implementatie, randgevallen en de testtool van je project."
---

# Unit test writer

A good test fails when the behaviour breaks and keeps passing when someone refactors the internals. Tests that mirror the implementation line by line do the opposite: they break on every cleanup and miss real bugs. This skill writes tests from the outside in, based on what the code promises, and fits them into the project as if a teammate wrote them.

## Workflow

1. **Learn the project's testing setup.** Find the framework, file layout and naming (`*.test.ts` beside the source, `tests/test_*.py`, `src/test/java`), shared fixtures, factories and helpers, and the command that runs tests (`package.json` scripts, `pytest.ini`, `Makefile`). Read two or three existing tests and copy their style. If there are no tests yet, propose the standard framework for the stack and ask before adding it.
2. **Understand the behaviour of the unit.** Read the code, its callers and its docs. Write a short list of what it promises: given this input, it returns or does that. Note side effects (writes, calls, events) and failure modes (exceptions, error returns).
3. **Design the cases before writing code.** For each behaviour:
   - Typical case
   - Boundaries: zero, one, many; empty string; min and max values; just over a limit
   - Invalid input and error paths: wrong type, missing field, the exception message or error type
   - Special data: unicode, time zones and dates around midnight or DST, negative numbers, duplicates
   - State and order: calling twice, idempotency
   Share the list when the unit is large so the user can add domain cases you cannot know.
4. **Write each test as arrange, act, assert.** One behaviour per test, with a name that reads as a sentence: `returns_zero_for_empty_cart`, `it('rejects an expired coupon')`. Keep setup visible in the test or in a clearly named helper, so a failure is readable without jumping around.
5. **Use test doubles sparingly.** Mock things at the edge of the unit that are slow or non-deterministic: network, clock, randomness, file system, external services. Do not mock the unit's own internal helpers; that ties the test to the implementation. Prefer fakes and fixed clocks (`vi.useFakeTimers()`, `freezegun`, an injected clock) over deep mock chains.
6. **Assert on outcomes.** Check return values, resulting state and observable calls at the boundary. Assert specific values, not just "is truthy". Use parameterized tests (`it.each`, `pytest.mark.parametrize`, `@ParameterizedTest`) for tables of inputs.
7. **Run them and see them fail for the right reason.** Run the new tests. Then briefly break the code under test (for example flip a comparison) to confirm at least the key tests fail, and restore it. A test that cannot fail protects nothing.
8. **Report findings.** If a test reveals a bug, do not change the test to match the bug. Leave it failing or mark it as an expected failure, and tell the user.

## Example (pytest)

```python
import pytest
from shop.pricing import apply_coupon, CouponExpired

@pytest.mark.parametrize("total, pct, expected", [
    (100, 10, 90),
    (0, 50, 0),
    (19.99, 100, 0),
])
def test_apply_coupon_reduces_total_by_percentage(total, pct, expected):
    coupon = make_coupon(percent=pct)

    result = apply_coupon(total, coupon)

    assert result == pytest.approx(expected)

def test_apply_coupon_rejects_expired_coupon(fixed_today):
    coupon = make_coupon(percent=10, expires=fixed_today.replace(day=1))

    with pytest.raises(CouponExpired):
        apply_coupon(100, coupon)
```

## Output to the user

- Files added or changed, and the command to run them
- The case list, grouped by behaviour
- Actual run result (passed, failed, skipped counts), or a clear statement that tests were not run
- Bugs or unclear behaviour discovered, with the failing test that shows it
- Gaps left on purpose (for example integration paths better covered elsewhere)

## Pitfalls and when to ask

- Chasing a coverage percentage leads to tests that execute code without checking anything. Aim for behaviours covered, not lines touched.
- Snapshot tests of large objects are brittle; use them only for stable output like rendered markup, and keep them small.
- Code that is hard to test (hidden globals, `new Date()` inside, direct network calls) may need a small seam. Ask before refactoring production code to make it testable.
- Do not change production behaviour to make a test pass.

## Scope

Unit tests for existing code. End-to-end and load testing need different tools; test strategy for a whole system is a broader conversation.
