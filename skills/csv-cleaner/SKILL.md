---
name: csv-cleaner
description: >-
  Clean messy CSV, TSV or Excel data and write a cleaned copy plus a change log, never touching the
  original. Fixes encodings (UTF-8, Windows-1252, BOM), wrong delimiters, broken or duplicated headers,
  duplicate rows, mixed date formats, Dutch decimal commas, thousands separators, stray whitespace and
  missing values. Use this skill whenever the user shares a spreadsheet or export that "looks weird",
  will not import, has garbled characters, or asks to clean, tidy, deduplicate or standardise data,
  including "maak deze csv schoon", "ontdubbel dit bestand", "de datums kloppen niet" or "opschonen".
license: "MIT"
metadata:
  author: "prompt"
  category: "data"
  tags: "csv, excel, data cleaning, opschonen, deduplicate, encoding, pandas, ontdubbelen"
  version: "1.0.0"
  summary_nl: "Schoont rommelige CSV- en Excel-bestanden op en schrijft een schone kopie met een logboek van alle wijzigingen."
---

# CSV cleaner

Most data problems are boring and predictable: a file saved by Dutch Excel uses semicolons and decimal
commas, an export has two header rows, "Ã©" shows up where "é" belongs. Fixing them is easy; fixing them
without silently changing meaning is the real work. That is why this skill profiles first, asks before
anything destructive, writes to a new file and logs every change.

## Workflow

1. **Copy, do not overwrite.** Read the original and write results to `<name>_clean.csv` (or `.xlsx`)
   next to it, plus `<name>_changelog.md`. The user can always compare or go back.
2. **Sniff the raw file before parsing.** Look at the first bytes and lines:
   - Encoding: a BOM, or bytes that fail as UTF-8, suggest Windows-1252 / Latin-1. Mojibake like `Ã«`
     means UTF-8 was read as Latin-1.
   - Delimiter: count `,` `;` `\t` `|` per line; the one with a stable count wins. Dutch/Belgian Excel
     exports usually use `;`.
   - Header: is row 1 really the header, or is there a title row, blank rows, or a second header line?
3. **Profile each column** and show the user a short table: inferred type, % missing, unique count,
   examples, and suspicious values. This is where you agree on the plan.
4. **Apply fixes in a clear order** (encoding → structure → headers → values → duplicates), because
   deduplicating before trimming whitespace misses duplicates.
5. **Validate**: row counts before and after, no column lost, numeric totals of key columns compared,
   spot-check five random rows against the original.
6. **Write the clean file and change log**, and summarise in chat.

## Common fixes

| Problem | Fix | Watch out |
|---|---|---|
| `1.234,56` (Dutch number) | → `1234.56` | `1.234` alone may be one thousand or 1.234; check the column |
| `€ 12,50`, `12,50 EUR` | strip currency into numeric, note the unit | mixed currencies in one column: stop and ask |
| Dates `03-04-2026`, `2026/4/3`, `3 apr 2026` | → ISO `2026-04-03` | day-first vs month-first: decide per column using values > 12 |
| Excel serial dates `45123` | convert from 1899-12-30 epoch | only if the column is clearly dates |
| Headers `Klant Naam `, `klantnaam`, duplicates | trim, `snake_case`, make unique | keep a mapping old → new in the log |
| Leading zeros lost (postcodes, phone, article numbers) | read as text | never convert IDs to numbers |
| `NULL`, `n/a`, `-`, `?`, empty | unify to empty | do not fill with 0 or a mean unless asked |
| Exact duplicate rows | remove, count them | near-duplicates (case, spacing): report, let the user decide |
| Whitespace, non-breaking spaces | trim | inside values like names, keep single spaces |

A minimal pandas pattern for a Dutch Excel export:

```python
import pandas as pd
df = pd.read_csv("export.csv", sep=";", encoding="cp1252", decimal=",", thousands=".",
                 dtype={"postcode": str, "artikelnr": str})
df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
df["datum"] = pd.to_datetime(df["datum"], dayfirst=True, errors="coerce")
df.to_csv("export_clean.csv", index=False, encoding="utf-8")
```

Use `errors="coerce"` only together with a count of values that became empty, so failures are visible.

## Change log format

```markdown
# Change log: klanten.csv -> klanten_clean.csv
Input: 4,212 rows, 14 columns, cp1252, delimiter ";"
Output: 4,187 rows, 13 columns, UTF-8, delimiter ","

1. Re-encoded cp1252 -> UTF-8 (fixed 38 values like "CafÃ©" -> "Café")
2. Dropped title row "Export 17-10-2026" above the header
3. Renamed columns: "Klant Naam " -> klant_naam, ... (full mapping below)
4. bedrag: decimal comma -> point; 3 values not numeric, left empty (rows 88, 901, 2210)
5. datum: parsed day-first to ISO; 0 failures
6. Removed 25 exact duplicate rows
7. Dropped empty column "Unnamed: 13"
Not changed: 41 near-duplicate customer names (listed in near_duplicates.csv) - your call
```

## When to stop and ask

- A fix would delete rows or columns that contain data (other than exact duplicates and fully empty
  columns).
- A column's meaning is ambiguous: day/month order, units, currencies, or codes you do not recognise.
- More than a few percent of values in a column fail to parse; that usually means a wrong assumption.
- The file holds personal data and the user wants it shared or uploaded somewhere; keep it local.

## Scope

This skill makes data clean and consistent. Analysis and charts come after; see a data exploration or
chart skill. It does not merge multiple sources unless asked, and it does not guess values to fill gaps.
