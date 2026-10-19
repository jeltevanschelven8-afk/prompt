---
name: ui-polish
description: >-
  Tidy up an existing user interface so it looks deliberate and consistent, by introducing a spacing scale,
  fixing alignment, sharpening the typography hierarchy, unifying buttons, inputs and cards, and adding missing
  hover, focus, disabled, empty, and loading states. Changes are small, reviewable, and listed as before and
  after. Use this skill whenever the user says "this looks messy", "clean up the UI", "make it look more
  professional", "polish this screen", or in Dutch "maak het strakker", "het ziet er rommelig uit", or
  "verbeter de uitstraling van mijn app".
license: "MIT"
metadata:
  author: "prompt"
  category: "design"
  tags: "ui, polish, spacing, typography, css, design system, strakker, uitstraling"
  version: "1.0.0"
  summary_nl: "Maakt een bestaande interface strakker met vaste spacing, betere typografie en consistente componenten, met voor-en-na notities."
---

# UI polish

Most "ugly" interfaces are not badly designed; they are inconsistent. Twelve slightly different paddings,
four greys, three button styles, and headings that are barely bigger than body text. Polish means reducing
those choices to a small system and applying it everywhere, without redesigning what already works.

## Workflow

1. **Look before touching.** Take a screenshot or read the relevant components and styles. Inventory what
   exists: every distinct padding/margin value, font size, font weight, colour, border radius, and shadow.
   The inventory usually makes the problem obvious ("17 spacing values, 9 font sizes").
2. **Propose a compact system.** Show it to the user before applying it:
   - Spacing scale on a 4px base: 4, 8, 12, 16, 24, 32, 48, 64.
   - Type scale with clear steps, e.g. 12, 14, 16, 20, 24, 32, with two weights (regular, semibold).
   - Two or three radii (e.g. 4, 8, 12) and one or two shadows.
   Reuse existing tokens if the project has them; polishing should not fork the design system.
3. **Fix hierarchy first.** On each screen, decide what the one most important thing is and make it
   clearly dominant through size, weight, or position. Demote secondary text with colour (muted) rather
   than shrinking it until it is unreadable.
4. **Fix alignment and rhythm.** Align to a few shared edges; group related items with less space between
   them than between groups (proximity does the work borders often do). Remove borders that only separate.
5. **Unify components.** One primary button style, one secondary, one destructive. Same height for buttons
   and inputs in a row. Cards share padding and radius.
6. **Complete the states.** Hover, active, focus-visible, disabled, loading, empty, and error states for
   interactive pieces. Missing states are a big reason UIs feel unfinished.
7. **Apply in small commits or steps.** Change tokens first, then components, then screens, so the user
   can review each step and revert one without losing the rest.
8. **Show before and after.** Screenshots if possible, otherwise a precise change list.

## Example change

```css
/* before */
.card { padding: 13px 18px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 22px; }
.card h3 { font-size: 15px; font-weight: 700; }

/* after */
.card { padding: var(--space-4) var(--space-6); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); }
.card + .card { margin-top: var(--space-4); }
.card h3 { font-size: var(--text-lg); font-weight: 600; }
```

## What the user receives

```markdown
## UI polish: Dashboard
System: spacing 4-64 (8 steps), type 12-32 (6 steps), radius 4/8/12.

| Area | Before | After | Why |
|---|---|---|---|
| Page title | 18px bold, same as card titles | 32px semibold | Clear entry point |
| Cards | 4 paddings, 2 radii | space-4/space-6, radius-md | Consistent rhythm |
| Buttons | 3 primary styles | 1 primary, 1 secondary | Predictable actions |
| Empty table | blank area | message + "Add first client" button | Guides new users |

Files changed: tokens.css, Card.tsx, Button.tsx, Dashboard.tsx
Not changed: navigation layout (works well), colours (out of scope; see notes).
```

## Pitfalls and when to ask

- Polish is not a redesign. If you find that the layout or flow itself is the problem, say so and ask
  before restructuring.
- Do not change brand colours or logos on your own initiative; flag issues and suggest.
- Watch for side effects: a token change can ripple through screens you did not look at. Search usages
  and mention them.
- Keep accessibility intact or better. Lighter grey "for elegance" often breaks text contrast.
- If there is no way to see the UI (no screenshot, no running app), say that your changes are based on
  the code only and ask for a screenshot to verify.

## Scope

This skill refines an existing interface. Building a new page from scratch, creating a colour palette, or
doing a formal accessibility audit are separate, more focused tasks.
