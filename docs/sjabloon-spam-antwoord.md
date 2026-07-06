# Thunderbird-sjabloon: "aanbodmail niet ontvangen / in spam"

Standaardantwoord voor klanten die de wekelijkse aanbodmail niet zagen
(vrijwel altijd: in de map Ongewenste e-mail beland). Achtergrond: onze
verzendkant (SPF/DKIM/schoon EmailLabs-IP) staat goed — het enige wat de
klant zelf kan doen zijn de drie stappen hieronder.

## Eenmalig instellen in Thunderbird

1. Nieuw bericht (vanuit info@kiemkracht.be).
2. Plak de tekst hieronder (je handtekening staat er automatisch al onder).
3. Menu **Bestand → Opslaan als → Sjabloon**.
4. Gebruik later: map **Sjablonen** → dubbelklik het sjabloon → naam
   invullen achter "Dag" → versturen.

## Sjabloontekst

---

Dag

De wekelijkse aanbodmail is gewoon vertrokken — die versturen we elke
maandagochtend. Waarschijnlijk is hij in je map **Ongewenste e-mail /
Spam** beland. Met deze drie stapjes komt hij voortaan in je Postvak IN:

1. Kijk in je map **Ongewenste e-mail** en open de mail van Kiemkracht
   (afzender info@kiemkracht.be).
2. Markeer hem als **"Geen ongewenste e-mail"** (of versleep hem naar je
   Postvak IN).
3. Voeg **info@kiemkracht.be toe aan je contacten** — dat is het sterkste
   signaal voor de spamfilter. Lees je je mail in een app én via webmail,
   doe het dan op beide plaatsen.

Dat je me nu schrijft, helpt trouwens ook al: de filter leert daarvan dat
onze mails gewenst zijn.

Vind je de mail nergens terug, laat het me even weten — dan kijk ik het na.

Groeten,

---

## Varianten per mailprogramma (indien de klant doorvraagt)

Geverifieerd 2026-07-06 (menunamen verschillen per provider!):

- **Outlook-app (telefoon):** open de mail → menu ⋮ → "Melden" →
  "Geen ongewenste e-mail".
- **Hotmail/Outlook.com/Live (webmail):** Instellingen → E-mail →
  Ongewenste e-mail → **"Veilige afzenders en domeinen"** → adres
  toevoegen.
- **Telenet Webmail:** Instellingen → **"Vertrouwde adressen"** → adres
  (of @kiemkracht.be) toevoegen. Mails van die lijst belanden nooit in
  de spammap.
- **Gmail (app of web):** GEEN veilige-afzenderslijst — open de mail in
  Spam → "Geen spam", daarna afzender toevoegen aan Contacten.
  (Power-users: filter aanmaken met "Nooit naar spam sturen".)
- **Proximus/Skynet/Scarlet Webmail:** menu rechtsboven → E-mail →
  **"Veilige afzenders"** → adres toevoegen.
- **Yahoo / iCloud:** geen lijst; "geen spam" markeren + contact
  toevoegen.

## Eenmalige "reddingsmail" (verzonden vanaf klaas.ysebaert@gmail.com)

Bulk-aankondiging na de kanaal-switch (week 28, 2026-07): vanaf het oude
vertrouwde Gmail-adres, omdat dat wél inbox-historie heeft bij de klanten.
Doelgroep: het Mailmerge-tabblad van de week (= wie de aanbodmail kreeg).

**Onderwerp:** krijg je de mails van info@kiemkracht.be?

**Tekst (definitieve versie Klaas, 2026-07-06):**

Dag {{Voornaam}}

Sinds vorige week gebruiken we het nieuwe mailadres info@kiemkracht.be om
het aanbod van de week te versturen op maandagvoormiddag.

Een delicate switch, niet zonder reden: mijn persoonlijke mailadres botst
op de limiet van de mogelijkheden voor professioneel gebruik.

Een overgang naar Google Workspace was voor de hand liggend, maar ik
verkoos een pad weg van Amerikaanse techgiganten die de hielen likken van
de president die het spel niet eerlijk speelt (hah!).

EmailLabs biedt een kwalitatief alternatief en gebruikt eigen Europese
infrastructuur. Op termijn zou de kwaliteit van de aflevering van de
mails uitstekend moeten zijn, maar de eerste weken kunnen mijn mails
onbedoeld botsen op spamfilters.

Verwacht je een mail, maar zie je die niet, dan is de mail waarschijnlijk
in je map Ongewenste e-mail / Spam beland.

Ik kan volgende tips geven om de mails voortaan in je Postvak IN te laten
terechtkomen:

1. Kijk in je map "Ongewenste e-mail" of "Spam" en open de mail van
   Kiemkracht (afzender info@kiemkracht.be).
2. Markeer hem als "Geen ongewenste e-mail/Geen spam" (of versleep hem
   naar je Postvak IN).
3. Voeg "info@kiemkracht.be" toe aan je contacten — dat is het sterkste
   signaal voor de spamfilter. Lees je je mail in een app én via webmail,
   doe het dan op beide plaatsen. Veel providers hebben in hun
   webmail-instellingen ook een lijst "veilige afzenders" of "vertrouwde
   adressen" — ook daar toevoegen helpt.

Eventueel kan je antwoorden op de mail die je bij spam vond: antwoorden
aan info@kiemkracht.be helpt om de mail in de toekomst beter te ontvangen
en kan ons helpen om te zien bij welke providers we problemen
ondervinden.

Vriendelijke groet,

Klaas

**Verzend-nota's:** via smtp.gmail.com (Gmail-identiteit, NIET de
EmailLabs-relay — anders lijkt het gespooft en beland je zelf in spam);
Gmail-limiet ±500/dag dus 366 past, maar met pauze tussen de mails.

## Nota voor onszelf

- Verzendcontrole: in `mailmerge_recipients` nakijken of de klant in de
  run zat (`status='verzonden'` + tijdstip) vóór je spam-advies geeft —
  misschien stond die gewoon niet in de lijst.
- Komt dit opvallend vaak terug bij één ISP (bv. telenet.be), meld het
  dan: dat is een patroon voor de EmailLabs-kant, geen klantprobleem.
