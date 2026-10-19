---
name: explain-like-im-new
description: >-
  Explain a concept, term or technology simply for someone who is new to it, using an everyday
  analogy, plain words, a tiny concrete example, then one level deeper, and finishing with a quick
  question to check understanding. Use this skill whenever the user asks "what is", "explain",
  "ELI5", "explain like I'm five", "I don't get", "in simple terms", "leg dit simpel uit", "wat
  betekent", "ik snap het niet" or "uitleg voor beginners", about tech, science, finance, law or any
  topic, or when they seem confused by jargon in an earlier answer.
license: "MIT"
metadata:
  author: "prompt"
  category: "learning"
  tags: "explain, eli5, beginner, uitleg, simpel, analogie, leren, concept"
  version: "1.0.0"
  summary_nl: "Legt een onderwerp simpel uit met een vergelijking, gewone woorden, een klein voorbeeld en een korte check."
---

# Explain like I'm new

Beginners do not lack intelligence, they lack anchors: familiar things to hang a new idea on. A good
explanation gives one solid anchor, shows the idea working once, and only then adds detail. This skill
follows that order and checks whether it landed instead of assuming it did.

## Workflow

1. **Find the starting point.** If unclear, ask one quick question: "What do you already know about
   X?" or "Where did you run into it?" Someone reading a news article needs a different answer from
   someone debugging code. If the context makes it obvious, skip the question.
2. **One-sentence core.** Say what it is and what it is for, in words a 12-year-old knows. No jargon;
   if a technical term is unavoidable, define it in the same sentence.
3. **Analogy.** Pick one everyday comparison and say where it stops working. Naming the limit
   prevents the analogy from teaching something false.
4. **Tiny example.** Show the idea working once with real, small numbers or a concrete scene.
5. **One level deeper.** Add the next most important detail, the one that makes the beginner
   explanation more accurate. Introduce the proper term here so they can search for it later.
6. **Check understanding.** Ask one short question that requires applying the idea, not repeating
   it. Wait for the answer, then correct gently or go deeper.

Keep the whole answer short (roughly 150-250 words before the check). Beginners get lost in walls of
text, and they can always ask for more.

## Output template

```markdown
**In one sentence:** <plain explanation>

**Think of it like:** <analogy>. (Where it breaks: <limit>.)

**Tiny example:** <concrete scene or numbers>

**One step deeper:** <next detail + proper term>

**Quick check:** <application question>
```

## Example

User: "What is an API?"

```markdown
**In one sentence:** An API is a fixed way for one program to ask another program for something
and get an answer back.

**Think of it like:** a restaurant menu. You do not walk into the kitchen; you order from the menu,
and the kitchen sends back your dish. (Where it breaks: a program can order thousands of times per
second, and there is no waiter improvising.)

**Tiny example:** A weather app on your phone does not measure the weather. It sends a request like
"weather for Utrecht" to a weather service's API and gets back "14 degrees, light rain", which it
then shows you.

**One step deeper:** Most web APIs work over the same technology as websites (HTTP). The program
visits a special address, called an endpoint, and gets data back as JSON, a text format that is
easy for programs to read.

**Quick check:** When you pay with a webshop's "Pay with iDEAL" button, which two programs do you
think are talking through an API?
```

## Adjusting on the fly

- If the answer to the check is right, offer the next level or a related concept.
- If it is partly right, name what is correct first, then fix the gap with a second, different
  analogy; repeating the same one rarely helps.
- If the user says "even simpler", shorten sentences and drop the deeper section.
- If they are clearly more advanced than assumed, skip the analogy and go to the precise version.
- Match the user's language; answer in Dutch when they ask in Dutch.

## Pitfalls

- Analogies that are cute but wrong do damage; accuracy beats charm.
- Do not stack three analogies at once; one good one is clearer.
- Avoid "simply" and "just": if it were simple for them, they would not ask.
- If you are unsure about a fact, say so rather than smoothing it over.

## Scope

For first explanations of a single concept. For structured study of a whole chapter, or for learning
to program step by step, a study or tutoring workflow fits better.
