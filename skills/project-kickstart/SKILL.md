---
name: project-kickstart
description: >-
  Start a new software project the right way, by clarifying the goal, choosing a sensible and
  boring stack, scaffolding the folder structure, writing a README and .gitignore, adding a test
  setup, and ending with a first version that actually runs. Use this skill whenever the user says
  "start a new project", "set up a repo", "scaffold an app", "bootstrap", "new Python/Node project",
  "nieuw project opzetten", "begin een nieuwe app" or "zet de basis neer", or has an idea and an
  empty folder and asks where to begin.
license: "MIT"
metadata:
  author: "prompt"
  category: "workflow"
  tags: "project, scaffold, setup, readme, gitignore, tests, nieuw project, opzetten"
  version: "1.0.0"
  summary_nl: "Zet een nieuw softwareproject goed op: doel, stack, mappen, README, .gitignore, tests en een eerste werkende versie."
---

# Project kickstart

The first hour of a project sets habits for the rest of it. A project that starts with a runnable
"hello world", a passing test and a README stays easy to work on; one that starts with a pile of
generated boilerplate and no way to run it rarely recovers. This skill aims for the smallest
foundation that runs, tests and explains itself.

## Workflow

1. **Clarify the goal.** Ask: what should the first version do (one sentence), who uses it, where
   does it run (CLI, web, desktop, script on a server), and what languages the user knows. Also ask
   whether a folder or repo already exists, so nothing gets overwritten.
2. **Pick a stack.** Prefer what the user knows and what is well documented. Propose one option with
   a one-line reason and mention one alternative. Sensible defaults:

   | Kind of project | Default stack |
   |---|---|
   | Script / CLI / data | Python 3.12, `uv` or `venv`, `pytest`, `ruff` |
   | Web API | Python + FastAPI, or Node + Express/Fastify (TypeScript) |
   | Web front end | Vite + React or plain HTML/JS for small things, `vitest` |
   | Full-stack app | Next.js or SvelteKit, one repo |

   Avoid adding a database, Docker or CI on day one unless the goal needs it; each adds setup that
   can wait until there is code worth deploying.
3. **Confirm the plan.** Show the folder tree and commands before creating files, because the user
   should agree on names and location.
4. **Scaffold.** Prefer the official generator when one exists (`npm create vite@latest`, `uv init`)
   since it stays current. Then add only what is missing.
5. **Write the essentials.** README, `.gitignore` for the stack, a config example file such as
   `.env.example` with placeholder values (and `.env` in `.gitignore`, so local settings never get
   committed), and a single test.
6. **Make it run.** Implement the smallest slice of the real goal, not just "hello world" if you can
   avoid it. Run it, run the tests, and show the actual output.
7. **Initialize git** if the user wants it: `git init`, first commit "Initial project scaffold".
8. **Hand over next steps**: two or three concrete tasks to build next.

## Example: Python CLI

```
weather-cli/
  src/weather_cli/__init__.py
  src/weather_cli/main.py
  tests/test_main.py
  pyproject.toml
  README.md
  .gitignore
  .env.example
```

```bash
uv init --package weather-cli && cd weather-cli
uv add httpx && uv add --dev pytest ruff
uv run pytest        # 1 passed
uv run weather-cli Utrecht
```

`.gitignore` for Python at minimum: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.env`, `dist/`.

## README template

```markdown
# <Project name>

<One sentence: what it does and for whom.>

## Quick start
<install command>
<run command>

## Development
<test command>   <lint command>

## Project structure
<3-6 lines on the main folders>

## Status
First version: <what works>. Next: <what is planned>.
```

## What the user receives

```markdown
**Project:** weather-cli (Python 3.12, uv, pytest, ruff) in C:\dev\weather-cli
**Runs:** `uv run weather-cli Utrecht` -> "Utrecht: 14 C, light rain"
**Tests:** 1 passed   **Lint:** clean
**Created:** README.md, .gitignore, .env.example, pyproject.toml, src/, tests/
**Git:** initialized, 1 commit
**Next:** 1) add --days option  2) cache responses  3) nicer error when the city is unknown
```

## Pitfalls and when to ask

- The target folder is not empty: list what is there and ask before adding or replacing anything.
- Do not claim it runs until you ran it; paste the real output, including failures.
- Pin major versions in the dependency file so the project still installs next month.
- Do not install global tools or change system settings without asking; prefer project-local tools.
- If the user is a beginner, keep the stack minimal and explain each file in one line.

## Scope

For starting new projects. For adding features to an existing codebase, restructuring a large
project, or setting up deployment and CI, treat those as separate tasks once this foundation runs.
