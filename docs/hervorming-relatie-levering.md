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
- `herstart-week` → weeknr, enkel bij `tijdelijk`

Layout verschoof: R=stopzetting, **S=stop-doel, T=herstart-week**, U=vooruitbestellingen,
V=start, W=type, X=formaat (vaste indices `COL_VB..COL_FORMAAT` +2 in `VerwerkStopStart`).

**Wat de stop-tak schrijft** (per doel, op week W; herstart H):
| doel | abonnementen | klanten |
|---|---|---|
| definitief | `eind=(W)` op lopende primair-abo's | `pauze_vanaf=W, pauze_tot=NULL` |
| tijdelijk | `eind=(W)` + opvolger `start=(H)` (ritme/formaat gekopieerd) | `pauze_vanaf=W, pauze_tot=H` |
| weekperweek | `eind=(W)` | geen pauzewindow |

**Belangrijke as-built nuances:**
- **NULL-veilig**: bestaande abo's hebben vaak `start=NULL` → conditie is
  `(start IS NULL OR start_N <= N)`. Idem `eind IS NULL` = open.
- **Selectie hervat zonder cron**: weekbestand én mailmerge lezen de windows
  rechtstreeks; bij week ≥ herstart valt de uitsluiting vanzelf weg en wordt de
  opvolger actief. De cron is dus enkel nodig voor (a) `klanten.type`/`status` als
  **weergave** in klanten_beheer en (b) het opruimen van een afgelopen pauzewindow.
- **Cron-recompute nog niet aangezet** (enige niet-additieve mutatie op prod):
  gescoped op klanten met een abonnement of pauzewindow, `on_hold` uitgesloten,
  legacy weekperweek-pariteit blijft. Toe te voegen aan `kiemkracht-flip-abonnement.sh`
  na een dry-run op prod.
- Fase 0-annulaties-guard blijft als vangnet tot de oude stops gebackfilld zijn.
