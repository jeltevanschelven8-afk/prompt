---
name: accessibility-audit
description: >-
  Audit a web page, component, or app screen for accessibility against WCAG 2.2, covering keyboard access,
  visible focus, colour contrast, form labels, alt text, headings and landmarks, ARIA use, and motion. Produces
  a prioritised list of issues with the exact fix for each. Use this skill whenever the user asks "is this
  accessible", "check a11y", "WCAG audit", "screen reader support", or "can keyboard users use this", or
  says in Dutch "controleer de toegankelijkheid", "is mijn site toegankelijk", or "doe een WCAG-check".
license: "MIT"
metadata:
  author: "prompt"
  category: "design"
  tags: "accessibility, a11y, wcag, screen reader, keyboard, toegankelijkheid, contrast, audit"
  version: "1.0.0"
  summary_nl: "Controleert je pagina of app op toegankelijkheid volgens WCAG 2.2 en geeft een geprioriteerde lijst met oplossingen."
---

# Accessibility audit

Accessibility problems lock real people out: someone using only a keyboard, a screen reader, zoom at 200%,
or a phone in bright sunlight. Automated tools catch roughly a third of issues, so this audit combines a
code read, automated checks where available, and manual checks that mimic how people actually use the page.

## Workflow

1. **Define what is audited.** Agree on the pages or components and the target level (WCAG 2.2 AA unless
   the user says otherwise). Auditing one representative page per template is usually enough to start.
2. **Run automated checks if you can.** axe-core (via Playwright or the browser extension), Lighthouse,
   or the project's linter (`eslint-plugin-jsx-a11y`). Treat results as leads, not the full picture.
3. **Keyboard pass.** Tab through the page. Can every interactive element be reached and operated with
   Tab, Shift+Tab, Enter, Space, Escape, and arrows? Is the order logical? Does focus get trapped in a
   modal while it is open and return to the trigger when it closes? Is there a skip link?
4. **Focus visibility.** Every focused element needs a visible indicator with at least 3:1 contrast.
   `outline: none` without a replacement is one of the most common failures.
5. **Semantics and structure.** One `h1`, headings in order, landmarks (`header`, `nav`, `main`,
   `footer`), lists as lists, buttons as `<button>` and links as `<a href>`. A `div` with a click
   handler is invisible to keyboard and screen reader users.
6. **Names and labels.** Every input has a programmatic label; icon-only buttons have an accessible name;
   errors are announced and linked to their field (`aria-describedby`). Placeholder text is not a label.
7. **Images and media.** Informative images get alt text that conveys their purpose; decorative ones get
   `alt=""`. Videos need captions; auto-playing motion needs a pause control.
8. **Contrast and resize.** Text 4.5:1 (large text 3:1), UI components 3:1. Zoom to 200% and check
   that nothing overlaps or is cut off; check a 320px-wide viewport for reflow.
9. **WCAG 2.2 additions.** Target size of at least 24x24px, focus not hidden behind sticky headers,
   no drag-only interactions, and no forcing users to re-enter information they already gave.
10. **Prioritise and report.** Order by impact on users, then by effort.

## Priority levels

- **Blocker**: some users cannot complete a task (keyboard trap, unlabelled form, button that is a div).
- **Serious**: task is possible but very hard (missing focus indicator, low contrast body text).
- **Moderate**: friction or confusion (heading order, vague link text like "click here").
- **Minor**: polish (redundant alt text, missing `lang` on a quote).

## Output format

```markdown
## Accessibility audit: Sign-up page (WCAG 2.2 AA)
Method: axe-core scan + manual keyboard and screen-reader-style review of the code.

| # | Priority | Issue | WCAG | Where | Fix |
|---|---|---|---|---|---|
| 1 | Blocker | "Next" is a div with onClick; not reachable by keyboard | 2.1.1 | SignupForm.tsx:42 | Use `<button type="submit">` |
| 2 | Serious | Focus outline removed globally | 2.4.7 | globals.css:12 | Add `:focus-visible { outline: 2px solid var(--color-primary); }` |
| 3 | Moderate | Email field uses placeholder as label | 3.3.2 | SignupForm.tsx:30 | Add `<label for="email">Email</label>` |

**What works well:** logical tab order, alt text on the hero image.
**Not checked:** real screen reader testing (NVDA/VoiceOver), PDF downloads.
```

## Pitfalls and when to ask

- Adding ARIA is rarely the first fix. Native HTML elements come with keyboard support and roles for free;
  wrong ARIA makes things worse than no ARIA.
- Be explicit about what was not tested. Reviewing code is not the same as testing with a real screen
  reader, and claiming full compliance from a code read would mislead the user.
- If the user wants fixes applied, show the list first and ask which to change; some fixes alter visuals.
- Legal compliance questions (e.g. the European Accessibility Act) need a qualified person; offer the
  technical findings and say so.

## Scope

This skill audits and recommends. Choosing a full colour system belongs to a palette task, and general
visual tidying belongs to a UI polish task, though both should respect the findings here.
