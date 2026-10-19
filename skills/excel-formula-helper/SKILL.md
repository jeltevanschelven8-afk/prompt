---
name: excel-formula-helper
description: >-
  Write, fix and explain Excel and Google Sheets formulas, from simple SUM and IF to XLOOKUP, SUMIFS,
  INDEX/MATCH, FILTER, UNIQUE, LET, conditional formatting rules and pivot tables. Translates between
  English and Dutch function names (VERT.ZOEKEN, ALS, SOM.ALS, X.ZOEKEN) and the semicolon separator
  Dutch Excel uses. Use this skill whenever the user asks for a formula, gets an error like #N/A,
  #VALUE! or #REF!, wants a pivot table, or types "welke formule moet ik gebruiken", "hoe doe ik een
  vert.zoeken", "mijn formule werkt niet" or "help met Excel", even if they describe the goal loosely.
license: "MIT"
metadata:
  author: "prompt"
  category: "data"
  tags: "excel, google sheets, formulas, formules, xlookup, vert.zoeken, spreadsheet, draaitabel"
  version: "1.0.0"
  summary_nl: "Schrijft en legt Excel- en Google Sheets-formules uit, ook met Nederlandse functienamen zoals VERT.ZOEKEN."
---

# Excel formula helper

People rarely need "a formula"; they need a result in a cell that keeps working when rows are added.
This skill writes the formula in the user's own language and locale, explains it in a sentence, and
points out where it can break. A formula that works today but fails on row 1001 is not a fix.

## Workflow

1. **Pin down the setup.** Ask or infer: Excel or Google Sheets, which version (Microsoft 365 has
   XLOOKUP, FILTER, LET; Excel 2016 does not), language (Dutch Excel uses Dutch function names and `;`
   as the argument separator), and the layout (sheet names, columns, header row, whether data is an
   Excel Table).
2. **Restate the goal in one line** using their column names: "For each order in column A, find the
   customer's region from sheet Klanten."
3. **Write the formula** in the user's locale, with the English version alongside if useful. Prefer
   structured references (`Tabel1[Bedrag]`) or whole-column ranges over fixed ranges like `A2:A500`,
   so the formula survives new data.
4. **Explain it** piece by piece, briefly. The user should be able to adapt it next time.
5. **Mention edge cases**: not found, blanks, text that looks like numbers, duplicates in the lookup.
6. **Suggest a simpler path** when one exists (a pivot table instead of 40 SUMIFS, Power Query for
   repeated cleanup).

## Dutch / English names that come up most

| English | Dutch | English | Dutch |
|---|---|---|---|
| IF | ALS | VLOOKUP | VERT.ZOEKEN |
| IFERROR | ALS.FOUT | XLOOKUP | X.ZOEKEN |
| SUMIFS | SOMMEN.ALS | INDEX / MATCH | INDEX / VERGELIJKEN |
| COUNTIFS | AANTALLEN.ALS | TEXT | TEKST |
| AND / OR | EN / OF | TODAY | VANDAAG |
| LEFT / RIGHT / MID | LINKS / RECHTS / DEEL | ROUND | AFRONDEN |
| UNIQUE / FILTER / SORT | UNIEK / FILTER / SORTEREN | CONCATENATE / TEXTJOIN | TEKST.SAMENVOEGEN / TEKST.COMBINEREN |

Google Sheets always uses English function names; its separator follows the spreadsheet's locale
setting (`;` for a Dutch locale).

## Examples

Look up a region, with a friendly message if not found:

```
NL:  =X.ZOEKEN(A2; Klanten!A:A; Klanten!C:C; "niet gevonden")
EN:  =XLOOKUP(A2, Klanten!A:A, Klanten!C:C, "not found")
```

Without XLOOKUP (older Excel): `=ALS.FOUT(INDEX(Klanten!C:C; VERGELIJKEN(A2; Klanten!A:A; 0)); "niet gevonden")`.
The `0` asks for an exact match; leaving it out is the most common cause of wrong lookups.

Total revenue for region Noord in 2026:

```
=SOMMEN.ALS(D:D; B:B; "Noord"; C:C; ">="&DATUM(2026;1;1); C:C; "<"&DATUM(2027;1;1))
```

## Error clinic

| Error | Usual cause | Fix |
|---|---|---|
| #N/A | value not found; extra spaces; number stored as text | `SPATIES.WISSEN` (TRIM), `WAARDE` (VALUE), check exact match |
| #VALUE! | text in a calculation, wrong separator | check cells with `ISGETAL`, use `;` in Dutch Excel |
| #REF! | deleted rows/columns or a sheet referenced | rebuild the reference, prefer Tables |
| #NAME? | function not in this version or wrong language name | use the table above, check version |
| #SPILL! | dynamic array blocked by cells below | clear the spill range |
| Wrong total, no error | numbers stored as text, hidden rows, relative refs shifted | check `$` anchors and number format |

## Pivot tables

When the user wants totals by category and period, a pivot table (draaitabel) is usually faster and
less error-prone than formulas. Give the steps: select the data (preferably an Excel Table), Insert >
PivotTable, drag the category to Rows, the date to Columns (grouped by month or year), the amount to
Values (Sum). Mention that pivots need a refresh after data changes.

## Output format

```
Formula (Dutch Excel, cell E2):
=X.ZOEKEN(A2; Klanten!A:A; Klanten!C:C; "niet gevonden")

What it does: looks up the customer number from A2 in column A of Klanten and returns the region in C.
Copy down: yes, A2 adjusts per row.
Watch out: customer numbers stored as text in one sheet and as numbers in the other won't match.
```

## When to stop and ask

If the layout is unclear (which sheet, which column holds what) ask for a screenshot or the header row
rather than guessing cell references. If the user shares a workbook, edit a copy and say which cells
changed.

## Scope

Formulas, functions, conditional formatting, data validation and pivot tables. VBA macros and Apps
Script are a step further; offer them only when formulas genuinely cannot do the job.
