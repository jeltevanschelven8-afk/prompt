---
name: git-helper
description: >-
  Solve git problems in plain language: undo a commit, fix a bad merge, untangle branches, move work
  to the right branch, resolve conflicts and recover lost commits with the reflog. Explains every
  command before running it and asks for confirmation before anything that rewrites history. Use this
  skill whenever the user is stuck or worried in git, for example "undo my last commit", "I committed
  to main by accident", "my merge went wrong", "detached HEAD", "I lost my changes", "ik heb per ongeluk
  gecommit", "mijn branch is kapot" or "hoe draai ik dit terug", even if they do not name the exact
  git command.
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "git, undo, reflog, merge, rebase, branches, terugdraaien, versiebeheer"
  version: "1.0.0"
  summary_nl: "Lost git-problemen op in gewone taal: commits terugdraaien, merges herstellen en verloren werk terugvinden."
---

# Git helper

Most git panic comes from not knowing what state the repository is in. This skill first finds out
exactly where things stand, then picks the least destructive fix, explains it in plain words and only
then runs it. Almost nothing in git is truly lost for about 90 days, so stay calm and make the user
calm too.

## Workflow

### 1. Diagnose before touching anything

Run read-only commands and summarise what you see in one or two sentences:

```bash
git status
git log --oneline --graph --decorate -n 15
git branch -vv          # which branch tracks what, ahead/behind counts
git stash list
```

Answer three questions for yourself: which branch is checked out, is there uncommitted work, and has
the problem already been pushed? The last one decides everything that follows, because rewriting
pushed history affects other people.

### 2. Make a safety net

Before any change that moves branch pointers, create a backup branch. It costs nothing and turns every
mistake into a one-line recovery:

```bash
git branch backup/before-fix
```

If there is uncommitted work, suggest `git stash push -m "before fix"` or a WIP commit first.

### 3. Pick the fix

Prefer the reversible option. Use this table as a starting point:

| Situation | Not pushed yet | Already pushed |
|---|---|---|
| Undo last commit, keep changes | `git reset --soft HEAD~1` | `git revert HEAD` |
| Fix last commit message or add a forgotten file | `git commit --amend` | new commit instead |
| Committed on main instead of a feature branch | `git branch feature && git reset --keep HEAD~1` | move work with a new branch, revert on main |
| Bad merge | `git reset --keep ORIG_HEAD` | `git revert -m 1 <merge-sha>` |
| Discard local edits in one file | `git restore <file>` | same |
| Lost commit after reset or rebase | `git reflog`, then `git branch rescue <sha>` | same |
| Detached HEAD with new commits | `git switch -c <new-branch>` | same |
| Conflict in the middle of a rebase | fix files, `git add`, `git rebase --continue` (or `--abort`) | same |

Prefer `--keep` over `--hard`: it refuses to throw away uncommitted changes, whereas `--hard` silently
deletes them.

### 4. Explain, then confirm

For each command, write one line on what it does and what it changes. For history-rewriting or
destructive commands (`reset --hard`, `rebase`, `commit --amend` on shared commits, `push --force`,
`branch -D`, `clean -fd`, `filter-repo`), stop and ask for an explicit yes. Say who could be affected:
"This rewrites `main` on the remote; anyone who pulled it will need to reset their copy."

When a force push is really needed, use `git push --force-with-lease`, which refuses to overwrite work
someone else pushed in the meantime.

### 5. Verify

Run `git log --oneline --graph -n 10` and `git status` again and show the user that the result
matches what they wanted. Tell them the backup branch can be removed later with
`git branch -d backup/before-fix` once they are happy.

## Output format

```text
What happened: you committed 2 files to main; nothing is pushed yet.
Plan:
  1. git branch backup/before-fix       - safety copy of the current state
  2. git branch feature/login           - new branch that keeps your commit
  3. git reset --keep HEAD~1            - moves main back one commit (your files stay safe on feature/login)
  4. git switch feature/login           - continue working there
Risk: low, nothing on the remote changes. Shall I run this?
```

After running: show the new log graph and one sentence confirming the state.

## Recovering lost work

The reflog records every position HEAD has been at, including commits that no branch points to:

```bash
git reflog -n 30
git show <sha>                 # inspect before restoring
git branch rescue/<topic> <sha>
```

For a dropped stash, `git fsck --lost-found` lists dangling commits that may contain it. Uncommitted
changes that were never staged cannot be recovered by git; check the editor's local history instead
and say so honestly.

## Pitfalls and when to stop

- Shared branches (main, develop, release): prefer `revert` over rewriting. Ask whether the team
  allows force pushes before suggesting one.
- Large conflicts: do not resolve semantic conflicts by guessing. Show both sides and ask which
  behaviour the user wants.
- Submodules, LFS and hooks behave differently; mention it when they show up in `git status`.
- If the repository looks corrupt (`fatal: bad object`), stop and suggest making a full copy of the
  folder before trying anything.
- Never invent a commit sha or the output of a command; run it and read it.

## Scope

This skill handles local and remote git operations and recovery. Writing the commit message itself is
covered by commit-message-writer, removing leaked credentials from history by secrets-scanner, and CI
configuration by github-actions-ci.
