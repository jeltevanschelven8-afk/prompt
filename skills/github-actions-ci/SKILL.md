---
name: github-actions-ci
description: >-
  Set up or fix GitHub Actions CI for a repository. Writes workflows that test, lint and build on
  every pull request, with dependency caching, a version matrix, least-privilege permissions,
  concurrency limits and failure output that is easy to read. Use this skill whenever the user asks to
  "add CI", "set up GitHub Actions", "my workflow is failing", "make CI faster", "run tests on PRs",
  "add a build matrix" or pastes a red Actions log. Also trigger for "zet CI op voor mijn repo", "mijn
  GitHub Action faalt" or "waarom is mijn pipeline rood".
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "github actions, ci, workflow, pipeline, yaml, caching, matrix, testen, bouwen"
  version: "1.0.0"
  summary_nl: "Zet GitHub Actions CI op of repareert die: testen, linten en bouwen bij elke pull request, snel en veilig."
---

# GitHub Actions CI

CI earns its keep when it is fast, trustworthy and tells you in one glance what broke. This skill
writes workflows that match how the project already builds locally, and diagnoses failing runs from
the actual log rather than from guesses.

## Workflow: new CI

### 1. Learn how the project builds

Read `package.json` scripts, `Makefile`, `pyproject.toml`, `tox.ini`, `go.mod`, existing
`.github/workflows/*`. Find the exact lint, test and build commands and the supported runtime versions.
CI should run the same commands a developer runs, so a green build means something locally too.

### 2. Write the workflow

Place it at `.github/workflows/ci.yml`. A Node example with the important parts annotated:

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read            # least privilege; widen per job only when needed

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true  # a new push cancels the outdated run

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false      # see every failing version, not just the first
      matrix:
        node: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test -- --reporter=dot
      - name: Build
        run: npm run build
```

Equivalents: `actions/setup-python@v5` with `cache: pip`, `actions/setup-go@v5` (caches by default),
`actions/setup-java@v4` with `cache: gradle`. Separate named steps make the failing stage obvious in
the UI. Keep the matrix small; every entry multiplies minutes.

### 3. Security defaults

- Set `permissions` at the top level; grant `pull-requests: write` or `packages: write` only to the job
  that needs it.
- Pin third-party actions to a full commit sha with a version comment (`uses: org/action@<sha> # v2.1.0`).
  Official `actions/*` on a major tag is a common, acceptable compromise; mention the trade-off.
- Prefer `pull_request` over `pull_request_target`; the latter runs with repository secrets on code
  from forks and is easy to misuse.
- Pass untrusted input such as PR titles through `env:` instead of inlining `${{ }}` in `run:` scripts,
  which prevents script injection.
- Store credentials in repository or environment secrets and reference them with `${{ secrets.NAME }}`.

### 4. Validate

If available, run `actionlint` on the file. Otherwise check YAML indentation and job names carefully,
and tell the user the workflow has not run yet. Suggest opening a draft PR to see the first run.

## Workflow: fixing a failing run

1. Get the real log: `gh run list --limit 5`, then `gh run view <id> --log-failed`, or ask the user to
   paste the failing step.
2. Find the first error, not the last line. Later errors are often consequences.
3. Classify: workflow config (bad YAML, missing permission, wrong action input), environment
   (version mismatch, missing system package, cache restoring stale data), or a real test failure.
4. Reproduce locally with the same version when possible, then fix the cause. Do not paper over a real
   test failure by marking the step `continue-on-error`.
5. Re-run with `gh run rerun <id> --failed` only after a change, or when the failure is clearly flaky,
   and say which it was.

## Output format

```text
Diagnosis: the Test step fails on Node 20 only - `structuredClone` behaves differently in an old
jsdom version pulled in by the lockfile.
Fix: bump jsdom to 24.x (package.json) - no workflow change needed.
Also improved: added concurrency cancel and npm cache; expected run time ~4 min -> ~2 min.
Files changed: package.json, package-lock.json, .github/workflows/ci.yml
Verify: push the branch and check the "CI" run on the PR.
```

For new setups, show the full workflow file followed by a short list of what each job checks.

## Pitfalls

- Caches keyed on the wrong file never hit; key on the lockfile.
- `npm install` in CI can change the lockfile silently; use `npm ci`.
- Long matrices on every push burn minutes; run the full matrix on main and a subset on PRs if needed.
- Ask before adding deploy steps or anything that writes to registries or environments.

## Scope

This skill covers GitHub Actions CI. Other CI systems (GitLab, Azure Pipelines) need different syntax;
say so and translate the ideas. Building container images is covered by dockerize-app.
