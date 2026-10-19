# Prompt

Een Windows-programma dat alle slash-commands van Claude Code laat zien, met uitleg, plus een marktplaats met
skills van anderen. Klik op **Kopieer** en het command staat op je klembord. Klik op een regel om de uitleg uit
te klappen.

Geïnstalleerd in `%LOCALAPPDATA%\Programs\Prompt\` (het programma zelf is `bin\Prompt.exe`).

## Openen

- Snelkoppeling **Prompt** op het bureaublad
- Startmenu: Windows-toets, typ "Prompt"

Er draait altijd maar één venster. Open je het nog een keer, dan komt het bestaande venster naar voren.
Het programma blijft open tot je het zelf sluit en start nergens automatisch.

## Tab Mijn commands

- **Filter**: knoppen onder het zoekveld filteren op categorie. Zoeken zoekt ook in de uitleg.
- **Uitleg**: klik op een regel om die uit te klappen: wat het doet, wanneer gebruiken, en een voorbeeld
  dat je apart kunt kopiëren.
- **Mijn skills**: alles in `~\.claude\skills\<naam>\SKILL.md`. Uitgeklapt heb je ook **Kopieer als prompt**
  (de hele skill, klaar om in Claude Code te plakken) en **Deel op marktplaats**.
- **Mijn commands**: alles in `~\.claude\commands\*.md` (submappen worden `/map:naam`)
- **Project: ...**: skills en commands uit `.claude\` van je echte projectmappen
- **Plugins** en **Ingebouwd**: de vaste lijst in `builtin_commands.json`

De gescande mappen worden elke 2 seconden gecontroleerd. Maak je via Claude een nieuwe skill of command,
dan verschijnt die vanzelf in de lijst, zonder herstart.

## Tab Marktplaats

- Zoeken, filteren op categorie of op **Geïnstalleerd**.
- **Installeer**: zet de skill in `~\.claude\skills\<naam>\`. Start daarna een nieuwe Claude Code-sessie.
- **Bijwerken** verschijnt als de marktplaats een nieuwere versie heeft; **Verwijder** haalt hem weg.
- **Eigen versie**: je hebt zelf al een skill met die naam. **Vervang** vraagt eerst om bevestiging.
- **Kopieer prompt**: de volledige skill plus (optioneel) wat je invult bij *Je taak*. Plak het in Claude Code
  en Claude volgt de skill meteen, alleen in dat gesprek.
- **! notities**: de automatische veiligheidscheck vond iets om na te lezen. Klap de regel open en kies
  **Bekijk SKILL.md**. Prompt vraagt om bevestiging voordat zo'n skill wordt geïnstalleerd.
- Zonder internet zie je de laatst opgehaalde lijst (`market_cache.json`).

Welke marktplaats Prompt gebruikt staat in `registry.json` naast Prompt.exe:

```json
{ "url": "https://<eigenaar>.github.io/prompt/", "repo": "<eigenaar>/prompt", "branch": "main" }
```

`url` is waar de catalogus staat, `repo` is waar **Deel op marktplaats** een pull request voor opent.

## Installeren en aanpassen

- Installeren of bijwerken: dubbelklik op `install.cmd` in deze map. Daarvoor is Python 3 met tcl/tk nodig
  ([python.org](https://www.python.org/downloads/)). Het script zoekt Python zelf.
- Extra vaste commands (bijvoorbeeld nieuwe plugins): voeg ze toe in `builtin_commands.json` met
  `description`, `uitleg`, `wanneer` en `voorbeeld`; draai daarna `install.cmd`.
- Nederlandse uitleg voor je eigen skills en commands: zet ze in `uitleg.json` (sleutel is het command,
  bijvoorbeeld `/mijn-skill`; werkt ook voor plugin-varianten zoals `/anthropic-skills:mijn-skill`).
- Venstergrootte en positie worden onthouden in `state.json`, geïnstalleerde marktplaats-versies in
  `market_state.json`, beide naast Prompt.exe.
- Fouten (als die er ooit zijn) komen in `error.log` naast Prompt.exe.
- Het icoon (`icon.ico`) komt uit `make_icon.py`.

## Hoe Prompt.exe in elkaar zit

Windows Smart App Control blokkeert zelfgebouwde programma's zonder digitale handtekening. Daarom is
`Prompt.exe` een kopie van het ondertekende `pythonw.exe` van de Python Software Foundation, in de submap `bin`.
Het bestand `pyvenv.cfg` in de Prompt-map (gemaakt door `install.ps1`) maakt die map tot zijn eigen omgeving, en
`Lib\site-packages\sitecustomize.py` laadt bij het starten `prompt.pyw`. Voor jou is het gewoon een programma;
onder de motorkap draait het op je Python-installatie. Verwijder je die, dan werkt Prompt niet meer.
