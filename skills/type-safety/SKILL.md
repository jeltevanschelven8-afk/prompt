---
name: type-safety
description: >-
  Add or tighten static types in TypeScript or Python (type hints with mypy or
  pyright), step by step, without drowning the codebase in any or ignore
  comments. Turns on stricter checks gradually, types the boundaries first,
  narrows unknown data properly, and fixes the real bugs the type checker
  uncovers. Use this skill whenever the user wants to add types, enable strict
  mode, migrate JavaScript to TypeScript, fix type errors, get rid of any, or
  set up mypy, and for Dutch phrases such as "voeg types toe", "maak dit type
  safe" or "los deze typefouten op".
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "typescript, types, mypy, pyright, type hints, strict mode, typering, typefouten"
  version: "1.0.0"
  summary_nl: "Voegt stap voor stap types toe of maakt ze strenger in TypeScript of Python, en lost echte typefouten op."
---

# Type safety

Types pay off when they describe what the code really does, and they backfire when they are bolted on with `any` everywhere just to silence the checker. This skill adds types gradually, starting where they catch the most bugs (the boundaries where data enters), and treats every type error as a question: is the type wrong, or is the code wrong?

## Workflow

1. **Assess the starting point.** Check the current config and how noisy a stricter run would be:
   - TypeScript: read `tsconfig.json`, then `npx tsc --noEmit` and count errors.
   - Python: look for `mypy.ini`, `pyproject.toml` `[tool.mypy]` or `pyrightconfig.json`, then run `mypy .` or `pyright`.
   Also count escape hatches: `grep -rn ": any\|as any" src | wc -l`, or `type: ignore` in Python.
2. **Agree on a target and pace.** Strict everywhere at once can produce hundreds of errors. Propose a ramp, for example: enable `strict` for new and touched files, or turn on one flag at a time (`noImplicitAny`, then `strictNullChecks`, then the rest). For mypy, use per-module overrides so strict modules can grow over time.
3. **Type the boundaries first.** Function signatures of public modules, API responses, configuration, database rows, message payloads. Internal locals can usually be inferred. Untyped data from outside should enter as `unknown` (TS) or `object` / `Any` held at the edge, then be validated and narrowed once, for example with zod, pydantic, or a hand-written type guard.
4. **Fix errors one category at a time.** Group by error code (`TS2532`, mypy `[union-attr]`) and work through similar errors together; the fix pattern repeats.
5. **For each error, decide who is wrong.** Many errors are real bugs: a value that can be `null`, a missing case in a union, a wrong argument order. Fix the code in those cases and tell the user what you found. If the type is wrong, fix the type.
6. **Use precise tools instead of escape hatches.**
   - Narrowing: `if (x == null) return`, `in` checks, `isinstance`, discriminated unions with a `kind` field
   - Exhaustiveness: `const _never: never = value` in a default branch; `assert_never` in Python
   - Generics instead of `any` for containers and helpers
   - `Literal`, `TypedDict`, `Protocol`, `dataclass` in Python; `satisfies`, `as const`, utility types in TS
   - When an escape hatch is truly needed (bad third-party typings), keep it local, add a comment explaining why, and prefer `unknown` or `cast` at one spot over `any` leaking through
7. **Run tests and the checker again.** Type changes should not change runtime behaviour, except deliberate bug fixes. Report the error count before and after.
8. **Lock in the gain.** Suggest adding the type check to CI (`tsc --noEmit`, `mypy`) so new code does not regress, and a lint rule such as `@typescript-eslint/no-explicit-any` set to warn.

## Example

Before:

```ts
function total(items: any) {
  return items.reduce((s: any, i: any) => s + i.price * i.qty, 0);
}
```

After:

```ts
interface LineItem { price: number; qty: number }

function total(items: readonly LineItem[]): number {
  return items.reduce((sum, i) => sum + i.price * i.qty, 0);
}
```

The checker then flagged a caller passing `order.items ?? null`, a real bug when an order had no items.

## Output format

```markdown
**Scope:** src/billing (12 files)
**Checker:** tsc --noEmit with strict. Errors: 87 before, 0 after.
**Escape hatches:** any 41 to 2 (both in vendor typings shim, commented)
**Real bugs found:** 3
- invoice.ts:58 discount could be undefined, produced NaN totals
- ...
**Config changes:** strict: true for src/billing via project reference
**Tests:** npm test, all green
```

## Pitfalls and when to ask

- Ask before flipping `strict` for the whole project if it produces a large error count; agree on a ramp instead.
- Do not change runtime behaviour silently to satisfy the checker. Call out every behavioural fix.
- Missing type packages (`@types/...`, `types-requests`) are dependencies; ask before installing.
- Avoid overly clever types. If a conditional type takes a paragraph to explain, a simpler signature is usually better.

## Scope

Static typing for TypeScript and Python. The ideas carry over to Flow, PHPStan or Sorbet, but commands differ. Runtime validation libraries are used here only at boundaries.
