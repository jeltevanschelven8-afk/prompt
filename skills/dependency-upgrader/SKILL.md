---
name: dependency-upgrader
description: >-
  Upgrade packages and dependencies safely: inventory what is outdated, read
  changelogs and migration guides for breaking changes, upgrade one major
  version at a time, run the tests after each step, and keep lockfiles
  consistent. Works with npm, pnpm, yarn, pip, Poetry, uv, Maven, Gradle, Go
  modules, Cargo, Composer and Bundler. Use this skill whenever the user wants
  to update dependencies, bump a framework version, fix outdated or vulnerable
  packages, or handle a Dependabot PR, and for Dutch phrases such as "update
  mijn packages", "upgrade naar de nieuwste versie" or "afhankelijkheden
  bijwerken".
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "dependencies, upgrade, packages, npm, pip, lockfile, changelog, updaten, afhankelijkheden, bijwerken"
  version: "1.0.0"
  summary_nl: "Werkt je packages veilig bij: changelogs lezen, per major versie upgraden, testen en lockfiles netjes houden."
---

# Dependency upgrader

Upgrading everything at once and hoping for the best is how a Friday afternoon turns into a weekend. This skill upgrades in controlled steps, reads what changed before changing it, and keeps each step small enough that when tests fail, the culprit is obvious.

## Workflow

1. **Start from green.** Check `git status` is clean and run the test suite and build first. If they already fail, report that before upgrading anything; otherwise you cannot tell which failures the upgrade caused. Create a branch, for example `chore/deps-2026-10`.
2. **Inventory.** List what is outdated and why it matters:
   - npm / pnpm / yarn: `npm outdated`, `npm audit`
   - Python: `pip list --outdated`, `poetry show --outdated`, `uv pip list --outdated`, `pip-audit`
   - Go: `go list -m -u all`; Rust: `cargo outdated`; PHP: `composer outdated`; Ruby: `bundle outdated`; Maven: `mvn versions:display-dependency-updates`
   Classify each into patch, minor and major, and flag security advisories.
3. **Propose a plan and get agreement.** Typical order: security fixes first, then patch and minor updates in one batch, then each major upgrade separately, starting with the ones others depend on (for example the framework before its plugins). Show the plan before touching files.
4. **Read before upgrading majors.** For each major: changelog, release notes, migration guide, list of removed or renamed APIs, new minimum runtime versions (Node, Python, Java). Search the codebase for the affected APIs so you know the blast radius before you start.
5. **Upgrade one step at a time.**
   - Use the package manager rather than editing version numbers by hand, so the lockfile stays consistent: `npm install pkg@^5`, `poetry add pkg@^5`, `go get pkg@v5`, `cargo update -p pkg`.
   - For long jumps (v2 to v5), go through intermediate majors if the migration guides are written per version.
   - Run official codemods when available (for example framework upgrade CLIs), and review their diff.
6. **Test after each step.** Install from scratch to catch lockfile issues (`npm ci`, `poetry install --sync`), then build, lint, type-check and test. Commit each green step on its own: `chore(deps): upgrade express 4 to 5`.
7. **Handle failures deliberately.** Fix code for documented breaking changes. If a step is too large for now, revert it, pin the previous version, and note why. Avoid forcing peer conflicts with flags like `--force` or `--legacy-peer-deps` unless you understand the conflict and the user agrees.
8. **Report.** Summarize what changed, what was skipped and why, and any manual checks the user should do (UI smoke test, staging deploy).

## Reading a changelog efficiently

Changelogs can be long; skim for what can break your code:

- Sections titled Breaking changes, Removed, Deprecated, or Migration.
- New minimum versions of the runtime, peer dependencies or build tools.
- Changed defaults (a setting that used to be off is now on), which break things silently.
- Behaviour changes in functions the project actually calls; grep for them, for example `grep -rn "bodyParser\|req.param(" src`.
- Security fixes, which raise the priority of that upgrade.

Write down the relevant items per package; they go into the commit message and the final report.

## Lockfiles

Always commit the lockfile together with the manifest change. Do not delete and regenerate a whole lockfile to fix one conflict, because that silently upgrades every transitive dependency; resolve the specific package instead. Use one package manager per project; a stray `package-lock.json` next to `pnpm-lock.yaml` causes drift.

## Output format

```markdown
**Branch:** chore/deps-2026-10. Baseline: build and 312 tests green.

| Package | From | To | Type | Notes | Status |
|---|---|---|---|---|---|
| lodash | 4.17.20 | 4.17.21 | patch | security advisory fixed | done |
| express | 4.19.2 | 5.0.1 | major | req.param removed, 3 call sites updated | done |
| webpack | 4.47.0 | 5.94.0 | major | config migration needed, Node polyfills removed | skipped, needs its own PR |

**Tests:** npm ci, npm run build, npm test after each step, all green.
**Not verified:** manual UI check, staging deploy.
```

## Pitfalls and when to ask

- Ask before upgrading a runtime or framework major; it often affects deployment and teammates.
- Do not trust green tests alone when coverage is thin; list the risky areas the user should check by hand.
- Renovate or Dependabot PRs: still read the changelog for majors before merging.
- Watch for packages that changed name or were deprecated in favour of another; that is a migration, not an upgrade.

## Scope

Application and library dependencies. Operating system packages, container base images and infrastructure modules follow similar steps but have their own tooling; say so if the user asks about them.
