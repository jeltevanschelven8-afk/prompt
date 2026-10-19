---
name: commit-message-writer
description: >-
  Write clear, conventional commit messages from the staged diff. Reads what actually changed, picks
  the right Conventional Commits type and scope, writes a summary line under 72 characters and a body
  that explains why the change was made. Use this skill whenever the user asks to "write a commit
  message", "commit this", "what should my commit say", "make this a conventional commit", wants to
  split a messy change into several commits, or says "schrijf een commitbericht", "maak een commit
  message" or "wat zet ik in mijn commit". Also use it before committing on the user's behalf.
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "git, commit, conventional commits, commitbericht, changelog, diff, versiebeheer"
  version: "1.0.0"
  summary_nl: "Schrijft heldere commitberichten volgens Conventional Commits op basis van je gestagede wijzigingen."
---

# Commit message writer

A good commit message is written for the person reading `git log` or `git blame` a year from now. The
diff already shows *what* changed; the message has to say *why*, in a form that tools like changelog
generators can parse. This skill reads the staged changes and writes that message.

## Workflow

### 1. Read the real change

```bash
git diff --staged --stat
git diff --staged
git log --oneline -n 10        # learn the repo's existing style
```

If nothing is staged, say so and show `git status` instead of guessing from unstaged files. Ask whether
the user wants everything staged (`git add -A`) or only part of it.

Check the repo for its own rules first: `CONTRIBUTING.md`, a `commitlint.config.*`, or a pattern in the
recent log. Follow the house style when one exists, because consistency beats any external convention.

### 2. Check that it is one change

If the diff mixes unrelated things (a bug fix plus a dependency bump plus formatting), propose
splitting it. Suggest concrete groups and the commands to stage them:

```bash
git restore --staged .
git add src/auth/ && git commit        # fix(auth): ...
git add package.json package-lock.json && git commit   # chore(deps): ...
```

Small focused commits make reverts and reviews much easier, which is the main reason to split.

### 3. Choose type and scope

| Type | Use for |
|---|---|
| feat | new behaviour a user can notice |
| fix | a bug fix |
| refactor | code change without behaviour change |
| perf | faster or lighter, same behaviour |
| docs | documentation only |
| test | adding or fixing tests |
| build / ci | build system, dependencies, pipelines |
| chore | housekeeping that fits nowhere else |

Scope is optional: the module, package or area touched (`auth`, `api`, `ui`). Add `!` after the type
and a `BREAKING CHANGE:` footer when callers have to change their code.

### 4. Write the message

- Summary: imperative mood ("add", not "added"), lowercase after the colon, no trailing period, at most
  72 characters, ideally around 50.
- Blank line, then a body wrapped at 72 characters: the problem, why this approach, anything surprising.
  Skip the body only for truly trivial changes.
- Footers: `Fixes #123`, `Refs #45`, `BREAKING CHANGE: ...`, co-author lines the user asked for.

Do not describe things the diff does not contain, and do not claim tests pass unless you ran them.

### 5. Commit only when asked

Show the message first. If the user wants you to commit, use a file or heredoc so the formatting
survives:

```bash
git commit -F- <<'EOF'
fix(auth): refresh session before it expires
...
EOF
```

Let pre-commit hooks run; if a hook fails, report the failure and fix the cause rather than skipping it.

## Output format

````text
Proposed commit (1 of 1):

```
fix(cart): keep discount when quantity changes

Changing the quantity rebuilt the cart line from the product price and
dropped any applied coupon, so customers saw the full price at checkout.
The line now recalculates from the stored discount instead.

Fixes #212
```

Want me to commit this, or adjust the wording?
````

When proposing a split, list each commit with its files and message in the same format.

## Pitfalls

- Generic summaries like "update files" or "fix bug" carry no information; name the behaviour.
- Do not paste the diff into the body. Summarise intent.
- Watch for secrets or large generated files in the staged diff and flag them before committing.
- Amending a commit that is already pushed rewrites history; ask before doing it.

## Scope

This skill writes messages for individual commits. Summarising many commits for a release is the job of
release-notes-writer; fixing a commit that went to the wrong branch belongs to git-helper.
