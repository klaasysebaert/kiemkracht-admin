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
