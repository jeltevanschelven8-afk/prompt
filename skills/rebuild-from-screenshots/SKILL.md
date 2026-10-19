---
name: rebuild-from-screenshots
description: 'Recreate a program, app, or website from publicly available screenshots, previews, and demo videos found on the web, then iterate by comparing the rebuild against those references until it matches. Use this skill whenever the user wants to "rebuild", "recreate", "clone", "copy the look of", "make something like", "namaken" or "nabouwen" an existing application, tool, website, dashboard, or game — even if they only name the program ("make me a Trello", "I want my own version of Notion''s editor") or share a single screenshot and ask for the rest. Also trigger when the user says "look at how X does it and build that". Covers: finding reference images, cataloguing screens and components, building an original implementation, and a visual compare-and-fix loop.'
---

# Rebuild from screenshots

The job: turn a program the user can point at into a working program the user owns. Three phases,
looping between the last two:

1. **Collect** — find and study reference images of the original.
2. **Build** — an original implementation of what those images show.
3. **Compare** — put your result next to the references, list differences, fix, repeat.

## What you are and aren't rebuilding

Build the **experience**: layout, flows, interactions, information hierarchy, the general look. These are
ideas and patterns, and recreating them is how most software gets made.

Do **not** copy the **identity**: no logos, product names, taglines, mascots, icon sets lifted from the
original, proprietary illustrations, or fonts the user can't license. Use a neutral working name
("Boards", "Notes") unless the user supplies their own, generic or open icon sets (Lucide, Heroicons),
and open fonts. If the original's whole value is its artwork or brand (a game's characters, a famous
illustration style), say so and offer to build the mechanics with placeholder art.

Say this in one line at the start so the user isn't surprised by a different name and logo.

## Phase 1: Collect

**Find references.** Use image search and web search together. Good queries:
- `<program> screenshot`, `<program> interface`, `<program> dashboard`, `<program> mobile app`
- `<program> review` (review sites have many annotated screenshots)
- `<program> demo`, `<program> walkthrough`, `<program> tutorial` (videos show flows, not just screens)
- `<program> dark mode`, `<program> settings`, `<program> onboarding` for screens that marketing pages hide

Aim for 8–15 useful images covering the main screens, not 50 near-duplicates of the homepage. Prefer the
product's own site, docs and reviews over random blog thumbnails: higher resolution, current version.

**Catalogue what you found.** Before writing code, write a short inventory:

```
## Screens
1. Main board view — [ref 1, 3] — list columns, cards, add-column button at right
2. Card detail modal — [ref 5] — title, description, checklist, sidebar actions
...

## Shared components
- Top bar: logo left, search centre, avatar right (ref 1, 2, 4)
- Card: 2px radius, white, shadow, label chips on top
...

## Design tokens (estimated)
- Primary: ~#0079BF  Background: ~#F4F5F7  Text: ~#172B4D
- Font: sans-serif, ~14px body, 20px headings
- Spacing unit: ~8px
- Radius: 3px cards, 8px modals

## Flows observed
- Add card → inline input at column bottom → Enter saves
...

## Not visible / must assume
- Behaviour on empty board
- Error states
```

The "must assume" list matters: it's where you'll make decisions the user may want to overrule. Show the
inventory to the user and ask only the one or two questions that change the build (which screens matter
most; web or mobile; real data or mock).

## Phase 2: Build

- Pick the stack by context. Working in a repo: match its stack. Otherwise a single self-contained HTML
  page (or React artifact) is the fastest route to something the user can see.
- Build in the order the user cares about: main screen first, pixel-level polish last. A rough version of
  every screen beats a perfect version of one.
- Derive everything from the tokens in your inventory. Consistent spacing and a single palette are what
  make a rebuild feel like the original, far more than any single element.
- Real interactions, not painted ones: if the original has drag-and-drop, add drag-and-drop. If a flow
  was visible in a demo, implement that flow.
- Keep data in memory or local state with realistic sample content (not "Item 1, Item 2") so the screens
  read like the references.

## Phase 3: Compare and fix

This is the loop that makes the difference between "sort of like it" and "that's it".

1. **Render your build** at the same viewport as the reference (desktop ~1440px, mobile ~390px). In an
   environment with a browser (Playwright, a headless browser, Claude in Chrome), take a screenshot. In
   chat without a browser, view the artifact and describe honestly what you see.
2. **Compare screen by screen** against the catalogued references. For each, list concrete differences:

   ```
   Main board vs ref 1:
   - Column width 240px vs ~272px → widen
   - Cards missing label chips → add
   - Header too bright; original is darker blue overlay → adjust
   - Add-column button present ✓
   ```

   Be specific and measurable (sizes, colours, missing elements, wrong order), not "looks a bit off".
3. **Fix the top differences**, biggest-visual-impact first: layout and proportions → colour and type →
   spacing → details and icons.
4. **Repeat.** Stop when a round finds only nitpicks or when you've done three rounds; then show the
   user, side by side if possible, and let them steer.

Keep a running changelog of what each round fixed so the user can see progress and you don't undo earlier
fixes.

## When references are thin

- Only a homepage screenshot available: build what's visible, then design the missing screens in the
  same visual language and label them "designed, not observed".
- Only a video: pull frames at the key moments (or describe them from the video page), catalogue those.
- The program is old, niche, or paywalled with no public images: say so, ask the user for screenshots,
  and build from their descriptions.

Never invent a feature and present it as something the original has. "Observed" and "assumed" stay
separate in the inventory and the report.

## Delivering

End with:
- What was rebuilt (screens, flows) and what was deliberately changed (name, logo, assets).
- The comparison result of the last round: what matches, what still differs, what's assumed.
- How to run or open it.
- The reference images used (links), so the user can check your work.
