# Bijdragen aan Prompt

## Een skill toevoegen

**Makkelijkste route:** klap in de Prompt-app je skill open (tab Mijn commands) en klik op **Deel op marktplaats**. GitHub opent met je SKILL.md ingevuld.

**Via de website:** ga naar **Publiceren**. Vul het formulier in of importeer een bestaande SKILL.md, en klik op **Open pull request op GitHub**. GitHub maakt zo nodig een fork; jij klikt op *Commit changes* en daarna op *Create pull request*.

**Handmatig:**

```
skills/
  jouw-skill/
    SKILL.md        verplicht
    skill.json      optioneel
    scripts/…       optioneel: hulpbestanden waar SKILL.md naar verwijst
```

`SKILL.md` begint met frontmatter:

```markdown
---
name: jouw-skill
description: "Wat hij doet. Gebruik wanneer de gebruiker … vraagt."
license: "MIT"
metadata:
  author: "jouw-github-naam"
  category: "code"
  tags: "git, commits"
  version: "1.0.0"
---

# Jouw skill

Instructies voor Claude…
```

Marktplaatsgegevens mogen onder `metadata:` staan of in `skill.json`. Staan ze op beide plekken, dan wint `skill.json`:

```json
{ "author": "jouw-github-naam", "category": "code", "tags": ["git", "commits"], "version": "1.0.0", "license": "MIT" }
```

Categorieën: `code`, `testing`, `design`, `automation`, `workflow`, `writing`, `data`, `other`.

### Regels die de check afdwingt

- `name`: kleine letters, cijfers en enkele streepjes, maximaal 64 tekens, gelijk aan de mapnaam.
- `description`: verplicht, maximaal 1024 tekens.
- Na de frontmatter staan instructies.
- Bestandsnamen bevatten alleen letters, cijfers, `.`, `_` en `-`. Geen verborgen bestanden.
- Toegestane types: `.md .txt .json .yaml .yml .csv .py .js .mjs .ts .sh .ps1 .html .css .svg`, maximaal 200 KB per bestand.

Draai `npm run check` lokaal om hetzelfde te zien als de review.

### Wat maakt een goede skill

- **De beschrijving bepaalt of Claude hem gebruikt.** Noem wat hij doet *en* wanneer, met de woorden die mensen echt typen.
- Schrijf zoals je een slimme collega zou briefen: het doel, de stappen, wanneer je moet stoppen of iets moet vragen.
- Eén skill, één taak.
- Test hem in Claude Code voordat je hem instuurt.

## Reviewen (maintainers)

1. Lees de hele SKILL.md en elk hulpbestand, niet alleen de diff-samenvatting.
2. Kijk naar de veiligheidsnotities in de workflow-log of op de previewsite.
3. Weiger skills die geheimen vragen, data naar derden sturen, rechtencontroles omzeilen of instructies verstoppen (base64, onzichtbare tekens, "negeer eerdere instructies").
4. Merge pas als de `validate`-check groen is.

## Code bijdragen

De site is plain HTML/CSS/JS zonder build-stap (`site/`). De gedeelde logica (parser, validatie, veiligheidsscan) staat in `site/js/skill-core.js` en wordt ook door de build gebruikt. De app staat in `app/prompt.pyw` (Python/tkinter, alleen standaardbibliotheek). Voeg voor nieuwe logica een test toe in `test/` (`npm test` en `npm run test:app`).
