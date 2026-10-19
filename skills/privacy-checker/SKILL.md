---
name: privacy-checker
description: >-
  Check how an app, website, spreadsheet or business process handles personal data against the basics
  of the GDPR (AVG in Dutch) - data inventory, purpose and lawful basis, minimisation, retention,
  consent, access rights, processors and security - and report practical gaps with concrete next steps.
  Use this skill whenever the user asks "is this GDPR compliant", "what personal data do we store",
  "do I need consent for this", "how long may I keep this data", "review our privacy", or says "voldoen
  we aan de AVG", "welke persoonsgegevens verwerken we" or "mag ik deze gegevens bewaren".
license: "MIT"
metadata:
  author: "prompt"
  category: "security"
  tags: "privacy, gdpr, avg, persoonsgegevens, data protection, bewaartermijn, consent, toestemming"
  version: "1.0.0"
  summary_nl: "Toetst hoe je app of proces met persoonsgegevens omgaat aan de AVG-basis en geeft praktische verbeterpunten."
---

# Privacy checker

Most privacy problems are not exotic: data collected "just in case", kept forever, shared with a tool
nobody listed, or used for a purpose users were never told about. This skill builds a clear picture of
what personal data flows where and checks it against the core GDPR principles, so the user gets a short
list of fixes they can actually make.

## Workflow

### 1. Build the data inventory

Gather it from the code (database schemas, models, forms, analytics calls, logs), configuration and
the user's own description. For each data item record:

| Field | Example |
|---|---|
| Data | email address, IP address, date of birth, health notes |
| Whose | customers, employees, newsletter subscribers, children |
| Where stored | `users` table, Mailchimp, Excel on a shared drive, server logs |
| Shared with | payment provider, hosting, analytics, accountant |
| Special category? | health, religion, ethnicity, biometrics, criminal records |

Search code for clues: `grep -rniE 'email|phone|birth|address|iban|bsn|ssn|gender' src/`, tracking
scripts in HTML templates, and what request logs capture. Ask the user about offline copies and
processes the code does not reveal.

### 2. Check each principle

- **Purpose and lawful basis**: for each data group, one specific purpose and a basis (contract,
  consent, legal obligation, legitimate interest). Using data for a new purpose needs a fresh check.
- **Minimisation**: is every field needed for that purpose? Date of birth when an "over 18" checkbox
  would do is a typical gap.
- **Retention**: a concrete period per data group and a mechanism that deletes or anonymises it. A
  policy without a cleanup job is a gap.
- **Consent** (when consent is the basis): freely given, specific, opt-in, as easy to withdraw as to
  give, and logged. Non-essential cookies and analytics need it before they load.
- **Transparency**: the privacy notice matches what actually happens.
- **Data subject rights**: can the user find, export, correct and delete one person's data within a
  month?
- **Processors**: a data processing agreement with each vendor; note transfers outside the EU.
- **Security**: access limited to who needs it, encryption in transit, backups, a breach procedure
  (72-hour notification to the authority when risk exists).
- **Special categories and children**: extra conditions; flag for expert review.

### 3. Prioritise the gaps

Rank by risk to the people involved and effort to fix: special-category data or large-scale tracking
without a basis comes first, a missing line in the privacy notice later. Point to quick wins.

## Output format

```text
Privacy check - webshop "Bloemenhoek" (Django app + Mailchimp + Google Analytics)

Data inventory: 9 data items, 4 systems, 3 processors (table attached)

Gaps (highest first)
1. Analytics loads before consent - cookie banner only informs. Fix: block GA until opt-in
   (template base.html line 22), or switch to a cookieless analytics setup.
2. Orders kept indefinitely. Fix: define 7 years for invoices (tax law), anonymise customer
   details on older orders with a monthly management command.
3. No way to delete one customer's data. Fix: admin action that removes the account, Mailchimp
   contact and order personal fields.
4. Date of birth collected but unused. Fix: remove the field and drop the column after a backup.

Fine as is: HTTPS everywhere, admin access limited to 2 staff accounts, DPA with hosting provider.
Needs a specialist: none / health data in the contact form (if confirmed).
```

## Pitfalls and when to stop

- This is a practical check, not legal advice. Say so once, clearly, and recommend a privacy
  professional or the organisation's data protection officer for high-risk processing, special
  categories, large-scale monitoring or a DPIA.
- Do not guess what a vendor does with data; check their documentation or mark it unknown.
- When inspecting real records, look at structure and counts rather than copying personal data into
  the conversation or reports.
- Local rules add details (for example, the Dutch BSN may only be processed when a law allows it);
  mention them when relevant rather than covering every member state.

## Scope

Covers GDPR basics for the user's own app or process. Technical vulnerabilities are the domain of
security-review-lite, and leaked credentials of secrets-scanner. Drafting a full privacy policy or
contracts is outside this skill, though the inventory is a good starting point for one.
