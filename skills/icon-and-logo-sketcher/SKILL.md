---
name: icon-and-logo-sketcher
description: >-
  Draw simple, crisp SVG icons and early wordmark or logo concepts by hand-writing clean vector code on a
  consistent grid with matching stroke widths, corner radii, and optical sizes, then checking them at 16, 24,
  and 48 pixels. Produces several distinct concepts and avoids copying existing trademarks. Use this skill
  whenever the user asks to "make an icon", "draw an SVG", "design a logo", "I need a favicon", or "create an
  icon set", or says "teken een icoon", "maak een logo voor mijn bedrijf", or "ontwerp een favicon".
license: "MIT"
metadata:
  author: "prompt"
  category: "design"
  tags: "svg, icon, logo, wordmark, favicon, iconen, logo ontwerp, vector"
  version: "1.0.0"
  summary_nl: "Tekent strakke SVG-iconen en eerste logo-ideeën op een vast raster, getest op kleine en grote formaten."
---

# Icon and logo sketcher

Small graphics fail in small ways: a stroke that turns to mush at 16px, an icon that is visibly heavier
than its neighbours, a logo that only works in one colour. This skill writes SVG by hand on a fixed grid,
so the results are lightweight, editable, and consistent, and it checks them at the sizes where they live.

## Workflow

1. **Clarify the brief.** For icons: what each one represents, where it is used (toolbar, app icon,
   favicon), and whether it must match an existing set. For a logo: the name, what the business does, three
   words for its personality, colour constraints, and where it must work (avatar, invoice, signage).
2. **Set the grid and rules.** Default for UI icons: a 24x24 viewBox, 2px live area padding, 2px stroke,
   `stroke-linecap="round"`, `stroke-linejoin="round"`, no fill. Write the rules down so every icon in a
   set obeys them; consistency is what makes a set look professional.
3. **Sketch with simple geometry.** Build from circles, rectangles, and straight segments with coordinates
   on whole or half pixels. Use the fewest points possible. Use `currentColor` so icons inherit text colour.
4. **Apply optical corrections.** Circles look smaller than squares of the same size, so let them overshoot
   slightly; balance visual weight so a dense icon does not look darker than a sparse one.
5. **Test at real sizes.** Render at 16, 24, and 48px (a quick HTML preview page works). Simplify any detail
   that disappears at 16px; a favicon often needs its own simplified version.
6. **For logos, explore breadth before polish.** Offer three genuinely different directions, for example a
   pure wordmark, a monogram, and a symbol plus wordmark. Show each in one colour, reversed on dark, and at
   small size. Let the user choose one direction before refining.
7. **Clean the output.** Remove editor metadata, unused groups, and transforms where possible; keep a
   `viewBox`, no fixed width and height on the root unless needed, and a `<title>` for accessible use.

## Example icon

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round" role="img">
  <title>Calendar</title>
  <rect x="3" y="5" width="18" height="16" rx="2"/>
  <path d="M3 10h18M8 3v4M16 3v4"/>
</svg>
```

## What the user receives

```
## Concepts
A. Wordmark "Ferro" in a geometric sans, custom joined "rr"   -> ferro-a.svg
B. Monogram F built from two stacked bars                      -> ferro-b.svg
C. Anvil-like symbol + wordmark                                -> ferro-c.svg

Each shown: on light, on dark, at 32px, at 200px.
Rules used: 24px grid, 2px stroke, round caps, currentColor.
Next step: pick a direction; I will refine spacing and make favicon + social avatar versions.
```

Include the SVG code for each file and, when possible, a preview HTML page that shows all sizes side by side.

## Pitfalls and when to ask

- Do not reproduce or closely imitate existing logos, brand marks, or well-known icon sets with
  restrictive licences. If the user asks for "something like Nike's swoosh", explain the trademark risk
  and offer an original direction inspired by the qualities they like (motion, simplicity).
- Fonts used in a wordmark have licences too. Prefer open-licence fonts, or convert final letters to
  outlines and tell the user which font was the starting point.
- Hand-written SVG suits simple, geometric marks. For illustrative or photographic logos, say so and
  suggest a designer or an illustration tool rather than delivering something weak.
- An early concept is not a finished brand identity; say that a logo for wide commercial use deserves a
  trademark search and possibly a professional designer.

## Scope

This skill makes icons and logo concepts as SVG. Choosing a full colour system or tidying a whole
interface are separate tasks.
