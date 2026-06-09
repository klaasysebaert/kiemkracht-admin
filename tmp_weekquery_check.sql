WITH vb_week AS (
  SELECT klant_id, LOWER(klant_email) AS email_l,
    CASE LOWER(TRIM(REPLACE(formaat, ' pakket', '')))
      WHEN 'klein'       THEN 'klein'
      WHEN 'groot'       THEN 'groot'
      WHEN 'extra groot' THEN 'extra-groot'
      WHEN 'extra-groot' THEN 'extra-groot'
      WHEN 'mini'        THEN 'mini'
    END AS sleutel
  FROM vooruitbestellingen
  WHERE jaar = 2026 AND week_bestelling = 24
    AND formaat IS NOT NULL
),
res AS (
SELECT b.id,
COALESCE(NULLIF(k.voornaam,''), b.voornaam) AS voornaam,
COALESCE(NULLIF(k.familienaam,''), b.familienaam) AS familienaam,
b.klant_email,
COALESCE(kap.naam, b.afhaalpunt) AS afhaalpunt,
COALESCE(kap.dag_klaarmaken, b.leverdag) AS leverdag,
b.pakket, b.pakket_inhoud,
b.abonnement_wijziging, b.vragen_opmerkingen,
COALESCE(k.klant_type,'') AS klant_type,
COALESCE(k.formaat,'') AS formaat,
COALESCE(k.telefoon,'') AS telefoon,
COALESCE(k.id::text,'') AS klant_id,
COALESCE(k.type,'') AS type,
COALESCE(kap.dag_klaarmaken, bap.dag_klaarmaken,'') AS dag_klaarmaken,
COALESCE(kap.id_intern, bap.id_intern, 9999) AS id_intern_sort,
COALESCE(k.id, 999999) AS klant_id_sort
FROM bestellingen b
LEFT JOIN klanten k ON (k.id = b.klant_id OR (b.klant_id IS NULL AND k.email1 = b.klant_email))
LEFT JOIN afhaalpunten kap ON kap.id = k.afhaalpunt_id
LEFT JOIN afhaalpunten bap ON bap.naam = b.afhaalpunt
WHERE b.weeknummer = 24 AND b.jaar = 2026
 AND NOT EXISTS (SELECT 1 FROM annulaties a
   WHERE a.jaar = 2026 AND a.week_annulatie = 24
     AND (a.klant_id = b.klant_id OR (b.klant_id IS NULL AND LOWER(a.klant_email) = LOWER(b.klant_email))))
 UNION ALL
SELECT 0, k.voornaam, k.familienaam, k.email1,
COALESCE(ap.naam,''), COALESCE(ap.dag_klaarmaken,''),
CASE COALESCE(vb.sleutel, k.formaat)
  WHEN 'klein'       THEN 'klein pakket'
  WHEN 'groot'       THEN 'groot pakket'
  WHEN 'extra-groot' THEN 'extra groot pakket'
  WHEN 'mini'        THEN 'mini pakket' ELSE '' END,
'', '', '',
COALESCE(k.klant_type,''), COALESCE(vb.sleutel, k.formaat), COALESCE(k.telefoon,''), COALESCE(k.id::text,''),
COALESCE(k.type,''),
COALESCE(ap.dag_klaarmaken,''),
COALESCE(ap.id_intern, 9999),
COALESCE(k.id, 999999)
FROM klanten k
LEFT JOIN afhaalpunten ap ON ap.id = k.afhaalpunt_id
LEFT JOIN vb_week vb ON (vb.klant_id = k.id OR (vb.klant_id IS NULL AND vb.email_l = LOWER(k.email1)))
WHERE k.type IN ('abonnee', 'abonnee-pare-week')
 AND NOT EXISTS (SELECT 1 FROM bestellingen bx
   WHERE bx.weeknummer = 24 AND bx.jaar = 2026
     AND (bx.klant_id = k.id OR (bx.klant_id IS NULL AND LOWER(bx.klant_email) = LOWER(k.email1))))
 AND NOT EXISTS (SELECT 1 FROM annulaties a
   WHERE a.jaar = 2026 AND a.week_annulatie = 24
     AND (a.klant_id = k.id OR (a.klant_id IS NULL AND LOWER(a.klant_email) = LOWER(k.email1))))
 AND NOT EXISTS (SELECT 1 FROM annulaties ann
   WHERE ann.jaar = 2026
     AND ann.week_stopzetten_abonnement > 0 AND ann.week_stopzetten_abonnement <= 24
     AND (ann.klant_id = k.id OR (ann.klant_id IS NULL AND LOWER(ann.klant_email) = LOWER(k.email1))))
 UNION ALL
SELECT 0, k.voornaam, k.familienaam, k.email1,
COALESCE(ap.naam,''), COALESCE(ap.dag_klaarmaken,''),
CASE vb.sleutel
  WHEN 'klein'       THEN 'klein pakket'
  WHEN 'groot'       THEN 'groot pakket'
  WHEN 'extra-groot' THEN 'extra groot pakket'
  WHEN 'mini'        THEN 'mini pakket' ELSE '' END,
'', '', '',
COALESCE(k.klant_type,''), vb.sleutel, COALESCE(k.telefoon,''), COALESCE(k.id::text,''),
COALESCE(k.type,''),
COALESCE(ap.dag_klaarmaken,''),
COALESCE(ap.id_intern, 9999),
COALESCE(k.id, 999999)
FROM klanten k
LEFT JOIN afhaalpunten ap ON ap.id = k.afhaalpunt_id
INNER JOIN vb_week vb ON (vb.klant_id = k.id OR (vb.klant_id IS NULL AND vb.email_l = LOWER(k.email1)))
WHERE k.type IN ('weekperweek','weekperweek-pare-week','weekperweek-onpare-week','abonnee-toekomst','abonnee-pare-week-toekomst','abonnee-onpare-week-toekomst','abonnee-onpare-week')
 AND NOT EXISTS (SELECT 1 FROM bestellingen bx
   WHERE bx.weeknummer = 24 AND bx.jaar = 2026
     AND (bx.klant_id = k.id OR (bx.klant_id IS NULL AND LOWER(bx.klant_email) = LOWER(k.email1))))
 AND NOT EXISTS (SELECT 1 FROM annulaties a
   WHERE a.jaar = 2026 AND a.week_annulatie = 24
     AND (a.klant_id = k.id OR (a.klant_id IS NULL AND LOWER(a.klant_email) = LOWER(k.email1))))
 AND vb.sleutel IS NOT NULL
)
SELECT 'rijen totaal' AS metric, count(*)::text AS waarde FROM res
UNION ALL
SELECT 'distinct klant_id (niet-leeg)', count(DISTINCT klant_id)::text FROM res WHERE klant_id <> ''
UNION ALL
SELECT 'rijen met leeg klant_id', count(*)::text FROM res WHERE klant_id = ''
UNION ALL
SELECT 'DUBBELE klant_id', COALESCE(string_agg(klant_id || ' (x' || c || ')', ', '), '(geen)')
FROM (SELECT klant_id, count(*) c FROM res WHERE klant_id <> '' GROUP BY klant_id HAVING count(*) > 1) d;
