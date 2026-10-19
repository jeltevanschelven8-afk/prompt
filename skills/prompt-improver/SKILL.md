---
name: prompt-improver
description: >-
  Rewrite a prompt for Claude, ChatGPT or another AI model so it gets better results, by adding a
  clear goal, the missing context, constraints, examples and an explicit output format, then
  showing the before and after side by side with a short explanation of each change. Use this
  skill whenever the user shares a prompt and asks to improve, fix, sharpen or optimize it, writes
  a system prompt, or says "my prompt gives bad answers", "verbeter mijn prompt", "maak deze prompt
  beter" or "schrijf een goede prompt voor", including prompts for images and agents.
license: "MIT"
metadata:
  author: "prompt"
  category: "productivity"
  tags: "prompt, prompting, ai, claude, chatgpt, system prompt, verbeteren, instructies"
  version: "1.0.0"
  summary_nl: "Verbetert je AI-prompt met doel, context, eisen, voorbeelden en outputformaat, en laat voor en na zien."
---

# Prompt improver

A model can only use what is in the prompt. Weak prompts usually miss one of five things: the goal,
the context, the constraints, an example, or the shape of the answer. This skill finds which ones are
missing, adds them, and explains why, so the user learns to write the next prompt themselves.

## Workflow

1. **Understand the intent.** Ask what the prompt is for, which model or tool will run it, and what
   went wrong with the current output (too long, generic, wrong tone, made things up). If the user
   has a bad example output, ask for it; it shows the gap faster than a description.
2. **Diagnose against the five parts.**
   - **Goal**: what task, and what is the result used for? "Summarize" is weaker than "summarize so
     a busy manager can decide whether to read the full report".
   - **Context**: audience, background, source material, what has been tried.
   - **Constraints**: length, tone, language, things to avoid, and the reason for each. Models follow
     reasons better than bare rules, and reasons generalize to cases the rule did not cover.
   - **Examples**: one or two short input-output pairs fix tone and format better than adjectives.
     Vary them so the model does not copy one example too literally.
   - **Output format**: headings, bullets, JSON schema, table, or "only the email, no preamble".
3. **Rewrite.** Put long source material first and the question last; use simple tags or headings
   (`<document>`, `## Task`) to separate parts. Prefer plain, calm language over ALL-CAPS: emphasis
   in capitals often makes models overly rigid. Say what to do rather than only what to avoid.
4. **Add an escape hatch** where useful: "If information is missing, say what you need instead of
   guessing." This cuts made-up answers.
5. **Show before/after and the why.** Keep the explanation to one line per change.
6. **Suggest a test.** Run the new prompt on 2-3 different inputs, including a tricky one, and compare.
   Offer to run it now if the target is Claude.

## Output template

```markdown
### Before
<original prompt>

### After
<improved prompt>

### What changed and why
- Added goal: <...> -> the model can judge what matters
- Added audience: <...> -> sets vocabulary and depth
- Added format: <...> -> output can be pasted directly
- Removed: <...> -> was contradicting <...>

### Try it with
1. <normal input>  2. <edge case>  3. <input where it should ask for more info>
```

## Example

Before:

```
Write a LinkedIn post about our new feature. Make it engaging!!!
```

After:

```
## Task
Write a LinkedIn post announcing our new feature, aimed at operations managers at mid-size
logistics companies. The goal is clicks to the demo page, not likes.

## Context
Feature: automatic route re-planning when a driver reports a delay. It saved our pilot customer
(a 40-truck carrier) about 6 hours of planner time per week.

## Constraints
- 80-120 words; people skim on mobile.
- Plain, confident tone; no hype words like "revolutionary", because this audience distrusts them.
- One concrete number from the pilot.
- End with a single call to action linking to {demo_url}.

## Format
Only the post text, then three hashtag suggestions on a separate line.
```

Why: the goal (clicks) and audience change what "engaging" means; the pilot number gives credibility;
the reason behind "no hype" lets the model avoid similar words that were not listed.

## Pitfalls

- Do not change what the user asked for; improve how it is asked. If you think the goal itself is off,
  say so separately.
- Do not invent facts (numbers, product names) to fill a prompt; use placeholders like `{demo_url}`.
- Longer is not automatically better. Cut instructions that do not change the output.
- For image models, focus on subject, style, composition, lighting and aspect ratio instead.

## Scope

For improving prompts and system prompts. Building a reusable Claude Code skill is a different task;
use a skill-building workflow for that.
