---
name: regex-helper
description: >-
  Write, explain, debug and test regular expressions. Produces a pattern with a
  plain-language breakdown, a table of strings that should and should not
  match, actual test runs, and notes on differences between regex flavours such
  as JavaScript, Python, PCRE, Go, Java, .NET and grep or sed. Use this skill
  whenever the user asks for a regex, wants to validate or extract text with a
  pattern, pastes a cryptic regex and asks what it does, or says my regex does
  not match, and for Dutch phrases like "maak een regex voor", "wat doet deze
  regex" or "waarom matcht dit niet".
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "regex, regular expressions, pattern matching, validation, parsing, testen, reguliere expressies, tekst zoeken"
  version: "1.0.0"
  summary_nl: "Schrijft, verklaart en test reguliere expressies, met voorbeelden die wel en niet matchen per programmeertaal."
---

# Regex helper

Regular expressions are easy to write and hard to trust. A pattern that matches the three examples you thought of often also matches things you did not want, or misses valid input. This skill treats every regex like code: clear requirements, explained structure, and test cases that prove both what it matches and what it rejects.

## Workflow

1. **Pin down the requirements.** Ask or infer: which language or tool runs it, is it validating a whole string or finding matches inside text, should it be case sensitive, multiline input or single line, and what is the source of the text. These change the pattern more than people expect.
2. **Collect examples.** Gather at least three strings that must match and three that must not, including the tricky ones (empty string, extra whitespace, unicode, near misses). Propose them if the user has none.
3. **Write the simplest pattern that works.** Prefer readable over clever. Anchor validation patterns with `^...$` (or `\A...\z` where available) so partial matches do not slip through. Use non-capturing groups `(?:...)` unless the capture is needed, and named groups `(?<year>\d{4})` when extracting.
4. **Explain it piece by piece.** Break the pattern into tokens with a one-line meaning each, so the user can maintain it later.
5. **Test it for real.** Run the cases instead of eyeballing them, for example:
   ```bash
   python -c "import re; p=re.compile(r'^\d{4}\s?[A-Z]{2}$'); print([(s, bool(p.match(s))) for s in ['1234 AB','1234AB','123 AB','1234 ab']])"
   node -e "const r=/^\d{4}\s?[A-Z]{2}$/; for (const s of ['1234 AB','1234ab']) console.log(s, r.test(s))"
   ```
   Report the actual output. If you could not run anything, say the results are expected, not verified.
6. **Check for performance traps.** Nested quantifiers like `(a+)+`, `(.*)*` or alternations with overlapping branches can cause catastrophic backtracking on long non-matching input. Test with a long near-miss string and rewrite with possessive quantifiers, atomic groups or tighter character classes if needed.
7. **Give the final pattern in the exact syntax of the target**, escaped correctly for the string literal (raw strings in Python, double backslashes in Java and C# regular strings, slash delimiters in JavaScript).

## Flavour notes worth checking

- **JavaScript:** lookbehind supported in modern engines; `u` flag needed for proper unicode and `\p{L}`; `v` flag in newest engines. No possessive quantifiers.
- **Python `re`:** `re.match` anchors at start only; use `re.fullmatch` for whole-string validation. `\d` matches all unicode digits unless `re.ASCII`.
- **Go (RE2):** no backreferences or lookaround, but guaranteed linear time.
- **PCRE / PHP, Java, .NET:** lookaround, possessive quantifiers and atomic groups available (.NET has no possessive quantifiers, use atomic groups).
- **grep / sed:** basic regex by default; use `grep -E` or `sed -E` for `+`, `?`, `|` and `()` without backslashes. `\d` is not supported in POSIX classes; use `[0-9]`.

## Output format

```markdown
**Pattern (Python):** r"^(?P<num>\d{4})\s?(?P<letters>[A-Z]{2})$"

| Part | Meaning |
|---|---|
| ^ | start of string |
| (?P<num>\d{4}) | exactly four digits, captured as num |
| \s? | optional single space |
| (?P<letters>[A-Z]{2}) | two uppercase letters |
| $ | end of string |

| Input | Expected | Result |
|---|---|---|
| 1234 AB | match | match |
| 1234AB | match | match |
| 123 AB | no match | no match |
| 1234 ab | no match | no match |

Tested with Python 3.12. Add re.IGNORECASE to accept lowercase letters.
```

## Pitfalls and when to ask

- Some formats should not be parsed with regex at all: HTML, nested JSON, full email address validation per the RFC, dates with calendar rules. Say so and suggest a parser or library, while still offering a pragmatic pattern if the user wants one.
- Do not silently widen or narrow the requirement. If a case is ambiguous (is `1234ab` valid?), ask.
- When fixing a user's broken regex, show the smallest change and explain why the old one failed.

## Scope

For pattern work. Bulk find-and-replace across a codebase is fine to support with a pattern, but confirm with the user before running any replacement that edits files.
