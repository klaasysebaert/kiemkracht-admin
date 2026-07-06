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

- **Outlook-app (telefoon):** open de mail → menu ⋮ → "Melden" →
  "Geen ongewenste e-mail".
- **Telenet Webmail:** instellingen → ongewenste e-mail → afzender
  toevoegen aan veilige afzenders.
- **Gmail (app of web):** open de mail in Spam → "Geen spam". Daarna
  afzender toevoegen aan Contacten.
- **Proximus/Skynet Webmail:** mail in spammap openen → "Geen spam" /
  afzender whitelisten in de instellingen.

## Nota voor onszelf

- Verzendcontrole: in `mailmerge_recipients` nakijken of de klant in de
  run zat (`status='verzonden'` + tijdstip) vóór je spam-advies geeft —
  misschien stond die gewoon niet in de lijst.
- Komt dit opvallend vaak terug bij één ISP (bv. telenet.be), meld het
  dan: dat is een patroon voor de EmailLabs-kant, geen klantprobleem.
