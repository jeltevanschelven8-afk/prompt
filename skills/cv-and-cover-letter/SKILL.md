---
name: cv-and-cover-letter
description: >-
  Improve a CV and write a tailored cover letter (sollicitatiebrief or motivatiebrief) for a specific
  vacancy. Rewrites duties into concrete achievements, matches keywords from the job ad so applicant
  tracking systems (ATS) pick it up, keeps everything honest, and follows Dutch or international
  conventions. Use this skill whenever the user shares a CV or resume, a job posting, or asks to
  "improve my CV", "write a cover letter", "tailor my resume", or types "verbeter mijn cv", "schrijf
  een sollicitatiebrief", "help me solliciteren" or "motivatiebrief voor deze vacature".
license: "MIT"
metadata:
  author: "prompt"
  category: "writing"
  tags: "cv, resume, cover letter, sollicitatiebrief, solliciteren, vacature, ats, carriere"
  version: "1.0.0"
  summary_nl: "Verbetert je cv en schrijft een sollicitatiebrief op maat voor een specifieke vacature, eerlijk en ATS-vriendelijk."
---

# CV and cover letter

A recruiter skims a CV in under a minute and often only after software has filtered it. So a strong CV
does two things: it contains the words the vacancy uses, and it shows results rather than job
descriptions. The cover letter then answers the question the CV cannot: why this person, for this role,
at this organisation. All of it has to be true, because interviews test every line.

## Workflow

1. **Collect the inputs.** The current CV (file or text), the vacancy text, and anything the user wants
   to emphasise or downplay. If there is no vacancy yet, improve the CV in general and skip the letter.
2. **Analyse the vacancy.** Extract must-haves, nice-to-haves, key terms (tools, certificates, skills),
   and the tone of the organisation. Make a short match table: requirement → evidence in the CV → gap.
3. **Rewrite experience as achievements.** Pattern: action verb + what + measurable result or scope.
   "Responsible for customer service" becomes "Handled 40+ customer requests a day and cut average
   response time from 2 days to 6 hours". Only use numbers the user gives you; otherwise ask, or write a
   placeholder like `[aantal]`.
4. **Tailor, do not fabricate.** Reorder bullets so the most relevant come first, mirror the vacancy's
   terms where the user genuinely has the skill, and add a 2-3 line profile at the top aimed at this role.
5. **Make it ATS-friendly.** Single column, standard headings (Werkervaring / Experience, Opleiding /
   Education, Vaardigheden / Skills), no text in images or tables for key information, dates in one
   consistent format, file as .docx or text-based PDF.
6. **Write the cover letter** using the structure below. Under one page, about 250-400 words.
7. **Hand back** the improved CV as a new file or text (keep the original untouched), the letter, and the
   list of open questions and gaps.

## Cover letter structure

1. **Opening**: the role, and one specific reason this organisation appeals. Skip "Hierbij solliciteer
   ik naar de functie van"; it wastes the most-read sentence.
2. **Why you fit**: two or three short paragraphs, each linking a vacancy requirement to a concrete
   example from the CV.
3. **Why them**: something real about the organisation (a product, project, value, recent news the user
   confirms).
4. **Close**: availability and an invitation to talk. "Met vriendelijke groet" plus name.

Example opening (Dutch):

> Toen ik las dat jullie het planningssysteem van 12 vestigingen gaan samenvoegen, dacht ik meteen aan
> het project waarmee ik bij Van Dijk Logistiek drie roosters terugbracht tot één.

## Conventions

- **Netherlands / Belgium**: photo optional (often left out), date of birth and marital status not
  needed, 1-2 pages, *u* or *je* following the tone of the vacancy. A short "Persoonlijk profiel" is
  common.
- **UK / US**: no photo, no date of birth, "Resume" in the US is often one page.
- Spell-check names of the company and contact person twice; it is the most common avoidable mistake.

## Output format

```
Match analysis
| Requirement (vacancy) | Evidence in CV | Status |
| 3+ jaar ervaring met SQL | Data-analist bij X, 2021-heden | ok |
| Power BI | not mentioned | ask: do you use it? |

Improved CV        -> cv_[naam]_[bedrijf].docx (original kept)
Cover letter       -> sollicitatiebrief_[bedrijf].docx
Open questions     -> 3 items (numbers for achievements, Power BI, start date)
```

## Pitfalls and when to ask

- Never add skills, degrees, titles or results the user did not confirm. Gaps are better addressed
  honestly (a course in progress, transferable experience) than hidden.
- Ask about gaps in employment only if the user wants them addressed; do not pry.
- If the user wants one generic letter for many vacancies, explain that tailored letters perform better
  and offer a template with clearly marked parts to adjust.
- Personal data in the CV stays in the files you write; do not repeat it unnecessarily in chat.

## Scope

For CVs, resumes, cover letters and LinkedIn "About" sections tied to applications. It does not give
salary negotiation or legal employment advice, and it does not apply to jobs on the user's behalf.
