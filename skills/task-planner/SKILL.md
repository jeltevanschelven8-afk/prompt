---
name: task-planner
description: >-
  Break a goal or project into a concrete, doable plan with milestones, ordered tasks, rough time
  estimates, dependencies and one clear first next action, delivered as a Markdown checklist. Use
  this skill whenever the user has a goal that feels big or vague and wants structure, for example
  "plan this project", "break this down", "where do I start", "make a roadmap", "maak een
  planning", "help me dit op te delen in stappen" or "wat moet ik eerst doen", whether it is a
  software release, a move, an event, a thesis or a side project.
license: "MIT"
metadata:
  author: "prompt"
  category: "productivity"
  tags: "planning, project, milestones, checklist, takenlijst, roadmap, stappenplan, estimates"
  version: "1.0.0"
  summary_nl: "Maakt van een groot doel een concreet stappenplan met mijlpalen, schattingen, afhankelijkheden en een eerste actie."
---

# Task planner

A plan is useful when it tells you what to do next and how you will know you are done. Long lists of
vague tasks do the opposite: they look productive and stall. This skill produces a short, ordered plan
where every task is small enough to start today and the first action is obvious.

## Workflow

1. **Restate the goal as an outcome.** Turn "work on my website" into "portfolio site live at my
   domain with 5 projects, by 1 December". Ask about anything that changes the plan a lot:
   deadline, hours per week available, budget, who else is involved, what already exists.
   Ask at most three questions; make sensible assumptions for the rest and list them.
2. **Define done.** Two or three checkable criteria. These stop the project from growing forever.
3. **Cut into milestones.** 3-6 milestones, each a visible result (a working prototype, a booked
   venue), not an activity ("research"). Milestones give natural moments to check progress.
4. **List tasks per milestone.** Each task starts with a verb, has one owner, and fits in roughly
   half a day or less. If a task is bigger or you cannot picture the first minute of it, split it.
5. **Estimate.** Use ranges (1-2 h) because single numbers suggest false precision. Add a buffer of
   about 20-30% at milestone level; unknowns always show up.
6. **Mark dependencies.** Note "needs T3" where a task cannot start before another. Order tasks so
   blockers come first, and point out the critical path (the chain that sets the end date).
7. **Pick the first next action.** One physical step that takes under 30 minutes, such as "email the
   venue for availability on 14 March". Starting is the hardest part; make it easy.
8. **Check feasibility.** Add up estimates against the available time. If it does not fit, say so and
   offer options: move the date, drop scope, or get help.

## Output template

```markdown
# Plan: <outcome> by <date>

**Done when:** <criterion 1>; <criterion 2>
**Assumptions:** <e.g. 6 h/week available, no budget for paid tools>
**Total estimate:** <x-y h> (+25% buffer) -> fits / does not fit before <date>

## Milestone 1 - <visible result> (target <date>)
- [ ] T1 <verb + task> (1-2 h)
- [ ] T2 <verb + task> (2 h, needs T1)

## Milestone 2 - ...

**Critical path:** T1 -> T2 -> T5 -> T8
**Risks:** <risk> -> <mitigation>
**First next action (today, <30 min):** <one concrete step>
```

## Example (short)

Goal: "I want to launch a newsletter."

```markdown
# Plan: first newsletter issue sent to 50 subscribers by 30 November

**Done when:** issue #1 sent; signup page live; next 3 topics chosen
**Assumptions:** 4 h/week, free tier of a newsletter tool

## Milestone 1 - Setup ready (target 3 Nov)
- [ ] T1 Compare two newsletter tools and pick one (1 h)
- [ ] T2 Create account and signup page (1-2 h, needs T1)
## Milestone 2 - First issue written (target 17 Nov)
- [ ] T3 List 10 topic ideas, pick 4 (1 h)
- [ ] T4 Write and edit issue #1 (3-4 h, needs T3)
## Milestone 3 - Launch (target 30 Nov)
- [ ] T5 Share signup link in 3 places (1 h, needs T2)
- [ ] T6 Send issue #1 (0.5 h, needs T4, T5)

**First next action:** open both tools' pricing pages and note free-tier limits (20 min)
```

## Pitfalls and when to ask

- The goal is really several goals: plan them separately or ask which comes first.
- Tasks like "think about X" or "research Y" have no end; rewrite them with an output ("write a
  half-page comparison of X and Y").
- Do not invent deadlines or constraints the user did not give; label assumptions as assumptions.
- If the user already has a task tool (Todoist, Jira, a TASKS.md), offer the plan in a format that
  pastes into it.
- Keep plans to what fits on one screen where possible; offer detail for the first milestone only and
  plan later milestones when they get closer.

## Scope

For turning goals into plans. For choosing between options use a decision-making approach; for
managing an ongoing task list or calendar, use the user's task tool.
