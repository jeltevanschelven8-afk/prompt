# Veiligheid

Skills zijn instructies die Claude opvolgt. Een kwaadaardige skill kan Claude proberen over te halen om bestanden te verwijderen, geheimen uit te lezen of data te versturen. Prompt beperkt dat risico op vier manieren:

1. **Review.** Een skill komt alleen online via een pull request die een maintainer heeft goedgekeurd.
2. **Automatische scan.** `site/js/skill-core.js` zoekt naar riskante patronen: script downloaden en uitvoeren, `iex`, recursief verwijderen, permissiechecks overslaan, wachtwoorden en tokens, "negeer eerdere instructies", base64-inhoud en exfiltratiediensten. Hij somt ook alle genoemde websites op. Treffers zijn **notities, geen oordeel**. Ze staan op de site en in de Prompt-app, en Prompt vraagt om bevestiging voordat zo'n skill wordt geïnstalleerd.
3. **Veilig installeren.** Prompt accepteert alleen geldige skillnamen en bestandspaden, downloadt eerst alles en zet de map pas daarna op zijn plek, en overschrijft nooit zonder vragen een eigen skill met dezelfde naam.
4. **Strikte bestanden.** Alleen tekstbestanden met veilige namen en een beperkte grootte. Bestandsnamen komen in installatiecommando's terecht, en daarom zijn vreemde tekens geweigerd.

Wat de scan **niet** doet: de bedoeling van een tekst begrijpen. Lees een skill dus altijd voordat je hem installeert. Claude Code blijft daarnaast om toestemming vragen voor acties.

## Een probleem melden

- **Een skill die onveilig of kwaadaardig lijkt:** open een issue met het sjabloon *Probleem met een skill* en kies "Onveilig of kwaadaardig".
- **Een kwetsbaarheid in de site of de app:** gebruik **Security → Report a vulnerability** op GitHub (private melding), niet een openbaar issue.
