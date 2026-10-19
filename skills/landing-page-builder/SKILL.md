---
name: landing-page-builder
description: >-
  Build a clear, conversion-focused landing page in responsive HTML and CSS, organised around one goal with a
  strong hero, concrete benefits, social proof, objection handling, and a single repeated call to action. Writes
  the copy and the code, and keeps it fast and accessible. Use this skill whenever the user wants a "landing
  page", "sales page", "product page", "waitlist page", or "a page for my launch", or writes in Dutch
  "maak een landingspagina", "bouw een verkooppagina", or "ik wil een pagina voor mijn product".
license: "MIT"
metadata:
  author: "prompt"
  category: "design"
  tags: "landing page, conversion, html, css, copywriting, landingspagina, website, cta"
  version: "1.0.0"
  summary_nl: "Bouwt een heldere landingspagina met één doel, sterke kop, voordelen, bewijs en een duidelijke knop, responsief in HTML/CSS."
---

# Landing page builder

A landing page exists to get one kind of visitor to take one action. Every section either moves them
toward that action or removes a reason to hesitate; anything else is a distraction. This skill decides
the message first and builds the page second, because good layout cannot rescue unclear copy.

## Workflow

1. **Nail the brief in a few questions.** What is offered, for whom, the single action (sign up, book a
   call, buy, join waitlist), the main alternative the visitor uses today, and any real proof (numbers,
   quotes, logos the user is allowed to show). If the user has no proof yet, plan for that honestly.
2. **Write the message before the markup.** Draft the headline (the outcome for the visitor, not the
   product name), a subheadline that says what it is and who it is for, and the CTA label as a verb plus
   outcome ("Start my free trial", not "Submit"). Show these to the user; they are the riskiest part.
3. **Outline the sections.** A proven order:
   - Hero: headline, subheadline, primary CTA, a visual of the product in use.
   - Problem or "before": the pain in the visitor's words.
   - Benefits: 3 to 4, each a concrete outcome with a short supporting line.
   - How it works: 3 steps, to make it feel easy.
   - Social proof: testimonials with name and role, numbers, or logos.
   - Objections / FAQ: price, effort, trust, cancellation.
   - Final CTA: repeat the same action.
4. **Build mobile first.** Semantic HTML (`header`, `main`, `section`, one `h1`), a single CSS file with
   custom properties for colour and spacing, CSS grid or flexbox, and fluid type with `clamp()`. No
   framework unless the project already uses one.
5. **Keep it fast.** Inline critical CSS if the page is small, use modern image formats with width and
   height set, `loading="lazy"` below the fold, and system fonts or one web font. Speed is conversion.
6. **Make it accessible.** Sufficient contrast, real buttons and links, visible focus, alt text that
   describes the product shot, and a form with labels if there is one.
7. **Review against the checklist** below and show the result, ideally as a preview or screenshot.

## Example hero

```html
<header class="hero">
  <h1>Close your month-end books in one afternoon</h1>
  <p class="sub">Ledgerly matches bank transactions to invoices automatically, for freelancers and small
    agencies in the EU.</p>
  <a class="btn btn-primary" href="#signup">Start my free 14-day trial</a>
  <p class="fine">No card needed. Cancel anytime.</p>
</header>
```

```css
.hero { padding: clamp(3rem, 8vw, 6rem) 1rem; max-width: 46rem; margin-inline: auto; text-align: center; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.25rem); line-height: 1.1; }
.btn-primary { background: var(--color-primary); color: var(--color-on-primary); padding: .9rem 1.4rem;
  border-radius: .5rem; font-weight: 600; }
```

## Quality checklist

- Can a stranger say what this is and who it is for within five seconds of the hero?
- Is there exactly one primary action, with the same label everywhere it appears?
- Does every benefit describe an outcome rather than a feature?
- Is every claim and testimonial real? Placeholders are clearly marked as placeholders.
- Does it work at 360px wide with no horizontal scroll, and do tap targets feel comfortable?

## What the user receives

The page files (`index.html`, `styles.css`, images folder if needed), a short note on the copy choices,
and a list of placeholders still to fill, such as "testimonial 2: needs a real quote".

## Pitfalls and when to ask

- Do not invent testimonials, customer logos, or statistics. Fake proof damages trust and may be
  unlawful; use clearly marked placeholders and ask the user for real material.
- A navigation bar with ten links leaks visitors away; ask before adding one.
- If the user wants several goals on one page ("sign up, and also read the blog, and also hire us"), point
  out the trade-off and suggest a primary and a secondary action at most.
- Ask before adding analytics or third-party scripts, since they affect privacy and cookie consent.

## Scope

This skill builds a single marketing page. A multi-page website, a web app UI, or brand identity work
are separate tasks.
