---
name: release-notes-writer
description: >-
  Write release notes and CHANGELOG entries from commits, merged pull requests or tags. Groups changes
  under Added, Changed, Fixed, Deprecated, Removed and Security, rewrites developer jargon into
  user-facing language, puts highlights and breaking changes first and suggests the next semantic
  version. Use this skill whenever the user asks to "write release notes", "update the changelog",
  "what changed since v1.2", "summarise this release", "draft the GitHub release", or says "schrijf
  release notes", "wat is er veranderd sinds de vorige versie" or "maak een changelog".
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "release notes, changelog, semver, keep a changelog, versie, release, github releases"
  version: "1.0.0"
  summary_nl: "Maakt duidelijke release notes en CHANGELOG-items van je commits of pull requests, gegroepeerd en in gewone taal."
---

# Release notes writer

Release notes are read by users deciding whether to upgrade, not by the developers who wrote the
commits. This skill turns a range of commits or pull requests into notes that answer three questions
quickly: what is new, what might break for me, and what got fixed.

## Workflow

### 1. Collect the changes

Find the range, usually from the last tag to `HEAD`:

```bash
git describe --tags --abbrev=0                     # last tag, e.g. v1.4.0
git log v1.4.0..HEAD --no-merges --pretty='%h %s'
gh pr list --state merged --base main --search "merged:>2026-09-01" --json number,title,labels,body
```

Merged PRs usually carry better descriptions and labels than individual commits; prefer them when the
project uses PRs. Ask for the range if there are no tags.

### 2. Classify each change

Map to the Keep a Changelog groups:

| Group | Typical sources |
|---|---|
| Added | `feat:` commits, PRs labelled feature or enhancement |
| Changed | behaviour changes, `refactor` that users notice, dependency upgrades with visible effect |
| Deprecated | features that still work but will go away |
| Removed | features that are gone |
| Fixed | `fix:` commits, bug labels |
| Security | vulnerability fixes; link the advisory if public |

Drop items users never see: CI tweaks, test refactors, typo fixes in comments, internal chores. Mention
them in one line at most ("Internal maintenance and dependency updates").

### 3. Rewrite for users

Turn each item into one sentence about the effect, not the implementation:

- Commit: `fix(api): handle null tz in parseDate`
- Note: "Dates without a time zone no longer cause an error when importing CSV files."

Merge duplicates (three commits fixing the same bug become one line). Keep PR or issue links at the end
of the line so readers can dig deeper.

### 4. Highlights, breaking changes, version

Pick at most three highlights for the top. Put breaking changes in their own section with an upgrade
step for each, because that is what readers fear missing. Suggest the semantic version: breaking change
gives a major bump, new features a minor bump, only fixes a patch bump. For 0.x projects, note that
minor bumps may break.

### 5. Deliver and ask before publishing

Edit `CHANGELOG.md` by inserting the new section above the previous one, keeping its existing style. Do
not create a tag or publish a GitHub release unless the user asks; if they do, show the command first:

```bash
gh release create v1.5.0 --title "v1.5.0" --notes-file notes.md --draft
```

`--draft` lets the user review on GitHub before anyone sees it.

## Output format

```markdown
## [1.5.0] - 2026-10-17

### Highlights
- **Bulk export**: export up to 10,000 records to CSV in one go (#341)
- Search is noticeably faster on large projects (#352)

### Breaking changes
- The `--legacy` flag is removed. Use `--format v1` instead (#338)

### Added
- Dark mode follows the operating system setting (#329)

### Fixed
- Dates without a time zone no longer fail CSV import (#347)
- The settings page remembers the selected tab after a reload (#350)

Internal maintenance and dependency updates.
```

## Pitfalls

- Do not invent features or impact that the commits do not support. When a commit message is too vague
  to classify, list it under "Needs review" and ask the user.
- Credit external contributors if the project normally does so.
- Security fixes for unpublished vulnerabilities: ask how much detail to disclose.
- Keep dates in ISO format (YYYY-MM-DD) so they sort and read the same everywhere.

## Scope

This skill summarises many changes for a release. Writing an individual commit message belongs to
commit-message-writer, and creating tags or fixing history belongs to git-helper.
