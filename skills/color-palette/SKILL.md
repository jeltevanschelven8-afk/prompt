---
name: color-palette
description: >-
  Create a complete, usable colour palette for a website, app, or brand, with a primary colour, an accent,
  a neutral scale, semantic colours for success, warning and error, and matching light and dark modes.
  Checks every text and background pair against WCAG contrast ratios and delivers CSS custom properties or
  design tokens. Use this skill whenever the user asks to "pick colours", "make a colour scheme", "add dark
  mode", "my colours clash", or says "maak een kleurenpalet", "kies kleuren voor mijn site", or "maak de
  kleuren mooier".
license: "MIT"
metadata:
  author: "prompt"
  category: "design"
  tags: "colour palette, color, dark mode, wcag, contrast, design tokens, kleuren, kleurenpalet"
  version: "1.0.0"
  summary_nl: "Maakt een kleurenpalet met licht en donker thema, gecontroleerd op contrast, klaar als CSS-variabelen."
---

# Colour palette

A palette is not a set of pretty swatches; it is a system that decides which colour goes on which
surface, in which state, in both themes, while staying readable. This skill builds that system and proves
the contrast with numbers, so the user can trust it in production.

## Workflow

1. **Understand the context.** Ask for the brand or mood (calm, playful, serious), any existing brand
   colour, the product type, and whether dark mode is needed. If the user has an existing stylesheet,
   read it and list the colours actually in use; often there are 30 near-duplicates to consolidate.
2. **Choose the primary.** Start from the brand colour if there is one. Otherwise propose two or three
   options with a one-line rationale each and let the user pick, because this choice sets everything else.
3. **Build tonal scales.** For primary and neutrals, generate a 50-950 scale (around 10 steps). Working
   in OKLCH keeps perceived lightness even across hues; adjust lightness in roughly even steps and reduce
   chroma at the extremes so light tints do not look neon and dark shades do not look muddy.
4. **Add an accent and semantic colours.** One accent for highlights, plus success, warning, error, and
   info. Keep semantic hues conventional (green, amber, red, blue) because users already know them.
5. **Assign roles, not just values.** Map colours to tokens like `--color-bg`, `--color-surface`,
   `--color-text`, `--color-text-muted`, `--color-border`, `--color-primary`, `--color-on-primary`.
   Components should use roles; that is what makes dark mode a swap instead of a rewrite.
6. **Design dark mode separately.** Do not just invert. Use dark grey surfaces (not pure black), lift
   elevated surfaces slightly lighter, and pick a lighter primary step so it still reads on dark.
7. **Check contrast for every real pair.** Targets per WCAG 2.2: 4.5:1 for body text, 3:1 for large text
   (24px, or 19px bold) and for UI parts like borders of inputs and focus rings. Compute the ratios rather
   than eyeballing them; if you can run code, calculate relative luminance, otherwise state that the
   numbers should be verified with a contrast checker.
8. **Deliver tokens and a preview.** Provide CSS variables (and JSON tokens or a Tailwind config if the
   project uses those), plus a small HTML preview with buttons, text, alerts, and cards in both themes.

## Output format

```css
:root {
  --color-bg: #ffffff;
  --color-surface: #f6f7f9;
  --color-text: #16181d;
  --color-text-muted: #5b6270;
  --color-border: #d9dde3;
  --color-primary: #2554d9;
  --color-on-primary: #ffffff;
  --color-accent: #e8590c;
  --color-success: #1f7a3d;
  --color-error: #c62828;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #121418;
    --color-surface: #1c1f25;
    --color-text: #e8eaee;
    --color-text-muted: #a3a9b5;
    --color-border: #343944;
    --color-primary: #7d9cf5;
    --color-on-primary: #0d1530;
  }
}
```

Then a contrast table:

| Pair | Light | Dark | Passes |
|---|---|---|---|
| text on bg | 17.9:1 | 15.6:1 | AA, AAA |
| text-muted on surface | 5.8:1 | 7.1:1 | AA |
| on-primary on primary | 6.4:1 | 6.9:1 | AA |

(Example figures; recompute for the actual values you deliver.)

## Pitfalls and when to ask

- Colour alone should not carry meaning; pair error red with an icon or text, since about 1 in 12 men has
  some colour vision deficiency.
- Brand colours often fail contrast as text. Keep the brand hue for fills and large elements and use a
  darker step for text, and explain this to the user instead of silently changing their brand.
- Too many colours make a UI noisy. If the user asks for five accents, show how it looks and suggest fewer.
- Before replacing colours across an existing codebase, show the mapping old -> new and ask.

## Scope

This skill covers colour. For a full visual clean-up (spacing, type, components) use a UI polish pass; for
a complete accessibility review, use an accessibility audit.
