---
name: blog-post-writer
description: >-
  Write a blog post or article that people finish reading, by finding a specific angle, building an outline,
  opening with a strong intro, and writing scannable sections with concrete examples, then offering several
  title options and a short meta description. Works from a topic, rough notes, or an existing draft, in Dutch
  or English. Use this skill whenever the user asks to "write a blog post", "turn this into an article",
  "improve my draft", or "give me title ideas", or says "schrijf een blog", "maak een artikel over", or
  "herschrijf mijn blogpost".
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "blog, article, content writing, outline, headlines, blogpost, artikel, schrijven"
  version: "1.0.0"
  summary_nl: "Schrijft een blog of artikel met een scherpe invalshoek, sterke intro, overzichtelijke kopjes, concrete voorbeelden en titelopties."
---

# Blog post writer

Generic posts on broad topics ("10 tips for productivity") disappear in a sea of identical content.
Posts that get read take a specific angle, deliver on the promise of the title quickly, and show rather
than tell with examples. This skill gets the angle right before writing a single paragraph.

## Workflow

1. **Clarify reader, goal, and material.** Who is the reader and what do they already know? What should
   they think or do afterwards? Does the user have notes, experiences, data, or opinions to draw on?
   First-hand material is what makes a post worth reading, so ask for it.
2. **Find the angle.** Turn the topic into a specific claim or promise. Topic: "remote work". Angles:
   "Why our 6-person team stopped doing daily stand-ups", "The 3 rules that made async work for us".
   Offer two or three angles and let the user choose; this decision shapes everything after it.
3. **Outline.** A working title, the hook, 3 to 6 section headings that each make a point (not just a
   label), and the takeaway. Share the outline for longer posts before drafting; restructuring an outline
   costs a minute, restructuring a draft costs an hour.
4. **Write the intro.** In the first three sentences, show the reader their problem or a surprising fact,
   and promise what they will get. Skip background history and definitions unless the reader needs them.
5. **Write scannable sections.** Headings that carry meaning, short paragraphs (2-4 sentences), lists for
   steps or options, bold for the one phrase per section that matters. Each section gets at least one
   concrete example, number, quote, or mini-story.
6. **End with something useful.** A summary of the key point, a next step, or a question. Avoid "In
   conclusion" followed by repetition.
7. **Edit.** Cut filler words and hedges, swap abstract nouns for verbs, vary sentence length, and read
   the headings alone to check they tell the story.
8. **Add title options and meta.** Give 5 titles in different styles (benefit, how-to, number, contrarian,
   question) and a meta description under 155 characters.

## Example outline

```markdown
Working title: Why we stopped doing daily stand-ups (and what replaced them)
Reader: team leads of small software teams. Goal: try a written check-in for two weeks.

Hook: our stand-up took 15 minutes x 6 people = 7.5 hours a week, mostly status nobody used.
1. The stand-up had turned into a reporting ritual
2. What we tried instead: a 3-question written check-in at 10:00
3. What got better (and what got worse: fewer spontaneous chats)
4. How to run a two-week experiment in your own team
Takeaway: keep the sync meeting for problems, move status to writing.
```

## What the user receives

1. The title options and the chosen working title.
2. The full post in Markdown, with headings and suggested places for images or screenshots.
3. A meta description and 3 to 5 tags.
4. A short note listing anything that needs the user's input, such as "[add your own number here]" or a
   claim that should be backed by a source.

## Pitfalls and when to ask

- Do not invent statistics, quotes, studies, or personal anecdotes and present them as real. Use
  placeholders or clearly framed hypothetical examples, and say which is which.
- Match the user's voice. If they share earlier posts, mirror sentence length, humour, and formality;
  ask for a sample when the voice matters.
- SEO helps, but keyword stuffing hurts readability. Use the main phrase naturally in the title, intro,
  and one heading, and stop there.
- If the topic needs expertise the user has and you lack (medical, legal, financial), write from their
  input and flag statements that need an expert check.
- For rewrites, preserve the author's main points and say what you changed and why.

## Scope

This skill writes long-form posts and articles. Short social posts, emails, landing page copy, and
technical documentation have different structures and are better served by their own workflows.
