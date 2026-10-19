---
name: readme-writer
description: >-
  Write a new README or improve an existing one for a software project, based on what is actually in
  the repository. Covers what the project is and why it exists, a quick start that really works, usage
  examples, configuration, and how to contribute, with every command checked against the repo. Use this
  skill whenever the user asks to "write a README", "improve the README", "document this repo", "add
  installation instructions", "make the readme clearer", or says "schrijf een README", "maak de readme
  beter" or "documenteer dit project", even if they only point at a folder.
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "readme, documentation, docs, open source, quick start, documentatie, handleiding, markdown"
  version: "1.0.0"
  summary_nl: "Schrijft of verbetert de README van je project, met een snelstart die echt werkt en commando's die gecontroleerd zijn."
---

# README writer

A README is the front door of a project. Most readers spend under a minute on it and want three answers:
what is this, is it for me, and how do I get it running. A README that answers those fast, with commands
that actually work, earns more users and fewer issues than a long one full of marketing.

## Workflow

1. **Read the repo before writing a word.** Look at the manifest files (`package.json`, `pyproject.toml`,
   `Cargo.toml`, `go.mod`, `Makefile`, `Dockerfile`), the entry points, the scripts section, existing docs,
   example config files and the CI workflow. CI is valuable because it shows the commands that really run
   on a clean machine.
2. **Find the one-sentence purpose.** Write down what the project does for whom, in plain words. If you
   cannot tell from the code, ask the user instead of guessing; a wrong pitch is worse than none.
3. **Reconstruct the quick start.** List the minimum steps from clone to first visible result: install
   prerequisites (with versions from the manifest or CI), install dependencies, configure, run. Prefer the
   project's own scripts (`npm run dev`, `make run`) over generic commands.
4. **Verify the commands.** Where it is safe and cheap, run them (install, build, `--help`, tests). Where
   you cannot run them, at least confirm every script name, flag, file path and port exists in the repo.
   Mark anything you could not verify so the user can check it.
5. **Draft using the template below**, dropping sections that do not apply. A tiny library does not need a
   Deployment section.
6. **When improving an existing README**, keep what is correct and the author's tone. Show a short list of
   what you changed and why, rather than silently rewriting everything.

## Template

````markdown
# project-name

One sentence: what it does and for whom.

![screenshot or demo gif, if the project has a UI](docs/screenshot.png)

## Why
Two or three sentences on the problem it solves or what makes it different.

## Quick start
```bash
git clone https://github.com/owner/project-name
cd project-name
npm install
npm run dev     # opens http://localhost:5173
```

## Usage
The two or three most common tasks, each with a copy-pasteable example and its expected output.

## Configuration
| Variable | Default | What it does |
|---|---|---|
| `PORT` | `3000` | Port the server listens on |

## Contributing
How to run tests, code style, how to propose a change.

## License
MIT (see LICENSE)
````

## Writing guidance

- **Lead with the result, not the history.** "Converts Markdown to slide decks" beats "This project was
  started in 2023 as an experiment".
- **Show expected output** after commands where it helps. Readers then know they succeeded.
- **One way to install first.** Mention alternatives (Docker, Homebrew) after the main path, not mixed in.
- **Configuration as a table** with defaults, taken from the example config or the code that reads the
  environment. Never put real secrets or credentials in examples; use clearly fake placeholders.
- **Badges sparingly.** Build status and license are useful; ten badges are noise.
- **Relative links** to files in the repo (`docs/`, `CONTRIBUTING.md`) so they work on forks.
- Match the audience: a CLI tool for developers can be terse; an app for non-technical users needs more
  screenshots and fewer terminal commands.

## What you hand back

1. The README (as a file written to `README.md`, or as a proposed new version if one already exists and
   the user has not asked you to overwrite it).
2. A short verification note, for example:

```
Verified: npm install, npm run build, npm test (passing)
Not verified: Docker section (Docker not available here)
Assumed: Node 20+ (from .nvmrc)
```

## When to stop and ask

- The purpose of the project is unclear from the code.
- The quick start needs credentials, paid services or private infrastructure you cannot see.
- Existing docs contradict the code (for example an old port or a removed command). Point out the
  conflict instead of picking one silently.
- The license is missing; do not invent one, ask which the author wants.

## Scope

This skill is for project READMEs. For full documentation sites, API references or runbooks, a broader
documentation workflow fits better. It does not write marketing copy for a landing page.
