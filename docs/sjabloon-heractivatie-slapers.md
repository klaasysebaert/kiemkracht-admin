# Sjabloon: "krijg je de weekmail nog graag?"

Opgesteld 2026-09-27, naar aanleiding van de verzendscan. Dit is een
**eenmalige** re-permissiemail aan ontvangers die de wekelijkse aanbodmail
al maanden krijgen zonder ooit te bestellen.

## Waarom deze mail bestaat

45 week-per-weekklanten krijgen sinds april 2026 elke week de aanbodmail en
hebben in die hele periode geen enkele bestelling, vooruitbestelling of
annulatie geplaatst — geen enkel spoor van activiteit. Voor Gmail is een lijst
met zo'n aandeel nooit-reagerende ontvangers het schoolvoorbeeld van
ongewenste bulk, en die beoordeling treft **de hele lijst**, ook de trouwe
klanten. Zie `reference_mailmerge_blindheid` en `gmail-promoties-uitval`.

## Hoe versturen — niet via de runner

Via **Thunderbird**, niet via admin-mailmerge. De runner-mails belanden bij
Gmail in de Reclame-tab; precies daarom heeft deze groep ze waarschijnlijk
nooit gezien, en een re-permissiemail die óók in Reclame belandt bewijst niets.
Het afrekening-kanaal (Thunderbird, `info@kiemkracht.be`, kleine oplage) komt
wél in Primair aan — dat is het kanaal dat je hier nodig hebt.

`Module4` heeft de machinerie al: `BereidHeractivatieMailmergeVoor` bouwt een
Thunderbird-sheet met een gepersonaliseerde bestellink en uitschrijflink per
klant. Enkel de selectie op regel 79 (`WHERE k.status = 'on_hold'`) moet de
slaper-selectie worden. Merge-velden: `{{Voornaam}}`, `{{GroentenURL}}`,
`{{UitschrijfURL}}`.

## De tekst

**Onderwerp:** Krijg je onze weekmail nog graag?

```
Dag {{Voornaam}}

Elke maandag sturen we een mail met de groenten van die week. Jij krijgt
die mail al een hele tijd, maar we zien je niet terug bij de bestellingen —
en dat is prima, daar is niets mis mee. Alleen weten we niet of je hem nog
graag krijgt, of dat hij elke week ongelezen bij je binnenvalt.

Dus de eerlijke vraag: wil je hem blijven krijgen?

- Ja, graag → je hoeft niets te doen als je deze week bestelt:
  {{GroentenURL}}
  Of antwoord gewoon even op deze mail met "ja".

- Liever niet meer → {{UitschrijfURL}}
  Je blijft gewoon klant, alleen de wekelijkse mail stopt. Je kan altijd
  opnieuw beginnen, gewoon door ons een seintje te geven.

Hoor ik tegen [DATUM] niets, dan zet ik de wekelijkse mail voor jou stil.
Niet uit onvriendelijkheid — een mail die niemand wil, doet meer kwaad dan
goed, ook voor de klanten die hem wél verwachten.

Met vriendelijke groet
Klaas
Kiemkracht bioboerderij
```

## Varianten

**De 3 recente klanten (juni–juli)** krijgen een andere toon — zij hebben pas
10 tot 13 mails gehad en verdienen geen "of het stopt". Vervang het middenstuk
door een open vraag:

```
Je bent sinds kort klant, maar we zagen je nog niet bij de bestellingen.
Loopt er iets stroef, of is het gewoon nog niet gelukt? Laat het me weten —
ook als iets niet werkt aan het bestelformulier hoor ik dat graag.
```

Geen deadline, geen uitschrijfdreiging.

## Wie er NIET in hoort

| Wie | Waarom |
|---|---|
| Sofie Casier, Ruth Selleslaghs, Bart Deberlanger, Helena Verfaillie | klant sinds september — hebben één tot drie mails gehad, die hebben gewoon tijd nodig |
| Klaas Ysebaert (3342) | jijzelf |
| Maggie Dendoncker (3264) | bestelde wél koffie — zij is actief, alleen niet voor groenten. Aanspreken kan, maar niet met deze tekst |
| Ann Hoste (3180) | schreef zich in juli uit; de opt-out staat sinds week 31 weer op `false` en ze krijgt opnieuw elke week post. Uitzoeken vóór je haar aanschrijft — dit is een mail waar een spamklacht uit komt |

Volledige lijst met groepsindeling: `c:\tmp\slapende-ontvangers-2026-09-27.csv`

## Nadien

Wie niet reageert: `mail_opt_out = true` met
`mail_opt_out_reden = 'Geen reactie op heractivatiemail 2026-09'` en
`mail_opt_out_methode = 'heractivatie'`. Klant blijft `actief` — enkel de
wekelijkse mail stopt.

⚠ Reken erop dat het merendeel niet antwoordt. Dat is niet het mislukken van
de actie, dat is de uitkomst: een lijst van ~330 die de mail wél wil, levert
betere aflevering op dan een lijst van 378 waarvan 45 nooit kijken.
