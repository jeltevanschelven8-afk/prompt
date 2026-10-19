---
name: chart-maker
description: >-
  Choose the right chart for the question the data has to answer and build it in matplotlib, Plotly,
  Chart.js, Excel or Google Sheets, with honest axes, a clear title that states the takeaway, direct
  labels and colour-blind-safe colours. Use this skill whenever the user asks to plot, chart, graph or
  visualise numbers, wants a figure for a report or slide, asks "which chart should I use", wants an
  ugly or misleading chart fixed, or types "maak een grafiek", "zet dit in een diagram", "welke grafiek
  past hierbij" or "visualiseer deze cijfers".
license: "MIT"
metadata:
  author: "prompt"
  category: "data"
  tags: "charts, grafiek, visualisation, matplotlib, plotly, chartjs, diagram, dataviz"
  version: "1.0.0"
  summary_nl: "Kiest de juiste grafiek voor je vraag en bouwt hem met eerlijke assen, duidelijke labels en toegankelijke kleuren."
---

# Chart maker

A chart is an argument made with shapes. It works when the reader gets the point in five seconds and
the shapes do not exaggerate or hide anything. That depends far more on choosing the right chart type and
removing clutter than on the tool. This skill starts from the question, not from the chart menu.

## Workflow

1. **State the question the chart answers.** "Which region grew fastest?" or "How are delivery times
   distributed?" If the user just says "make a chart", propose the most useful question for the data.
2. **Choose the chart type** with the table below.
3. **Pick the tool** the user will actually use: matplotlib/seaborn for reports and notebooks, Plotly
   for interactive HTML, Chart.js for a web page, Excel or Google Sheets when the user lives there. Match
   what the project already uses.
4. **Prepare the data** in the shape the chart needs (long vs wide, sorted, aggregated). Check that the
   numbers you plot match the source; never fill in or smooth data without saying so.
5. **Build it, then remove clutter**: no 3D, no shadows, light or no gridlines, no legend when direct
   labels fit.
6. **Write a takeaway title** ("Noord grew 18%, twice the average") and a neutral subtitle with unit,
   period and source.
7. **Check it** against the honesty and accessibility list, then save as PNG/SVG (or HTML) with a
   descriptive file name, and give alt text.

## Which chart for which question

| Question | Chart | Avoid |
|---|---|---|
| Compare categories | horizontal bar, sorted | pie with more than 3-4 slices |
| Change over time | line (bars for few periods) | area charts with many series |
| Part of a whole | stacked bar, or a single pie with 2-3 parts | donut forests |
| Distribution | histogram, box plot | bar of averages only |
| Relationship between two numbers | scatter (add trend line if meaningful) | dual y-axes |
| Ranking change | slope chart or dumbbell | spaghetti line chart |
| Many categories over time | small multiples | one line per category on one chart |

## Honesty and accessibility checklist

- **Bars start at zero.** A truncated bar axis turns a 3% difference into a visual doubling. Line charts
  may zoom in, but label the axis clearly.
- **Same scale** across small multiples, unless noted.
- **Units and period** in the subtitle or axis label (EUR x 1,000, Q1-Q3 2026).
- **Colour**: a colour-blind-safe palette (Okabe-Ito, viridis, Tableau 10); one highlight colour plus
  grey for the rest when telling a single story. Do not rely on red vs green alone.
- **Contrast** of text against background at least 4.5:1; font size readable when the chart is shrunk
  onto a slide.
- **Alt text** that states the takeaway and main numbers, not "a bar chart".
- **Locale**: Dutch audiences expect decimal commas and `EUR 1.234,56` or `€ 1.234`; set the formatter
  rather than leaving it to defaults.

## Example (matplotlib)

```python
import matplotlib.pyplot as plt
regions = ["Noord", "Oost", "Zuid", "West"]; growth = [18, 9, 8, 6]
colors = ["#0072B2" if r == "Noord" else "#BBBBBB" for r in regions]
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.barh(regions[::-1], growth[::-1], color=colors[::-1])
for y, v in enumerate(growth[::-1]):
    ax.text(v + 0.3, y, f"{v}%", va="center")
ax.set_xlim(0, 20); ax.spines[["top", "right"]].set_visible(False); ax.set_xticks([])
ax.set_title("Noord grew 18%, twice the average", loc="left", fontweight="bold")
fig.text(0.01, 0.01, "Revenue growth 2025 vs 2024, source: sales export", fontsize=8, color="#555")
fig.tight_layout(); fig.savefig("groei_per_regio.png", dpi=200)
```

For Chart.js or Plotly, apply the same decisions: sorted data, one highlight colour, takeaway title,
value labels, zero-based bar axis.

## What you hand back

```
Chart: groei_per_regio.png (and .svg)
Type: sorted horizontal bar - comparing 4 regions
Alt text: "Bar chart of revenue growth by region in 2025. Noord grew 18%, Oost 9%, Zuid 8%, West 6%."
Code: the script above, re-runnable on new data
```

## When to stop and ask

- The data cannot support the claim the user wants the chart to make; show what it does support.
- The question is unclear and two very different charts would fit; offer both as thumbnails or a short
  description and let the user choose.
- Brand colours or a house style exist; use them, but check contrast and colour-blind safety.

## Scope

One chart or a small set for a report, slide or page. Full interactive dashboards and exploratory
analysis are adjacent jobs; this skill focuses on getting the individual chart right.
