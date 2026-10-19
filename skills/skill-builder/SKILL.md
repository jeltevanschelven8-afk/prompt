---
name: skill-builder
description: >-
  Create a new Claude Code skill (a SKILL.md with frontmatter and instructions) from an idea or
  from a workflow the user just did, then test and refine it. Use this skill whenever the user
  says "skill maken", "maak een skill", "nieuwe skill", "create a skill", "make a skill", "turn this
  into a skill", "save this as a skill", "slash command maken" or "kun je hier een skill van maken",
  or wants Claude to remember a repeatable way of working, even if they never say the word skill.
  Covers intent, a description that triggers well, structure, saving, testing and iterating.
license: "MIT"
metadata:
  author: "prompt"
  category: "workflow"
  tags: "skill, claude code, skill maken, slash command, automation, workflow, nieuwe skill, prompt"
  version: "1.0.0"
  summary_nl: "Maakt samen met jou een nieuwe Claude Code skill: goede beschrijving, duidelijke stappen, opslaan en testen."
---

# Skill builder

A skill is a folder with a `SKILL.md` that teaches Claude a repeatable way of doing a task. Good
skills trigger at the right moment and produce consistent results; weak ones never trigger or are
too vague to help. This workflow follows Anthropic's skill-creator approach: capture intent, write,
test with real prompts, and iterate.

## Anatomy

```
my-skill/
  SKILL.md        required: YAML frontmatter + Markdown instructions
  scripts/        optional: helper scripts Claude can run (deterministic, repeatable steps)
  references/     optional: longer docs Claude reads only when needed
  assets/         optional: templates, images, example files used in the output
```

Frontmatter needs at least `name` (lowercase, hyphens, equal to the folder name) and `description`.

## Progressive disclosure

Claude loads skills in layers, which is why the parts have different jobs:

1. **Description**: always in context, for every skill. It decides whether the skill triggers, so
   it must be precise and short (a few sentences).
2. **Body**: loaded only when the skill triggers. Keep it under about 500 lines; past that, Claude
   spends attention on text it does not need.
3. **Bundled files**: read only when the body points to them. Put long reference tables, API docs
   or examples here, and say in the body when to read which file.

## Workflow

1. **Capture intent.** If the conversation already contains the workflow ("turn this into a
   skill"), extract it: the steps taken, the tools used, the corrections the user made. Otherwise
   ask: What should the skill do? When should it trigger (what would the user type)? What does a
   good result look like? Are there edge cases or things to avoid? Keep it to a few questions.
2. **Write the description.** Say what it does and when to use it, and be slightly pushy, because
   Claude tends to under-use skills. List concrete phrases users type, in the languages they use.

   Weak: `description: Helps with invoices.`

   Strong: `description: Create, check and summarize invoices from PDFs or emails. Use this skill
   whenever the user mentions an invoice, factuur, bill or payment request, asks to extract amounts,
   due dates or VAT, or says "verwerk deze factuur", even if they do not ask for a skill.`

3. **Write the body.** Use imperative voice and this structure: a short purpose paragraph, numbered
   workflow steps, an output template with a small example, pitfalls and when to ask the user, and a
   scope note on what the skill is not for.
4. **Explain the why instead of shouting.** "Use absolute paths, because the scheduler starts in a
   different directory" works better than "ALWAYS USE ABSOLUTE PATHS". Models generalize from
   reasons to cases you did not list; bare capitalized rules make them rigid and literal.
5. **Add an output template and examples.** A concrete template is the single most effective way to
   get consistent output. One or two short input-output examples show tone and level of detail.
6. **Save it.** Personal skills go in `~/.claude/skills/<name>/SKILL.md` (on Windows
   `C:\Users\<you>\.claude\skills\<name>\SKILL.md`). Team skills that belong to a codebase go in
   `.claude/skills/<name>/SKILL.md` in the project and are committed with it. Confirm the location
   with the user and check that no existing skill with that name would be overwritten.
7. **Test with 2-3 realistic prompts.** Write prompts the way a real user would type them, including
   one casual or indirect phrasing, for example "can you sort out this factuur from KPN?" Start a new
   session (skills load at start), run them, and check: did it trigger, did it follow the steps, does
   the output match the template? Also try one prompt that should not trigger it.
8. **Iterate.** For each failure, fix the cause: missing trigger phrases go into the description,
   skipped steps get a reason, inconsistent output gets a tighter template. Re-run the same prompts
   so you can compare. Two or three rounds is usually enough.

## Template

```markdown
---
name: invoice-helper
description: >-
  <What it does>. Use this skill whenever the user <situations>, says "<phrase>", "<phrase>"
  or "<Dutch phrase>", even if <indirect case>.
---

# Invoice helper

<1-3 sentences: purpose and why this approach works.>

## Workflow
1. <Step> - <why it matters>
2. ...

## Output format
<template + small example>

## Pitfalls and when to ask
- ...

## Scope
<what this skill is not for>
```

## What the user receives

```markdown
**Skill:** invoice-helper  ->  ~/.claude/skills/invoice-helper/SKILL.md
**Triggers on:** invoice, factuur, "verwerk deze factuur", extract amounts or VAT
**Tested:** 3/3 prompts triggered and produced the table; 1 negative prompt correctly ignored
**Changed after testing:** added "bill" to the description; tightened the output table
**Try it:** start a new session and type "verwerk deze factuur" with a PDF attached
```

## Pitfalls

- Too broad ("helps with documents") triggers everywhere or nowhere; narrow it to one job.
- Do not report a skill as working before the test prompts were actually run; if you could not run
  them, say so and hand the user the prompts to try.
- Keep secrets and personal data out of skills; they are plain text files and often get shared.
- One skill per job. If the body grows into two workflows, split it.

## Sharing

A finished skill can be shared with others on the Prompt marketplace: open the skill in the Prompt
app and press the "Deel op marktplaats" button.

## Scope

For creating and improving skills. For one-off prompts that will not be reused, improving the prompt
itself is quicker; for settings, hooks or permissions, edit the Claude Code configuration instead.
