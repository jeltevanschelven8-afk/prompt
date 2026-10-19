---
name: script-automator
description: >-
  Automate a repetitive task with a small, readable PowerShell, Python or bash script that is safe to
  run - dry-run mode by default, clear logging, input checks, sensible defaults and plain instructions
  on how to run and schedule it. Use this skill whenever the user describes something they do by hand
  over and over, such as renaming exports, merging CSV files, backing up a folder, converting files or
  calling an API daily, or says "automate this", "write me a script", "can this be done automatically",
  "dit doe ik elke week met de hand", "schrijf een script dat" or "kan dit automatisch".
license: "MIT"
metadata:
  author: "prompt"
  category: "automation"
  tags: "automation, script, powershell, python, bash, dry run, automatiseren, taakplanner"
  version: "1.0.0"
  summary_nl: "Automatiseert een terugkerende klus met een klein, veilig script met proefdraaimodus, logging en uitleg om te draaien."
---

# Script automator

A good automation script is boring: it does one job, tells you what it is about to do, does nothing
harmful by default, and leaves a log you can read when something goes wrong. This skill turns a task
the user does by hand into such a script, and explains how to run it without needing to be a
programmer.

## Workflow

### 1. Pin down the task

Ask, or infer from what the user shared:

- Input: which folder, files, website or system, and an example of real input.
- Output: what should exist afterwards, and an example of the expected result.
- Frequency and trigger: once, daily, on a new file.
- Environment: Windows, macOS or Linux, and what is installed (Python version, PowerShell 5.1 or 7).

Walk through one concrete example by hand with the user before writing code; it uncovers the edge
cases (empty files, duplicate names, spaces in paths) that break scripts later.

### 2. Pick the language

| Situation | Choice | Why |
|---|---|---|
| Windows, files, Office, scheduled tasks | PowerShell | built in, no installation |
| Data work, CSV/Excel/JSON, APIs, cross-platform | Python (standard library first) | readable, portable |
| Linux/macOS servers, chaining CLI tools | bash | already there, good for glue |

Prefer the standard library. Each extra dependency is something the user has to install and keep
working.

### 3. Write it with safe defaults

Every script gets the same backbone:

- **Dry run by default**: it prints what it would do; a flag such as `--apply` or `-Apply` makes it act.
- **Configuration at the top** or as arguments, never buried paths in the middle.
- **Validation** of inputs before touching anything, with a clear message on what is wrong.
- **Logging** to the console and a timestamped log file.
- **Non-destructive actions**: copy or move to an archive folder instead of deleting; never overwrite
  without a flag.
- **Exit codes**: 0 on success, non-zero on failure, so schedulers notice problems.
- **Secrets** read from environment variables or the OS credential store, never written into the script.

Python skeleton:

```python
import argparse, logging, sys
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser(description="Merge monthly CSV exports into one file.")
    p.add_argument("source", type=Path)
    p.add_argument("--out", type=Path, default=Path("merged.csv"))
    p.add_argument("--apply", action="store_true", help="actually write output (default: dry run)")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler("merge.log")])
    if not args.source.is_dir():
        logging.error("Source folder not found: %s", args.source)
        return 1
    files = sorted(args.source.glob("*.csv"))
    logging.info("Found %d files", len(files))
    if not args.apply:
        logging.info("Dry run - would write %s. Re-run with --apply.", args.out)
        return 0
    ...  # do the work
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

In PowerShell, use `[CmdletBinding(SupportsShouldProcess)]` so `-WhatIf` and `-Confirm` work for free,
`Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`. In bash, start with
`set -euo pipefail` and quote every variable.

### 4. Test on a copy

Run the dry run on the user's real input (or a copy of it) and show the output. Only run with the
apply flag after the user agrees the plan looks right, ideally first on a test folder.

### 5. Explain how to run and schedule

Give copy-paste commands for their system, for example
`python merge_exports.py "C:\Exports" --apply`, plus how to schedule it: Task Scheduler
(`Register-ScheduledTask`) on Windows, `cron` or a `systemd` timer on Linux, `launchd` on macOS. Note
that on Windows, running local PowerShell scripts may require `Set-ExecutionPolicy -Scope CurrentUser
RemoteSigned`; explain what that changes and let the user decide.

## Output format

1. One-paragraph summary: what the script does and its safety behaviour.
2. The script, with short comments on non-obvious lines.
3. Example dry-run output (real if you ran it, labelled "expected" if not).
4. How to run, how to apply, where the log goes, how to schedule, how to undo.

## Pitfalls and when to stop

- Ask before the script deletes, sends email, posts to an API or changes shared systems.
- Do not scrape sites in ways their terms forbid, and respect rate limits on APIs.
- Paths with spaces, non-ASCII names and different date formats break naive scripts; handle them.
- If the task needs a full application, a database or a UI, say so instead of growing the script.

## Scope

General-purpose task automation. Sorting and deduplicating a messy folder has its own dedicated
workflow in file-organizer; CI pipelines belong to github-actions-ci.
