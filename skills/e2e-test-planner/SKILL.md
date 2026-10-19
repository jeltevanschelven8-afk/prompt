---
name: e2e-test-planner
description: >-
  Plan and write end-to-end tests for the critical user flows of a web app, using Playwright or whatever
  E2E tool the project already has. Picks the flows that matter most, uses stable role- and test-id-based
  selectors, waits on real conditions instead of sleeps, and keeps tests independent. Use this skill whenever
  the user asks to "add e2e tests", "test the checkout flow", "write Playwright tests", "my Cypress tests are
  flaky", or says "schrijf end-to-end tests", "test de inlogflow", "maak e2e tests voor mijn app".
license: "MIT"
metadata:
  author: "prompt"
  category: "testing"
  tags: "e2e, playwright, cypress, testing, flaky tests, user flows, testen, eindgebruiker"
  version: "1.0.0"
  summary_nl: "Plant en schrijft stabiele end-to-end tests voor de belangrijkste gebruikersflows van je app, zonder wankele wachttijden."
---

# E2E test planner

End-to-end tests are the slowest and most expensive tests a project has, so every one should earn its
place. The goal is a small set of tests that cover the flows that would hurt most if they broke, and that
pass or fail for real reasons only. A flaky E2E suite is worse than none, because people learn to ignore it.

## Workflow

1. **Find the existing setup.** Look for `playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, or an
   `e2e/` folder, and check `package.json` scripts. Use the tool that is already there; introducing a second
   E2E framework doubles maintenance. If there is none, propose Playwright and ask before installing it.
2. **List candidate flows and rank them.** Ask (or infer from routes and the README) which journeys make
   or lose money or trust: sign-up, sign-in, search, add to cart, checkout, create/edit/delete a core
   record, sharing. Rank by impact times likelihood of breaking. Show the list to the user and agree on the
   top 3 to 6 before writing code, since that is where the scope is decided.
3. **Write a short plan per flow.** Preconditions, steps, and the observable outcome that proves success
   (a URL, a heading, a row in a table, a toast). Asserting on what the user sees keeps tests meaningful.
4. **Prepare test data deliberately.** Prefer seeding through an API, fixture, or factory over clicking
   through setup screens; it is faster and failures point at the flow under test. Give each test its own
   data (unique names, e.g. with a timestamp suffix) so tests can run in parallel and in any order.
5. **Choose stable selectors.** In order of preference: accessible role and name
   (`getByRole('button', { name: 'Save' })`), label (`getByLabel('Email')`), then a dedicated
   `data-testid`. Avoid CSS classes, nth-child chains, and XPath; they break on harmless styling changes.
   If an element has no accessible name, that is often an accessibility bug worth reporting too.
6. **Wait on conditions, not time.** Replace `waitForTimeout(3000)` and `sleep` with web-first assertions
   (`await expect(locator).toBeVisible()`), waiting for a specific network response, or a URL change.
   Fixed sleeps are either too short on a slow CI runner or waste time everywhere else.
7. **Run the tests and report honestly.** Run them locally, then a few times in a row (for Playwright,
   `--repeat-each=3`) to catch flakiness early. Report actual results; if something fails, show the error
   and whether it is a test problem or a real bug in the app.
8. **Wire into CI if asked.** Suggest traces or videos on first retry only, so failures are debuggable
   without slowing every run.

## Example (Playwright)

```ts
import { test, expect } from '@playwright/test';

test('customer can add a product to the cart and reach checkout', async ({ page }) => {
  await page.goto('/products/blue-mug');
  await page.getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByRole('status')).toHaveText(/added to cart/i);

  await page.getByRole('link', { name: /cart \(1\)/i }).click();
  await expect(page.getByRole('row', { name: /blue mug/i })).toBeVisible();

  await page.getByRole('button', { name: 'Checkout' }).click();
  await expect(page).toHaveURL(/\/checkout/);
});
```

For flows behind sign-in, log in once in a setup project and reuse the stored session state, instead of
repeating the login form in every test.

## What the user receives

```
## E2E plan
| # | Flow | Why it matters | Outcome asserted | Status |
|---|------|----------------|------------------|--------|
| 1 | Add to cart -> checkout | Revenue path | URL /checkout, cart row | written, passes 3/3 |
| 2 | Sign up | Growth | Welcome heading | written, fails: see below |

## Files
- e2e/cart.spec.ts (new)
- e2e/fixtures/products.ts (new)

## Findings
- Sign-up fails because the "Create account" button has no accessible name (icon only).
```

## Pitfalls and when to ask

- Tests that depend on each other's leftovers fail randomly once run in parallel. Keep each test
  self-contained.
- Do not test third-party pages (payment providers, OAuth screens) end to end; stub at the boundary or
  use the provider's test mode, and ask the user which they prefer.
- If the app needs real external accounts or production data to run, stop and ask for a test environment
  rather than pointing tests at live systems.
- If a selector only works with a brittle CSS path, ask whether you may add a `data-testid` to the app
  code, since that is a change outside the test folder.
- Never mark a test as passing that you did not run.

## Scope

This skill is for browser-level user flows. For unit and integration tests, or an overall test strategy,
use a testing-strategy approach instead; for load testing, use a dedicated performance tool.
