# Hervorming: relatie en levering ontkoppelen

Status: **ontwerp v1** (2026-06-23). Te valideren met Klaas vóór implementatie.

## Aanleiding

Een gepauzeerde/gestopte klant (Annemie, 3220) werd tóch in de mailmerge
opgenomen, terwijl het weekbestand haar correct oversloeg. Oorzaak: de twee
selecties hanteren elk hun eigen definitie van "actieve klant deze week", en
de stop-flow (`VerwerkStopStart`, kolom R) schrijft de stop maar op één plek
(`annulaties.week_stopzetten_abonnement`) zonder `klanten.type/status` of
`abonnementen` bij te werken.

Ziektebeelden:
1. **Divergentie** tussen `MaakWeekbestand` en `BereidMailmergeVoor/Combi`.
2. **Versnipperde staat** over `klanten.type`, `klanten.status`,
   `abonnementen.status/pauze_vanaf`, `annulaties.week_stopzetten`.
3. **Jaar-gebonden guard** (`annulaties.jaar = iJaar`) → klant duikt in 2027
   opnieuw op.
4. **Geen doel-concept**: stop is binair; downgrade-naar-weekperweek en
   toekomst-planning passen er niet in. `klanten.type` drift weg van de realiteit.

## Het model: twee onafhankelijke assen

| As | Bron van waarheid | Bepaalt |
|---|---|---|
| **1. Relatie** (mail-poort) | klant-pauzewindow (zie schema) | Krijgt de klant de wekelijkse **aanbodsmail**? |
| **2. Levering** (pakket) | abonnement-window `[start, eind)` | Komt de klant **automatisch in het weekbestand** met voorgevuld pakket? |

`klanten.type` is geen invoer meer maar een **afgeleid label**, dagelijks door de
cron herberekend voor de huidige week:

| relatie | actief abonnement deze week | afgeleid `klanten.type` | aanbodsmail | auto-pakket |
|---|---|---|---|---|
| actief | ja (pare/onpare/wekelijks) | `abonnee[-pare/-onpare]` | ja — uitnodiging | ja |
| actief | nee | `weekperweek` | ja — uitnodiging-los | nee |
| gepauzeerd (window met einde) | — | `stop-tijdelijk` | nee | nee |
| gestopt (window zonder einde) | — | `stop-definitief` | nee | nee |

Kerninzichten:
- **weekperweek = "actieve klant zonder actief abonnement"** — valt vanzelf uit
  zodra een abonnement eindigt en de relatie actief blijft. Downgrade wordt triviaal.
- **`klanten.type` toont altijd correct** stop-definitief/stop-tijdelijk/weekperweek,
  want afgeleid → geen drift meer.
- **gepauzeerd ≠ weekperweek**: beide hebben geen actief abonnement, maar de
  pauzewindow zet de mail-poort dicht. Daarom zijn het twee aparte assen.

## Schema

### `klanten` — relatie-pauzewindow (mail-poort)
```sql
ALTER TABLE klanten ADD COLUMN IF NOT EXISTS pauze_vanaf_jaar smallint;
ALTER TABLE klanten ADD COLUMN IF NOT EXISTS pauze_vanaf_week smallint;
ALTER TABLE klanten ADD COLUMN IF NOT EXISTS pauze_tot_jaar   smallint;  -- NULL = definitief gestopt
ALTER TABLE klanten ADD COLUMN IF NOT EXISTS pauze_tot_week   smallint;
```
Afleiding voor week `N = jaar*100 + week`:
- pauze actief in week N  ⇔  `pauze_vanaf IS NOT NULL AND pauze_vanaf_N <= N AND (pauze_tot IS NULL OR N < pauze_tot_N)`
- `status` = `gestopt` als pauze actief en `pauze_tot IS NULL`; `gepauzeerd` als pauze actief en `pauze_tot` gezet; anders `actief`.

### `abonnementen` — levering-window
Bestaande kolommen `start_jaar/week` (incl.) en `eind_jaar/week` (excl., NULL = open)
worden DE bron. `status='toekomst'/'pauze'` en `pauze_vanaf_*` (migr. 05) worden
geretireerd — het window zegt alles:
- abonnement actief in week N  ⇔  `start_N <= N AND (eind IS NULL OR N < eind_N)`.

Migratie backfillt `eind` uit `annulaties.week_stopzetten_abonnement` en uit
`pauze_vanaf_*`. Datum-vergelijkingen overal als `jaar*100+week` — **nooit** `jaar = X`
(lost het 2027-risico op).

## Invoer: blad `klanten_stop_start` met aparte doel-kolom

Bestaande actiekolommen Q–V blijven; we voegen twee kolommen toe (header-gebaseerd
gedetecteerd, zoals `klant_id`):

| Kolom | Kop | Inhoud | Voorbeeld |
|---|---|---|---|
| R (17) | stopzetting | **vanaf-week** (abonnement stopt) | `W30` |
| **+** | **stop-doel** | `definitief` / `tijdelijk` / `weekperweek` (leeg = `definitief`) | `tijdelijk` |
| **+** | **herstart-week** | week (alleen bij `tijdelijk`) | `W40` |

Leeg doel = `definitief` → backward-compatibel met de huidige "R alleen = stop".
weekperweek-variant in Fase 1 = **elke week** (`weekperweek`); ritme-behoud
(`weekperweek-pare/-onpare`) is een latere verfijning die de pariteit moet opslaan.

## Wat `VerwerkStopStart` per doel schrijft

Gegeven klant K, huidig primair abonnement A0 (ritme R0, formaat F0), vanaf-week
W, herstart-week H:

| doel | abonnementen | klanten-pauzewindow |
|---|---|---|
| **definitief** | A0.eind = W | pauze_vanaf = W, pauze_tot = NULL |
| **tijdelijk** | A0.eind = W + nieuw A1 (R0/F0) start = H, eind = NULL | pauze_vanaf = W, pauze_tot = H |
| **weekperweek** | A0.eind = W | géén pauzewindow (blijft actief) |

"Meteen" = W = huidige week; "in de toekomst" = W later. De windows encoderen
beide; geen aparte toekomst-status nodig. De stop-tak schrijft géén
`annulaties.week_stopzetten_abonnement` meer (vervangen door A0.eind).

## Cron (vervangt de flip-cron-logica)

`kiemkracht-flip-abonnement.sh` wordt één **herbereken-stap** voor de huidige week N:
- `klanten.status` ← afgeleid uit de pauzewindow;
- `klanten.type` ← afgeleid uit (status + actief abonnement bij N + ritme).

Dit subsumeert alles wat de cron nu apart doet:
- toekomst→actief (abonnement-window wordt vanzelf actief bij N);
- hervat na pauze (N ≥ pauze_tot → status actief, A1 actief → type abonnee);
- stop toegepast (N ≥ pauze_vanaf → gestopt/gepauzeerd).

De cron wordt dus **eenvoudiger**, niet complexer.

## Consumenten (Fase 1: windowcondities; Fase 2: gedeelde view)

**Weekbestand** (abonnement-tak): vervang `status='actief' + ritme + pauze-guard +
week_stopzetten-guard` door het window:
```sql
(a.start_jaar*100 + a.start_week) <= :N
AND (a.eind_jaar IS NULL OR (a.eind_jaar*100 + a.eind_week) > :N)
AND a.ritme IN (:parRitmes)
```
(de losse `week_annulatie`-guard blijft).

**Mailmerge** (kandidaat-poort): vervang `k.status NOT IN ('gepauzeerd','gestopt')` door
de pauzewindow:
```sql
NOT (k.pauze_vanaf_jaar IS NOT NULL
     AND (k.pauze_vanaf_jaar*100 + k.pauze_vanaf_week) <= :N
     AND (k.pauze_tot_jaar IS NULL OR (k.pauze_tot_jaar*100 + k.pauze_tot_week) > :N))
```
Mailtype/formaat daarna uit "actief abonnement bij N?" (window) + pariteit; anders
`uitnodiging-los`. De per-type If-ladder in `BereidMailmergeVoor` collapst hierdoor.

## Fasering

- **Fase 0 — nu (uren):** annulaties-guard als vangnet in `BereidMailmergeVoor` +
  `BereidCombiMailmergeVoor` + sync. Stopt de actuele bloeding, onafhankelijk.
- **Fase 1 — dagen:** dit model. Schema-migratie, doel-bewuste invoer + stop-tak,
  windowcondities in beide consumenten, cron-herbereken. Levert stop-definitief,
  stop-tijdelijk-met-herstart én weekperweek-downgrade, jaar-veilig.
- **Fase 2 — met cockpit:** gedeelde DB-view/functie `klant_in_week(jaar, week)` die
  weekbestand, mailmerge én cockpit identiek lezen; de gedupliceerde windowlogica
  eruit factoreren. Sluit aan op de weekcockpit-beslissing ("één bron, twee UI's").

## Open punten

1. weekperweek-variant na downgrade: Fase 1 = elke week; ritme-behoud later.
2. Migratie-backfill van bestaande stop-/pauzeklanten (3279 definitief, 3220 tijdelijk)
   doet Klaas zelf zodra het model staat.
3. Fase 2: view/functie in DB vs gedeelde Basic-helper.

## Fase 1 — as-built (2026-06-25)

Geïmplementeerd en op dev getest (transacties met ROLLBACK: definitief/tijdelijk/
downgrade + recompute, allemaal groen). Migratie 06 op **dev én prod** (additief,
gedragsneutraal — de macro-library is gedeeld, dus de mailmerge verwijst meteen ook
op prod naar de nieuwe kolommen).

**Invoer = aparte kolommen** (niet de `R:H`-syntax uit het eerste ontwerp). In
`klanten_stop_start`, header-gedetecteerd op naam (rijen 1–6):
- `stop-doel`  → `definitief` (of leeg) / `tijdelijk` / `weekperweek`
- `herstart-week` → weeknr; verplicht bij `tijdelijk`, optioneel bij `weekperweek`
  (klant wordt dan in die week weer volwaardig abonnee)

Layout verschoof: R=stopzetting, **S=stop-doel, T=herstart-week**, U=vooruitbestellingen,
V=start, W=type, X=formaat (vaste indices `COL_VB..COL_FORMAAT` +2 in `VerwerkStopStart`).

**Wat de stop-tak schrijft** (per doel, op week W; herstart H):
| doel | abonnementen | klanten |
|---|---|---|
| definitief | `eind=(W)` op lopende primair-abo's | `pauze_vanaf=W, pauze_tot=NULL` |
| tijdelijk | `eind=(W)` + opvolger `start=(H)` (ritme/formaat gekopieerd) | `pauze_vanaf=W, pauze_tot=H` |
| weekperweek | `eind=(W)` (+ opvolger `start=(H)` als herstart-week gegeven) | geen pauzewindow |

`weekperweek` mét herstart-week = krijgt aanbod-los in `[W, H)` en wordt abonnee vanaf
`H`; verschilt van `tijdelijk` enkel doordat de mail-poort openblijft (geen pauzewindow).

**Belangrijke as-built nuances:**
- **NULL-veilig**: bestaande abo's hebben vaak `start=NULL` → conditie is
  `(start IS NULL OR start_N <= N)`. Idem `eind IS NULL` = open.
- **Selectie hervat zonder cron**: weekbestand én mailmerge lezen de windows
  rechtstreeks; bij week ≥ herstart valt de uitsluiting vanzelf weg en wordt de
  opvolger actief. De cron is dus enkel nodig voor (a) `klanten.type`/`status` als
  **weergave** in klanten_beheer en (b) het opruimen van een afgelopen pauzewindow.
- **Cron-recompute** (live in `/root/kiemkracht-flip-abonnement.sh`, dagelijks 6u,
  prod+dev): leidt `klanten.status`/`type` af + ruimt afgelopen pauzewindows op.
  Gescoped: niet `on_hold`, niet `-toekomst` (flip-cron-territorium), enkel klanten
  met een abonnement of een gestopt/gepauzeerd-status; legacy weekperweek-pariteit
  blijft. Raakt alleen écht gewijzigde rijen aan (`IS DISTINCT FROM`). Dry-run op prod
  én dev gaf 0 wijzigingen op de huidige data; end-to-end testrun = overal `UPDATE 0`.
  Backup van het oude script: `kiemkracht-flip-abonnement.sh.bak-20260625`.
- Fase 0-annulaties-guard blijft als vangnet tot de oude stops gebackfilld zijn.

## Uitbreiding — tijdelijk zonder herstart-week + opvolging (2026-07-07)

`stop-doel = tijdelijk` mag nu ook **zonder** herstart-week: de klant krijgt een
open pauzewindow (`pauze_tot = NULL`) plus `klanten.opvolg_datum` = donderdag
van de stopweek **+ 2 maanden**. Migratie 16 (dev + prod) voegt
`opvolg_datum`/`opvolg_gemaild_op` toe en maakt `flip_abonnementen()`
opvolg-bewust: open window **mét** opvolgdatum ⇒ `gepauzeerd`/`stop-tijdelijk`
(intentie is tijdelijk), zonder ⇒ `gestopt`/`stop-definitief` zoals voorheen.

Het sein, twee kanalen:
- **Digest-mail** naar Klaas via `pauze-herinnering.php` (zelfde maandag-17u-cron
  als de herstart-herinnering; aparte mail, `opvolg_gemaild_op` = anti-herhaal).
- **Macro `ToonOpvolgingen`** (+ `StartToonOpvolgingen` in Standard/Module2):
  lijst van klanten met bereikte opvolgdatum, per klant af te vinken
  (= `opvolg_datum` leegmaken). Niet afgevinkt = blijft in de lijst.

Opvolging wordt automatisch gewist door: een definitieve stop, een tijdelijke
stop mét herstart-week, een abonnementsstart (kolom T/V), of un-stop via
klanten_beheer. De start-tak sluit sindsdien ook het pauzewindow van een
herstartende klant (`pauze_tot = startweek`, WHERE-guard op bestaand window) —
voorheen bleef dat window openstaan en flipte de cron de klant terug naar
gestopt. Expliciet `stop-definitief` via klanten_beheer wist nu einde +
opvolging (anders zet de opvolg-bewuste recompute de status terug op
gepauzeerd).

### Doel-bewuste stopbevestiging + registratie-rij (2026-07-07, later op de dag)

Casus klant 3197: tijdelijke stop met herstart-week (wk29→wk35) kreeg de
definitief-mail. Oorzaak: de macro gaf doel/herstart niet door aan de
mail-template. Fix door de hele keten:
- `VerstuurAnnulatieMail` stuurt nu `HerstartWeek`/`HerstartJaar` (+
  `MailBlijven`=1 bij doel weekperweek, `OpvolgenOk`=1 bij tijdelijk-open) mee;
  de proxy kiest de **pauze-variant** ("pauzeert vanaf week W; vanaf week H
  hervatten de leveringen automatisch") en bewaart de afscheidszin enkel voor
  een écht afscheid.
- **Registratie-rij in `annulaties` hersteld** (manco: stops waren onzichtbaar
  in het tabblad `annulaties` van kiemkracht-data.ods sinds de stop-tak geen
  `week_stopzetten` meer schreef). De stop-tak schrijft opnieuw één rij per
  stop, mét `week_stopzetten_abonnement` bij definitief/tijdelijk-open maar
  **NULL** bij weekperweek of herstart-week — het Fase-0-mailmerge-vangnet
  sluit een `week_stopzetten`-rij immers de rest van het jaar uit, en die
  klanten moeten later weer aanbodsmails krijgen. Zelfde reden: de
  formulier-stop-rij krijgt `week_stopzetten = NULL` bij `MailBlijven=1`.
  De windows blijven de bron van waarheid; de rij is registratie + vangnet.

### Herstart-week zichtbaar in `annulaties` (2026-07-10, migratie 17)

Casus klant 3197: `week_stopzetten_abonnement` staat bewust NULL bij een
afgesproken herstart (zie hierboven) — maar dat liet de herstart-week
volledig onzichtbaar in het tabblad `annulaties`: enkel `week_annulatie`
stond er, geen spoor van "hervat op week 35". Migratie 17 voegt
**`herstart_jaar`/`herstart_week`** toe aan `annulaties` — puur
documentair, geen enkele WHERE-guard leest ze (de bron van waarheid
blijft `klanten.pauze_tot_*`). `LaadAlleTabellen` pikt de kolommen
automatisch op (`SELECT *`, geen loader-wijziging nodig). De stop-tak in
`VerwerkStopStart` vult ze bij elke stop met `hW > 0` (tijdelijk of
weekperweek + herstart-week). Backfill op prod voor de twee bestaande
gevallen (3197 wk35, Annemie/3220 wk40).
