---
name: explain-codebase
description: >-
  Get oriented in an unfamiliar repository fast: map the folder structure, find
  the entry points, trace how a request or job flows through the code, identify
  the key modules and conventions, and produce a concise onboarding overview.
  Use this skill whenever the user opens a new project and asks how does this
  codebase work, where do I start, what does this repo do, where is X handled,
  or explain the architecture, and for Dutch phrases such as "leg deze codebase
  uit", "hoe zit dit project in elkaar" or "waar begin ik in deze repo". Use it
  also before making a change in code the user has not seen before.
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "onboarding, architecture, codebase, repository, overview, documentation, uitleg, inwerken, projectstructuur"
  version: "1.0.0"
  summary_nl: "Brengt een onbekende repository in kaart: structuur, startpunten, datastromen en kernmodules, als inwerkoverzicht."
---

# Explain codebase

Reading an unfamiliar repository file by file is slow and you lose the thread. This skill works top-down instead: what does the project claim to do, how is it started, what happens on one real request, and which few modules matter most. The result is an overview a new team member could read in ten minutes.

## Workflow

1. **Read the signposts first.** README, CONTRIBUTING, docs folder, and any architecture notes. Then the manifest files, because they reveal the stack and the scripts people actually run: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, `composer.json`, `Dockerfile`, `docker-compose.yml`, CI config in `.github/workflows`.
2. **Map the structure.** List the top two levels of folders, skipping dependency and build output (`node_modules`, `.venv`, `dist`, `target`). For a quick size picture, count files per top folder. Note which folders are source, tests, config, scripts, generated code.
3. **Find the entry points.** Look for where execution starts: `main` functions, `bin` entries, `scripts.start`, `if __name__ == "__main__"`, `cmd/` folders, server bootstrap files (`app.ts`, `server.py`, `Program.cs`), route registrations, CLI command definitions, scheduled job and queue consumer registrations.
4. **Trace one real flow end to end.** Pick the most representative action (for a web app: one API request; for a CLI: one command; for a library: the main public function). Follow it through routing, validation, business logic, persistence and response, noting file and function at each hop. One concrete trace teaches more than ten folder descriptions.
5. **Identify the key modules.** Usually five to ten carry most of the weight. Signals: imported by many files, large and frequently changed (`git log --format= --name-only | sort | uniq -c | sort -rn | head -20`), or named after domain concepts.
6. **Note conventions and gotchas.** Dependency injection style, error handling pattern, how config and environment are loaded, naming rules, test layout, code generation steps, anything surprising.
7. **Check how to run it.** Find the install, run and test commands. Only run them if the user wants you to; say plainly whether you verified them or only read them.
8. **Write the overview** using the template below, and offer to go deeper on any part.

## Output template

```markdown
# <Project> in 10 minutes

**What it is:** One or two sentences in plain language.
**Stack:** TypeScript, Express, PostgreSQL via Prisma, Jest, deployed as Docker image.

## Layout
| Folder | Purpose |
|---|---|
| src/routes | HTTP route handlers, one file per resource |
| src/services | Business logic, no HTTP knowledge |
| prisma/ | Schema and migrations |

## Entry points
- `src/server.ts` starts the HTTP server
- `src/jobs/index.ts` registers nightly jobs

## How a request flows: POST /orders
1. `routes/orders.ts` validates the body with zod
2. `services/orderService.ts#create` checks stock and prices
3. `repositories/orderRepo.ts` writes via Prisma in a transaction
4. `events/publish.ts` emits `order.created`

## Key modules
...
## Conventions and gotchas
...
## Run it
`npm install`, `npm run dev`, `npm test` (read from package.json, not executed)

## Open questions
...
```

Use a small text diagram for the flow when it helps, for example `route -> service -> repo -> db`.

## Pitfalls and when to ask

- Big monorepos: ask which package or service the user cares about before mapping everything.
- Do not guess what a module does from its name alone; open it. Mark anything inferred rather than read as an assumption.
- Generated or vendored code can dominate file counts; exclude it from the key modules.
- Stale docs are common. When README and code disagree, trust the code and point out the mismatch.
- Keep it short. An onboarding overview that is longer than the code it explains has failed.

## Scope

This skill explains and orients. It does not change code, write permanent documentation files unless asked, or review quality (see code-review-buddy).
