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

<!--
Nieuwe week? Kopieer dit blok:

## Week __ / ____

| Wie (klant + klant_id) | Wat de klant/situatie wou | Wat je in het weekbestand deed |
|---|---|---|
|  |  |  |
-->
