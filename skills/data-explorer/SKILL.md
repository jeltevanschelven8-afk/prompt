---
name: data-explorer
description: >-
  Run a quick exploratory data analysis (EDA) on a dataset such as a CSV, Excel file, database table or
  dataframe. Reports shape, column types, missing values, distributions, outliers, correlations and
  group differences, makes a handful of clear charts, and ends with plain-language findings and next
  questions. Use this skill whenever the user shares data and asks "what's in this", "explore this
  dataset", "any interesting patterns", "give me an overview", or types "analyseer deze data", "wat valt
  op in deze dataset", "verken dit bestand" or "maak een eerste analyse", even without saying EDA.
license: "MIT"
metadata:
  author: "prompt"
  category: "data"
  tags: "eda, data analysis, exploratory, pandas, statistics, data-analyse, verkennen, inzichten"
  version: "1.0.0"
  summary_nl: "Maakt een snelle verkennende analyse van je dataset met grafieken en bevindingen in gewone taal."
---

# Data explorer

The point of a first look at data is to learn what is there, what is wrong with it, and which questions
are worth asking next, before anyone builds a model or a dashboard on top of it. A good EDA is short,
honest about data quality, and written so a non-analyst can follow the findings.

## Workflow

1. **Ask for the question, if there is one.** "Why did sales drop in Q3?" focuses the analysis far more
   than "explore". Without a question, do a general pass and propose questions at the end.
2. **Load safely.** Read the file without modifying it. Detect delimiter, encoding, decimal comma and
   header row; keep ID-like columns (postcodes, article numbers) as text. If loading needs heavy
   cleaning, say so and suggest cleaning first.
3. **Structure overview.** Rows, columns, what one row represents (an order? a customer per month?),
   column types, memory size, date range. Getting the grain right prevents most wrong conclusions.
4. **Data quality.** Missing values per column, duplicates, impossible values (negative ages, dates in
   the future), constant columns, suspicious spikes at round numbers or defaults like `1900-01-01`.
5. **Univariate.** For numeric columns: count, mean, median, min, max, quartiles, skew. For categories:
   top values with counts and the long tail. Medians matter when distributions are skewed (incomes,
   order values).
6. **Relationships.** Correlations between numeric columns (Spearman when skewed), key metrics split
   by the main categories, trends over time if there is a date. Look for Simpson's-paradox-style
   reversals when grouping.
7. **Outliers.** Flag with IQR (below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR) or a domain rule, then
   look at the actual rows. Report them; do not drop them, since outliers are often the most important
   records (fraud, errors, top customers).
8. **Charts.** Make 3-6, each answering a question: histogram for a key metric, bar chart of top
   categories, line over time, scatter for the strongest relationship, missing-value overview.
9. **Write findings** in the format below.

## Starter code (pandas)

```python
import pandas as pd
df = pd.read_csv("data.csv")
print(df.shape); print(df.dtypes)
print(df.isna().mean().sort_values(ascending=False).head(10))
print(df.describe(include="all").T)
print(df.duplicated().sum(), "duplicate rows")
num = df.select_dtypes("number")
print(num.corr(method="spearman").round(2))
```

Adapt to what is available: SQL `GROUP BY` queries for a database table, or Excel pivot tables if the
user works in a spreadsheet.

## Output format

```
Dataset: verkopen_2025.csv - 18,240 rows x 11 columns, one row = one order line
Period: 2025-01-02 to 2025-12-30

Data quality
- korting: 34% missing (seems empty when no discount, not unknown - please confirm)
- 12 orders with negative quantity (returns?)

Findings
1. Revenue is concentrated: top 20 customers = 61% of revenue.
2. Average order value dropped from EUR 84 (H1) to EUR 71 (H2); order count stayed flat.
3. Region Noord has 2x the return rate of other regions (8.1% vs 3.9%).

Charts: omzet_per_maand.png, top_klanten.png, retouren_per_regio.png

Next questions
- Is the H2 drop driven by product mix or by discounts?
- What explains returns in Noord: one product, one carrier?
```

## Pitfalls

- **Correlation is not causation.** Phrase relationships as "goes together with", not "causes".
- **Small groups** produce extreme percentages; always show the n next to a rate.
- **Never invent numbers.** Every figure in the findings must come from code you ran on this data. If
  you could not run code, say so and give the code instead of results.
- **Leakage of personal data**: aggregate in findings; do not paste rows with names or contact details
  into the summary unless needed.

## When to stop and ask

- The meaning of a key column or of one row is unclear.
- Data quality is so poor that findings would be misleading; recommend cleaning first.
- The dataset is too large to load whole; propose sampling or aggregation and confirm.

## Scope

A first, broad look. It is not a statistical test, forecast or machine learning model, though it can
recommend one. Polished, publication-ready charts are the job of a chart-making skill.
