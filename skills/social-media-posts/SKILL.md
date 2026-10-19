---
name: social-media-posts
description: >-
  Write social media posts for LinkedIn, Instagram, X, Facebook, Threads or Bluesky with a strong hook,
  platform-appropriate length and tone, a clear call to action and a few relevant hashtags, delivered as
  two or three variants to choose from. Use this skill whenever the user wants a post, caption, tweet,
  thread or announcement, asks to "turn this into a LinkedIn post" or "write a caption", or types
  "schrijf een LinkedIn-post", "maak een caption voor Instagram" or "maak hier een post van", even when
  they only paste an article, news item or photo description and mention a platform.
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "social media, linkedin, instagram, copywriting, captions, posts, berichten, hashtags"
  version: "1.0.0"
  summary_nl: "Schrijft posts voor LinkedIn, Instagram, X en meer met een sterke openingszin, passende lengte en een paar varianten."
---

# Social media posts

On every platform the first line decides whether anyone reads the rest. After that, each platform has its
own habits: LinkedIn rewards a short personal story with a takeaway, Instagram is visual-first with the
caption in support, X rewards one sharp idea. Writing one text and pasting it everywhere wastes the
content. This skill writes for the platform.

## Workflow

1. **Get the essentials.** Platform(s), the one message, the audience, the goal (clicks, comments,
   applications, awareness), language (Dutch or English), and whether it is a personal or company
   account. If the user gave a source text, pull the single most interesting point from it.
2. **Write the hook first.** Options that work: a concrete number, a surprising contrast, a short
   confession, a direct question, or the outcome before the story. Avoid clickbait the post does not pay
   off, because it costs trust.
3. **Shape the body for the platform** (table below). Short paragraphs, one idea each. On mobile, a block
   of eight lines looks like a wall.
4. **End with one call to action.** Ask a real question, point to the link, or invite a DM. One, not three.
5. **Add hashtags sparingly**, specific over generic: `#dataengineering` reaches more of the right people
   than `#success`.
6. **Deliver variants** that differ in angle, not just wording (story vs list vs bold opinion).

## Platform guide

| Platform | Length | Tone | Hashtags | Notes |
|---|---|---|---|---|
| LinkedIn | 600-1,300 characters | professional but human, first person | 3-5 at the end | First ~210 characters show before "...more". Links in the post reduce reach for some accounts; offer "link in first comment". |
| Instagram | 125-300 characters for the visible part, more allowed | warm, visual, emoji fine | 3-10 relevant | Caption supports the image; suggest alt text for the image. |
| X | under 280 characters per post | sharp, one idea | 0-2 | For more, write a numbered thread with a strong first post. |
| Facebook | 40-250 characters works best | conversational | 0-2 | Questions drive comments. |
| Threads / Bluesky | under 500 / 300 characters | casual, conversational | 0-2 | Hashtags matter less here. |

These are habits, not hard limits. If the user's audience behaves differently, follow their experience.

## Output format

```
LinkedIn - variant A (story)
[post text]
Hashtags: #hr #recruitment #werkenbij
~780 characters

LinkedIn - variant B (list)
...

Tip: post on a weekday morning; reply to comments in the first hour.
```

Small example (LinkedIn, Dutch, hook plus opening):

> Vorig jaar kregen we 4 sollicitaties op een vacature. Dit jaar 61.
>
> We hebben niks aan het salaris veranderd. Wel aan de vacaturetekst.

## Pitfalls

- **Inventing facts.** Do not make up numbers, quotes, client names or results to make a post punchier.
  Use placeholders like `[aantal]` and ask the user to fill them in.
- **Engagement bait** ("Comment YES if you agree") reads cheap and some platforms downrank it.
- **Emoji walls and hashtag stuffing** make posts look automated.
- **Tagging people or companies**: suggest it, but let the user decide; they know the relationship.
- Sensitive topics (layoffs, incidents, politics): write carefully and recommend a second pair of eyes.

## When to stop and ask

If the platform, language or goal is unclear and changes the post substantially, ask one quick question.
Otherwise make a sensible choice, state it, and offer the alternative.

## Scope

This skill writes the post text. It does not schedule or publish posts, and it does not create the
images (it can suggest what the visual should show).
