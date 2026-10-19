---
name: design-first
description: >-
  Design-focused skill: make everything visual look intentional, polished and consistent, and pick the best
  tool or model for each design job before starting. Use this skill whenever the user asks for anything
  visual — a UI, app screen, website, landing page, mockup, logo, poster, flyer, banner, icon, slide design,
  colour palette, typography, "make it look good/nicer/modern/pro", "redesign this", "this looks ugly",
  "give me a few design options", or when they want an image or illustration generated. Also trigger when
  the user shares a screenshot or page and asks for feedback on how it looks. Covers: choosing between a
  Design artifact, coded mockup, or an image-generation model (Adobe, Higgsfield, etc.), then applying
  solid design principles and checking the result against a quality checklist.
---

# Design first

Two jobs, in this order:

1. **Pick the right maker** for this specific design task.
2. **Design it well** — deliberate choices, not defaults.

Most mediocre design output comes from skipping step 1 (building a poster in HTML when an image model would do it better, or generating an image when the user needed an editable screen) or from treating step 2 as "add some padding and a blue button".

## 1. Pick the right maker

Decide before producing anything. Ask one short question only if the choice genuinely changes the outcome; otherwise choose and state your assumption in one line.

| The user wants… | Best maker | Why |
|---|---|---|
| App screens, website pages, dashboards, forms, flows, "show me 3 options" — anything they will **edit, compare, iterate on** | **Design artifact type** (Artifact tool → list types → Design) | Opens on a canvas they can edit themselves; editable, shareable, versionable |
| A **working** page or component (clickable, real data, animations) | Coded HTML/React artifact, following the `frontend-design` skill | Design must be real code to behave |
| Logo, poster, illustration, photo-style image, hero image, social banner, concept art, product shot | **Image-generation model via connector** (Adobe for creativity, Higgsfield, or whatever is connected) | Pixels, not layout; an image model does this far better than SVG/CSS |
| A quick diagram or visual explanation inside the conversation | Inline visual (Visualizer / SVG) | Doesn't need to be a deliverable |
| Slides | Slides artifact type, with a design system if one is set as default | Built for decks |
| Feedback on an existing design | No maker — written critique using the checklist in section 3 | They asked for judgement, not output |

**Choosing the image model when several are connected**

Check which image connectors are available (tool list / tool_search). Then pick by strength rather than habit:

- **Photo-realism, product shots, brand-safe commercial imagery** → Adobe (Firefly) tends to be the safer, more controllable choice and is cleared for commercial use.
- **Stylised, cinematic, dramatic, motion-ready, or video output** → Higgsfield.
- **Logos and icons** → image models are inconsistent with text and clean vectors; prefer the Design type or SVG for anything that must be crisp at small sizes, and use an image model only for exploration/mood.
- If only one is connected, use it. If none is connected and the task is image-generation, search the connector directory and offer the fit, then fall back to an SVG/Design artifact and say so.

Never silently fall back from "the right maker" to "the convenient maker". If the ideal route isn't available, say in one line what you used instead and why.

## 2. Design it well

Before building, settle these four decisions explicitly (write them down for yourself; share them with the user in a sentence or two):

- **Purpose** — what is the one thing the viewer should do or understand? Everything else is secondary.
- **Audience and tone** — playful / serious / premium / technical / friendly. Pick one or two adjectives and commit.
- **Hierarchy** — what's primary, secondary, tertiary. If everything is bold, nothing is.
- **Constraints** — existing brand colours, fonts, platform (mobile/desktop/print), accessibility needs, dark mode.

Then apply the fundamentals:

**Typography**
- Two type families maximum (often one is enough). Pick something with character for display text and something quiet for body text.
- A clear scale: e.g. 48 / 32 / 20 / 16 / 14. Don't invent sizes per element.
- Body text: 16px+ on screen, line-height ~1.5, line length 50–75 characters.

**Colour**
- One dominant colour, one accent, neutrals for the rest. Derive tints/shades from those; don't add a fresh colour every time you need one.
- Contrast: 4.5:1 for body text, 3:1 for large text and UI elements. Check it.
- Decide dark mode up front if it's a screen.

**Spacing and layout**
- A single spacing unit (4 or 8px) and multiples of it. Consistent gaps make things look designed even when nothing else changes.
- Align to a grid. Related things close together, unrelated things further apart.
- Generous whitespace reads as confidence; cramped reads as cheap.

**Components and consistency**
- Same thing looks the same everywhere: one button style per role (primary/secondary/destructive), one card style, one input style.
- States exist: hover, focus, disabled, loading, empty, error. Design at least empty and error for any real screen.

**Imagery**
- When prompting an image model: describe subject, style, lighting, composition, colour mood and what to avoid. One strong concept per image, not a list of everything.
- Match the image's tone to the design's tone. A playful UI with a corporate stock photo looks wrong.

**Avoid the "AI default" look**
- No generic purple-to-blue gradients, no three identical feature cards with emoji icons, no centred-everything hero with the same rounded button, unless the user asked for exactly that.
- Make at least one deliberate, slightly surprising choice (an unusual type pairing, an asymmetric layout, a restrained palette) that gives the design a point of view.

## 3. Quality check before handing over

Run through this quickly and fix what fails:

- [ ] A viewer can tell in two seconds what this is for and where to look first
- [ ] Type scale, colours and spacing are consistent — no one-offs
- [ ] Text contrast passes; touch/click targets are ≥ 44px on mobile
- [ ] Looks right at the sizes it will actually be seen (phone width for screens; print size for posters)
- [ ] Nothing is placeholder-ugly ("Lorem ipsum", grey boxes) unless the user asked for wireframes
- [ ] Matches the stated tone and any brand constraints
- [ ] For generated images: no garbled text, mangled hands, or off-brand style; regenerate rather than ship a flawed one

## 4. Delivering

- Lead with the result, not the process. One or two sentences on the key design decisions (tone, palette, type), then the artifact/image.
- When offering options, make them genuinely different directions (e.g. bold vs. minimal vs. warm), not three shades of the same thing.
- Invite one specific kind of feedback ("want it warmer, or more corporate?") rather than "any thoughts?".
- Mention in one line which maker you used and, if relevant, what the user can export (PNG/PDF from a Design artifact, etc.).

## Giving design feedback (when asked to critique)

Structure it: what works → the two or three biggest issues in priority order → concrete fixes for each. Reference the fundamentals above by name so the feedback is actionable, not "make it pop". Offer to apply the fixes.
