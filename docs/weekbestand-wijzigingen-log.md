# Log — last-minute wijzigingen in het weekbestand

Doel: vóór we van de DB de enige bron van waarheid maken, elke last-minute
wijziging die je in het weekbestand doet, hier noteren. Zo krijgen we de
**volledige lijst van soorten wijzigingen** in beeld (elke nieuwe soort kan een
ontbrekende plek in de DB betekenen). Zie het geheugen `weekbestand-db-bron`.

Noteer **op het moment zelf** (de bedoeling vervaagt snel) en **intentie-eerst**:
niet "rij gewist" maar wát de klant/situatie wou — dat bepaalt welk DB-feit het is.

Per wijziging één regel:
- **Wie** — klant + `klant_id` (staat in kolom P van het weekbestand)
- **Wat de klant/situatie wou** — de bedoeling ("op verlof", "wil geen tomaten", "haalt deze week elders af")
- **Wat je concreet deed** — welke cel(len) in het weekbestand

---

## Week 29 / 2026

*(genoteerd op 2026-07-28, bij het afwerken van `week_29_2026_definitief.ods`)*

Gebeurtenis: een **cadeaubon** moest op de afrekening verrekend worden. Daar
bestaat geen aparte plek voor, dus is hij als **fictieve "groente"-kolom met een
negatieve prijs** ingevoerd — het weekbestand rekent hem dan gewoon mee als
(negatieve) besteling.

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 1 | — (aanbod, niet klantgebonden) | Cadeaubon kunnen verrekenen op de afrekening | Twee extra "groente"-kolommen achteraan bijgemaakt: **AO = "Cadeaubon"** en **AP = "Cadeaubon Extra Groot"**, beide met prijs **−25,00 €** in rij 3 |
| 2 | 3148 Veerle Colpaert (rij 117) | Haar cadeaubon van 25 € verzilveren | **AP117 = 1** (levering vrijdag) → −25,00 € op haar afrekening |

Kolom AO bleef deze week op 0 (aangemaakt maar niet gebruikt).

**DB-implicatie:** dit is géén groente maar een **korting-/tegoedregel op de
afrekening**. In een DB-wereld kan dit niet als product-in-het-aanbod
binnensluipen: er is een aparte notie nodig (bv. een regel op de afrekening met
type `cadeaubon`, bedrag en datum, gekoppeld aan `klant_id`) — anders duikt de
bon op in oogstlijsten, afweeglijsten, etiketten en pakketwaardes. Precies de
flexibiliteit die de spreadsheet gratis geeft en die de DB expliciet moet
inbouwen.

---

## Week 30 / 2026

Gebeurtenis: Meloen Charentais (onder voorbehoud) was maandag als losse groente
aangeboden, maar bleek donderdag/vrijdag nog niet rijp/oogstbaar. Drie handelingen:

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 1 | 2860 (regel 8) | Meloen niet oogstbaar — intrekken bij deze klant | Meloen staat in kolom AO → cel **AO8** gewist |
| 2 | 2860, 2881, 2885, 2923, 3065, 3086, 3156, 3158, 3172, 2931, 2947, 3299, 3328 (alle meloen-bestellers) | Getroffen klanten verwittigen dat de meloen niet komt | Gefilterd op de meloen-bestellers, mailadressen uit **kolom G** in BCC in Thunderbird |
| 3 | zelfde lijst (alle meloen-bestellers) | Meloen bij álle bestellers intrekken (niet oogstbaar) | **AO8:AO147** selecteren, delete |

---

## Week 31 / 2026

*(genoteerd op 2026-07-31)*

### Gebeurtenis 1 — kerstomaatjes niet beschikbaar op vrijdag

**kerstomaatjes** waren als losse groente aangeboden, maar er zijn er
op **vrijdag** geen. Donderdag-klanten krijgen ze wél — de intrekking geldt dus
maar voor een **deel** van de bestellers, aangewezen via de dag-filter.

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 1 | alle kerstomaatjes-bestellers met klaarmaakdag **vrijdag** | Verwittigen dat de kerstomaatjes niet komen | Gefilterd op de kerstomaatjes-kolom (ingevuld), mailadressen uit **kolom G** in BCC — enkel vanaf de eerste vrijdag-rij |
| 2 | zelfde lijst | Kerstomaatjes intrekken bij die klanten (niet beschikbaar op vrijdag) | Met dezelfde selectie: cellen in de kerstomaatjes-kolom gewist |

Volgorde is bewust: **eerst mailen, dan wissen** — de selectie zelf ís de
adressenlijst, en na het wissen is ze niet meer te reconstrueren.

**DB-implicatie 1 — reikwijdte per segment, ook voor losse groenten.** Bij de
meloen (week 30) was de reikwijdte "iedereen die besteld had" en de adressering
een lijst `klant_id`'s. Hier is de reikwijdte een **segment** (leverdag =
vrijdag) × de bestellers van één groente. Dezelfde segment-dimensie die eerder
al voor pakketinhoud opdook (maat × dag × afhaalpunt) geldt dus óók voor losse
groenten. Segment = alleen de *adressering*; het **feit blijft per (klant, week,
groente)** — de DB moet het segment op het moment zelf uitklappen naar concrete
klanten, anders is er volgende week niets meer om op terug te grijpen (klanten
kunnen van dag wisselen).

**DB-implicatie 2 — de dag zit in de rij-VOLGORDE, niet in een filter.** (Klaas,
2026-07-31.) In de praktijk wordt er niet op een dag-kolom gefilterd: er wordt
gefilterd op de kerstomaatjes-kolom, en de vrijdag-grens wordt **op naam
herkend** — vrijdag staat onder donderdag. Twee gevolgen:

- *Semantisch klopt het.* De rijen staan gesorteerd op de query-kolom `leverdag`
  = `COALESCE(kwap.dag_klaarmaken, kap.dag_klaarmaken, b.leverdag)` (Module1
  ~915/1004) — dus op **klaarmaakdag mét weekkeuze-override**, precies de notie
  die een oogsttekort nodig heeft. De ambachtelijke methode pakt gratis het
  juiste segment. Voor de DB-vervanging ligt de segment-as daarmee vast:
  `dag_klaarmaken` (keuze-override eerst), niet afhaaldag.
- *Mechanisch is het fragiel.* De grens komt uit mensenkennis, niet uit data. Eén
  rij te hoog beginnen = een donderdag-klant verliest tomaatjes die er wél zijn
  én krijgt een mail; één rij te laag = een vrijdag-klant houdt tomaatjes die er
  niet zijn en hoort niets. Beide falen stil. Bovendien is de sortering
  **alfabetisch op de dagnaam** (donderdag < vrijdag): dat klopt vandaag toevallig,
  maar een derde dag ("dinsdag", "woensdag") zou de vertrouwde volgorde omgooien
  zonder dat er iets verandert aan het scherm.

De vervanging moet dus niet de handeling nabouwen maar het **criterium**
aanbieden — "groente × klaarmaakdag" — en de klantenlijst zelf afleiden. Dan
komen mail, intrekking en (later) het voorrang-tegoed alle drie uit één en
dezelfde, herhaalbare lijst.

**Nieuw soort gevolg — compensatie/voorrang (wens Klaas).** Idee: klanten die
een groente door een tekort misliepen, krijgen **volgende week voorrang** op
diezelfde groente. Dat is een echt nieuw stuk: de eerdere gevolgen (telling
corrigeren, mail sturen) leven binnen dezelfde week, dit **overleeft de week**.
Vorm: een tegoed/wachtrij per (klant, groente), aangemaakt door de intrekking en
afgeboekt zodra de klant de groente krijgt. Sluit aan bij de eerdere vaststelling
dat "wie bij tekort uitvalt" een menselijke verdeelbeslissing is: het systeem
beslist niet, het **rangschikt** — bij schaarste toont de cockpit/afweeglijst de
bestellers gesorteerd op wie het laatst iets misliep. Verwant aan de cadeaubon
(week 29) — ook een tegoed — maar in natura i.p.v. in euro's.

### Gebeurtenis 2 — eenmalige klant

Een **eenmalige klant**: één keer een groot pakket, geen abonnement.

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 3 | 3331 Carmen ("(honing)" als familienaam) | Eén keer een pakket afnemen, zonder abonnement | **Niets** — normaal had je hier een **rij ingevoegd** en genoeg velden ingevuld om mee te tellen in de aantallen. In plaats daarvan als **nieuwe klant in de DB** aangemaakt (type `weekperweek`, status `actief`). Nog te doen: haar terug stopzetten. |

**Dit is de omkering van alle vorige regels in deze log.** Alle eerdere gevallen
waren *intrekkingen* die je in het weekbestand deed en die de DB nooit bereikten;
dit is een *toevoeging* die je bewust **niet** in het weekbestand hebt gedaan,
juist omdat een met de hand ingevoegde rij de telling in het samenstelling-doc
niet haalt. De DB-route was hier al de betere — het handwerk heeft zichzelf
weg-geselecteerd. Waardevol als bevestiging: waar de DB het feit al kan dragen,
verdwijnt het weekbestand-handwerk vanzelf.

**Het gat: er is geen notie "eenmalige afname".** De enige manier om in de
telling te raken is een **volledige klantrelatie** aanmaken, die je daarna met de
hand weer moet afsluiten. Dat opruimwerk moet je onthouden, en niets herinnert je
eraan. Precies het onderscheid uit de hervorming relatie/levering
(`hervorming-relatie-levering.md`): haar **levering** regelt zichzelf al goed —
één bestelling, geen abonnement, dus volgende week staat ze nergens in het
weekbestand — maar haar **relatie** blijft openstaan, en die is de mail-poort. Het
"terug stoppen" gaat dus over precies één as, niet over leveringen. Een echt
eenmalig-concept zou die relatie nooit geopend hebben.

**Let op bij het stopzetten:** doe het via de gewone stop-invoer in
`klanten_beheer` (kolom R + doel in S), niet met een handmatige `UPDATE` op
`klanten.type` — dat veld wordt dagelijks door `flip_abonnementen()` herberekend
en je wijziging draait terug.

**Open punt (2026-08-02):** mag ze na het stopzetten nog aanbod-mails krijgen?
Nog niet beslist; ze staat voorlopig ongewijzigd. "Nee" = relatie helemaal
afsluiten, "ja" = het bestaande `weekperweek`-geval. Dat is de keuze die een
eenmalig-concept expliciet zou moeten stellen op het moment van aanmaken.

**Klein bijkomend gat: herkomst.** De familienaam is met de hand op "(honing)"
gezet om te markeren dat ze uit het honing-kanaal komt. De `klanten`-tabel doet
dus dienst als contactenlijst voor meerdere kanalen, met een pseudo-naam als
herkomst-markering. Er is geen herkomst-/kanaal-veld — relevant voor de
koffie/groenten-mailontkoppeling, waar de scheiding nu op `koffie_opt_out` leunt.

---

## Week 32 / 2026

*(genoteerd op 2026-08-05)*

### Gebeurtenis 1 — bestelling per e-mail, buiten het bestelformulier

**Yves Vandenheede (3097)** antwoordde op de aanbod-mail van ma 3 aug 11:10 met:
*"Graag een klein pak +2kg patat en 2kg ui aub."* Hij is `weekperweek`, `actief`,
afhaalpunt 't Voldersveld (klaarmaken donderdag, afhaling vrijdag) en bestelt
normaal gewoon via het formulier (laatst week 29). Deze week kwam de bestelling
per mail, ná het sluiten van het bestelvenster (ma 7u – di 13u15).

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 1 | 3097 Yves Vandenheede | Klein pakket + 2 kg aardappelen + 2 kg ui, per mail doorgegeven | **Rij met de hand toegevoegd** in `week_32_2026_definitief.ods` en genoeg velden ingevuld om mee te tellen (pakket-kolom + de losse-groentekolommen voor aardappelen en ui) |

**Dit is het eerste geval in deze log zónder modelgat.** Alle vorige regels wezen
op een notie die in de DB ontbreekt (cadeaubon = kortingsregel, tekort =
intrekking-met-reden, eenmalige klant = relatie zonder levering). Hier past het
feit exact in wat er al staat: één rij in `bestellingen` + twee in `bestelregels`,
met `klant_id = 3097`. Er valt niets te ontwerpen. Wat ontbreekt is enkel de
**deur**: het bestelformulier is klantgericht en verdwijnt na dinsdag 13u15, dus
er is geen manier om als beheerder een bestelling in te voeren. (Server-side zit
die grens er trouwens alleen op *wijzigen* — `postgres-proxy.php` ~1651; het
aanmaken van een bestelling heeft geen venstercontrole. Het is dus vooral een
UI-/toegangskwestie, geen nieuwe logica.)

**Wat de handmatige rij kost.** De afrekening werkt gewoon — die is een levende
formule over de cellen van het weekbestand. Wat wél wegvalt:

- **De telling.** De oogst- en afweeglijsten voor week 32 waren al gegenereerd
  (5 aug 7:56) toen de mail verwerkt werd; die tellen bovendien uit de DB. Zijn
  klein pakket en zijn 2 kg aardappelen + 2 kg ui staan dus nergens in de
  oogstcijfers — enkel in het hoofd van wie de rij toevoegde.
- **`groenten.besteld` / `aantal_beschikbaar`** worden niet bijgewerkt, terwijl
  elk van de 109 andere bestellingen van deze week dat wel deed.
- **De geschiedenis.** Volgend jaar is "wat bestelde Yves in week 32" leeg; hij
  ziet er in de data uit als een klant die sinds week 29 niets meer nam.
- **Geen bevestigingsmail** — hij weet niet of het gelukt is behalve via een
  handgeschreven antwoord.
- **De rij is vluchtig:** een nieuwe `MaakWeekbestand`-run overschrijft ze.

> **Correctie (2026-08-16):** "de afrekening werkt gewoon" klopt niet helemaal.
> Yves' handmatige rij (rij 100) heeft wél een spiegelrij op het
> afrekening-tabblad, maar zijn **kolom X (€ losse groenten) staat op 0,00 €**
> terwijl hij voor 11,50 € losse groenten bestelde. En in hetzelfde bestand
> missen **drie andere klanten** hun spiegelrij volledig (Iris Walgraeve 2950,
> Françoise Roussel 2931, Martijn Loosvelt Vandenbroucke 2932). Zie week 33
> hieronder voor het mechanisme.

**Bijkomend: de vertaalstap van vrije tekst naar catalogus.** "klein pak" →
`Klein pakket`; "2kg ui" → `Ui` (3,00 €/kg, stap 0,5); "2kg patat" → `Nieuwe
aardappelen` (2,75 €/kg) *of* `Nieuwe aardappelen kriel` (3,35 €/kg) — dat laatste
is een gok. Een invoerscherm dat het echte week-aanbod toont, haalt die gok eruit.

**Kleinste bouwstuk in heel deze log: "bestelling invoeren namens een klant".**
Dezelfde POST als het formulier, vanuit de portal/cockpit, met klantkiezer en het
aanbod van de week. Dat pensioneert deze soort volledig, en meteen ook het geval
"klant belt of mailt een *wijziging* na dinsdag 13u15" — dat kan vandaag helemaal
niet, want `bestelling_wijzigen` weigert buiten het venster. Sluit aan bij het
patroon van week 31 (Carmen): waar de DB het feit kan dragen, verdwijnt het
weekbestand-handwerk vanzelf.

---

<!--
Nieuwe week? Kopieer dit blok:

## Week __ / ____

| Wie (klant + klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|
|  |  |  |
-->
