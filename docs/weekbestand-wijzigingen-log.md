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

## Week 33 / 2026

*(genoteerd op 2026-08-16, tijdens het afwerken van `week_33_2026_definitief.ods`)*

### Gebeurtenis 1 — nieuwe klant, bestelling retroactief ingevoerd

Een nieuwe klant meldde zich ná het bestelvenster. Ze is eerst **in de database
aangemaakt** (`klanten` id **3333**, Annemie Vanhee, type `abonnee`, status
`actief`, afhaalpunt 't Hoge) en haar bestelling is daarna **met de hand in het
weekbestand** gezet — mét haar `klant_id` in kolom P, zodat de koppeling met de
afrekening/maandbestand op identiteit blijft werken.

| # | Wie (klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|---|
| 1 | 3333 Annemie Vanhee ('t Hoge) | Als nieuwe klant deze week al meedraaien | Klant aangemaakt in de DB; **rij met de hand toegevoegd** in het 't Hoge-blok, incl. **klant_id 3333 in kolom P** |
| 2 | zelfde | Een groente die **niet op het formulier stond** toch afnemen | `VoegLosseGroenteToe` (macro) uitgevoerd → eerste vrije slot **AU**, naam + prijs + eenheid; daarna haar hoeveelheid ingevuld |

Dit is de omgekeerde volgorde van week 31 (Carmen): daar bleef het weekbestand
leeg omdat de DB het feit al droeg, hier draagt de **DB alleen de klant** en niet
de bestelling — er staat voor 3333 geen enkele rij in `bestellingen`. Zelfde
ontbrekende deur als bij Yves (week 32): *bestelling invoeren namens een klant*.
Het klant_id in kolom P is hier het redmiddel: zonder dat veld zou de afrekening
haar op naam moeten matchen.

De macro-route voor de extra groente werkt zoals bedoeld: naam in rij 2, prijs in
rij 3 en de eenheid-metadata in `Blad2` (kolom I + rij 100), waardoor afrekening,
samenvattingskolom en overzichten meelopen. Maar de groente bestaat **alleen in
dit bestand**: niet in `groenten`, niet in het aanbod van de week, dus ook niet in
de oogst-/afweeglijsten en niet in de geschiedenis.

### Gebeurtenis 2 — het tweede tabblad groeit NIET mee (structureel)

**Vaststelling bij het invoegen:** het tweede tabblad (`afrekening`) evolueert niet
mee met een met de hand toegevoegde rij. Dat is geen detail — het is stil, en het
gebeurt al weken.

**Mechanisme.** `MaakWeekbestand` bouwt de afrekening als een **spiegel op
rijnummer**: afrekening-rij *N* bevat formules die naar datablad-rij *N* wijzen
(plus `nExtra = 10` lege reserve-rijen onderaan, precies voor een handmatige
klant). Voeg je in het datablad een rij **tussenin** in, dan schuiven de
verwijzingen van alle onderliggende afrekening-rijen netjes één op — maar er komt
**geen nieuwe afrekening-rij bij**. De ingevoegde klant heeft dus nergens een
spiegel. Een rij **onderaan bijzetten** werkt wél (dat is waar die 10 reserve-rijen
voor dienen). Precies dat verschil verklaart waarom het soms lijkt te lukken.

Twee gevolgen, allebei zonder foutmelding:

1. **Kolom X (€ losse groenten) op het datablad is een formule naar
   `afrekening.C<zelfde rij>`.** Bij een verschoven spiegel wijst die naar de
   losse-groentenwaarde van de **buurklant**. In week 33 stond kolom X daardoor
   bij 6 klanten fout, en het weektotaal X4 **203,92 € te laag** (1.365,80 €
   getoond t.o.v. 1.569,72 € werkelijk besteld).
2. **`MaakMaandbestand` valt terug op het rijnummer.** De maandafrekening zoekt de
   afrekening-rij op `klant_id` (kolom F) en anders op naam — vindt ze geen van
   beide, dan neemt ze **dezelfde rijnummer**, dus de rij van een andere klant
   (Module2 ~1786). Pakketbedrag en weglatingen komen dan van die andere klant.

**Toestand week 33 op 2026-08-16** (nagekeken in het opgeslagen bestand, vóór de
rij van 3333): 142 klantrijen in het datablad, **136 spiegelrijen** in de
afrekening. Zonder spiegelrij:

| datablad | klant | klant_id | gevolg als de maandafrekening nu gemaakt wordt |
|---|---|---|---|
| 18 | Nelly Beddeleem | 3167 | € losse toont 0,00 € i.p.v. **171,25 €** (8 × tomaten voor directe verwerking); geen pakket, dus geen fout pakketbedrag |
| 51 | Sara Verhoest | 3323 | mini-pakket wordt aangerekend aan **16,60 €** i.p.v. 13,30 €; haar weglating *kropsla* valt weg |
| 151 | Lieve Borremans | 3232 | weglatingen *tomaten* + *courgette* vallen weg |
| 183 | Françoise Roussel | 2931 | klein pakket wordt aangerekend aan **13,30 €** i.p.v. 16,60 € |
| 184 | Stina Braem | 2937 | krijgt **2,15 €** korting die niet van haar is (weglating van de buurrij) |
| 185 | Lukas Ameye | 3224 | bedrag valt toevallig gelijk |

Daarbovenop: **Ann Maelfait (3228) staat twéé keer** in de afrekening (rijen 166 en
168), en er staat een `#VERW!`-weesrij van een verwijderde klantrij. Beide
vervuilen H4 (weglatingen-totaal) en dus het WEEKTOTAAL (H5 = 3.239,97 €).

Het is niet tot week 33 beperkt — dezelfde controle over de vorige weken:

| week | klantrijen | zonder spiegelrij | dubbel |
|---|---|---|---|
| 31 | 142 | 0 | 2893, 2934 |
| 32 | 134 | 3 (2950, 2931, 2932) | 2929 (6×) |
| 33 | 142 | 6 (zie tabel) | 3228 |

**DB-implicatie — dit is geen ontbrekend concept, maar een ontbrekende
integriteitscontrole.** Alle vorige regels in deze log wezen op een *notie* die de
DB mist (kortingsregel, intrekking-met-reden, eenmalige afname). Hier is het
model in orde: één rij per (klant, week) met bedragen. Wat de spreadsheet mist is
wat een DB gratis geeft — **de garantie dat elke klantrij precies één
afrekeningsrij heeft**. De koppeling is hier een rijnummer, en rijnummers
overleven handwerk niet. In de DB-wereld is de afrekening geen tweede tabblad maar
een **afgeleide van dezelfde bestelregels**: dan kan ze per definitie niet
verschuiven, en verdwijnt deze hele foutsoort mee.

**Zolang het weekbestand bestaat, is er een controle nodig** die na het handwerk
zegt: "deze klant_id's uit het datablad hebben geen rij in de afrekening" +
"deze klant_id's staan er dubbel" + "kolom X wijkt af van de zelf berekende
losse-waarde". Dat is een kwartier macro-werk en het vangt precies wat vandaag
stil misloopt. Alternatief (of aanvullend): `MaakMaandbestand` mag **niet stil
terugvallen op het rijnummer** — geen match op klant_id of naam moet een
zichtbare waarschuwing geven, niet het bedrag van de buurman.

#### Opgelost 2026-08-18 — `HerstelWeekbestandFormules` (Module1)

De diagnose hierboven bleek nog te mild: het is niet enkel dat een **ingevoegde**
rij geen spiegelrij krijgt. Bij het nakijken van `week_33_2026_definitief.ods`
(na het verzetten/wissen/toevoegen van klanten, laatst Annemie Vanhee 3333) liep
de spiegel over **acht aparte zones** uit de pas — LibreOffice verschuift de
verwijzing mee met de **bron-cel**, niet met de rij, dus elke ingreep laat een
eigen offset achter:

| afrekening-rijen | offset naar het datablad |
|---|---|
| 7–17 | 0 (correct) |
| 18–43 | +1 |
| 44–45 | 0, met `#VERW!` |
| 46–51 | −1, met `#VERW!` |
| 52–135 | 0 (correct) |
| 136 | volledig `#VERW!` (verwijderde rij) |
| 137–151 | −1 |
| 152–169 | +2, met uitschieters −14/−16 en `#VERW!` |
| 170–181 | +1 |
| 182–202 | +4 |

Het gaat **beide richtingen** uit: ook datablad-kolom X (`=afrekening.C<rij>`)
wees op 60 rijen naar de buurklant, en kolom W verloor op 6 rijen zijn
`Blad2.I`-eenheidsverwijzingen. Gevolg voor week 33: 6 klanten zonder eigen
afrekeningsrij, 3228 dubbel, WEEKTOTAAL 3.247,57 € i.p.v. 3.457,90 €
(bijbestellingen 1.373,40 → 1.593,29; weglatingen 193,33 → 202,89).

**De controle uit de vorige alinea is niet gebouwd — er is iets beters gekomen:
een herstel.** Een controle zegt alleen *dát* het misloopt; `HerstelWeekbestandFormules`
herschrijft het contract "afrekening-rij N = datablad-rij N" gewoon vanaf nul,
voor de afrekening (A–F, W, Y–AV, AY, AZ–BK) én voor datablad-kolom W en X, wist
weesrijen onder de spiegel, en meldt achteraf de totalen + dubbele klant_id's.
Ze raakt geen enkele ingevulde waarde aan en is idempotent. Het herstelwerk zelf
zit in `HerstelFormulesKern(oDoc)` — dialoogvrij, zodat het headless te draaien
en te controleren is. Start-wrapper: `StartHerstelWeekbestandFormules`.

Week 33 is ermee hersteld en nagerekend: pakketten, bijbestellingen en
weglatingen komen alle drie exact overeen met een onafhankelijke herberekening
uit de ruwe datablad-cijfers, en er staat geen `#VERW!` meer in het bestand.

##### Week 31 en 32 mee hersteld (2026-08-18)

Beide `_definitief`-bestanden waren nóg zwaarder verschoven dan week 33 — week 32
liep op tot offset **−8** en had 187 `#VERW!`-cellen:

| | week 31 | week 32 | week 33 |
|---|---|---|---|
| `#VERW!`-cellen | 98 | 187 | 49 |
| offset-zones | 11 | 16 | 10 |
| slechtste offset | −7 | −8 | +4 |
| kolom X fout | 130 | 124 | ~60 |
| klant zonder afrekeningsrij | 0 | 3 | 6 |
| klant dubbel | 2 | 1 (6×) | 1 |
| WEEKTOTAAL vóór → na | 2.790,82 (gelijk) | 3.056,02 → 3.052,02 | 3.247,57 → 3.457,90 |

**Structurele schade ≠ geldschade.** Dat is de les van week 31: 98 `#VERW!`-cellen
en elf offset-zones, en tóch geen enkele klant met een ander bedrag. De reden is
dat `MaakMaandbestand` op **klant_id** koppelt en een verschoven afrekening-rij
intern *consistent* is — alle cellen van die rij wijzen naar dezelfde (verkeerde)
datarij, inclusief kolom F. Zolang elke klant ergens nog een rij mét zijn eigen
klant_id heeft, komt het juiste bedrag mee. Pas wanneer een rij helemaal
**wegvalt** (verschoven over een andere heen) valt de macro terug op het
rijnummer, en dán pas gaat er geld mis:

| week | klanten met ander bedrag | saldo | grootste afwijking |
|---|---|---|---|
| 31 | 0 | 0,00 € | — |
| 32 | 3 (2950, 2931, 2932) | −1,47 € | Martijn Loosvelt Vandenbroucke −6,32 € |
| 33 | 6 | +188,92 € | Nelly Beddeleem 16,60 € i.p.v. **171,25 €** |

Week 31 valt in de **juli**-afrekening, die al gemaakt en gemailmergd is
(`afrekening_juli_2026_definitief.ods`, `..._mailmerge.ods` van 2026-08-16) — die
blijft dus gewoon correct, er hoeft niets rechtgezet. Week 32 en 33 vallen in
**augustus**; die maandafrekening bestond nog niet, dus de correctie loopt vanzelf
mee bij de eerstvolgende `MaakMaandbestand`.

Alle drie de bestanden zijn na herstel nagerekend: pakketten, bijbestellingen en
weglatingen komen exact overeen met een onafhankelijke herberekening uit de ruwe
datablad-cijfers, en er staat nergens nog een `#VERW!`.

##### De poort in MaakMaandbestand (2026-08-18)

Bij het nakijken van de drie weken kwam de vraag boven of een controle op
klant_id wel volstaat. Het antwoord: **nee, en om een structurele reden.** Zo'n
controle vertrouwt precies de cel waarvan de uitlijning in vraag staat — kolom F
is zelf een formule met dezelfde kwetsbaarheid als de bedragen ernaast. Ze vangt
"klant heeft geen rij" en "klant staat dubbel", maar niet **"juist etiket, geld
van iemand anders"**, en dat is net het geval dat niemand ooit opmerkt.

Gemeten in de drie weekbestanden: 13 afrekening-rijen verwezen naar méér dan één
datablad-rij, telkens doordat de matrixformules in W en AY (die naar een BEREIK
verwijzen) `#VERW!` werden terwijl de losse-cel-verwijzingen gewoon meeschoven.
In geen van die rijen liep F uit de pas met B/E — maar dat is een uitkomst, geen
garantie: twee soorten verwijzing in dezelfde rij, met verschillend gedrag bij
dezelfde ingreep.

Daarom staat er nu een poort vooraan in `MaakMaandbestand`, meteen na
`calculateAll()` per weekbestand: `ControleerWeekSpiegel(oWeek)` (Module1,
dialoogvrij, geeft "" of een verslag). Ze controleert **twee dingen naast
elkaar**, omdat elk vangt wat het andere niet ziet:

1. **uitlijning** — staan op afrekening-rij r dezelfde naam én hetzelfde
   klant_id als op datablad-rij r?
2. **herrekening** — kloppen B (pakket), C (losse) en D (weglatingen) met wat je
   uit de ruwe datablad-cijfers berekent? Dit is de enige die "juist etiket,
   verkeerd geld" ziet.

Plus de dubbele-klant_id-scan. Niet in orde → één melding met de week, de
aantallen en zes voorbeeldrijen, en de macro stopt (doorgaan kan bewust; de
eindpopup vermeldt dan welke weken de controle negeerden).

**Discriminatieproef** (zelfde eis als `validate-macro.py`: een controle die niet
kan falen bewijst niets):

| bestand | uitkomst |
|---|---|
| week 31/32/33 vóór herstel | 129 / 124 / 75 foute koppelingen + dubbels gemeld |
| week 31/32/33 ná herstel | schoon |
| hersteld bestand, B/C/D gesaboteerd met een vast getal (naam + klant_id dus perfect) | 3 rijen aangewezen, met de juiste verwachte bedragen |

Die laatste rij is de belangrijkste: het is exact het geval waar een
klant_id-controle blind voor is.

**Wat dit niet oplost.** De macro herstelt de koppeling *achteraf* en de poort
meldt ze *vooraf*; samen beletten ze niet dat ze breekt. Zolang de afrekening een
tweede tabblad is dat op rijnummer koppelt, blijft dit handwerk-gevoelig — het
onderliggende punt hierboven (de afrekening als afgeleide van de bestelregels)
blijft dus staan. De stille terugval op rijnummer in `MaakMaandbestand` (~1786)
staat er ook nog; ze is nu wel onschadelijk zolang de poort ervóór staat, want
bij een uitgelijnd bestand is rij N per definitie de juiste rij.

---

<!--
Nieuwe week? Kopieer dit blok:

## Week __ / ____

| Wie (klant + klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|
|  |  |  |
-->
